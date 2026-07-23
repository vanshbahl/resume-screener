

def test_create_pipeline(client, db_session):
    from parser_tests.factories.job_factory import JobFactory

    job = JobFactory.build()
    db_session.add(job)
    db_session.commit()
    response = client.post(
        f"/workflows/pipelines?template_name=standard&job_id={job.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Standard Engineering Pipeline (Customized)"
    assert len(data["stages"]) == 6
    return data["id"], data["stages"][0]["id"], data["stages"][1]["id"]


def test_start_workflow(client, db_session):
    from parser_tests.factories.candidate_factory import CandidateFactory

    candidate = CandidateFactory.build()
    db_session.add(candidate)
    db_session.commit()

    pipeline_id, first_stage, next_stage = test_create_pipeline(client, db_session)
    # The pipeline created a job, we can fetch it via pipeline
    from app.workflow.models.workflow import Pipeline

    job_id = (
        db_session.query(Pipeline).filter(Pipeline.id == pipeline_id).first().job_id
    )

    response = client.post(
        "/workflows/",
        json={
            "job_id": job_id,
            "candidate_id": candidate.id,
            "pipeline_id": pipeline_id,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["current_stage_id"] == first_stage

    # Check timeline for workflow start
    timeline_res = client.get(f"/workflows/{data['id']}/timeline")
    assert timeline_res.status_code == 200
    assert any(t["event_type"] == "workflow_started" for t in timeline_res.json())

    return data["id"], next_stage


def test_transition_workflow(client, db_session):
    workflow_id, next_stage = test_start_workflow(client, db_session)

    # Transition to the next stage
    response = client.post(
        f"/workflows/{workflow_id}/transition",
        json={
            "target_stage_id": next_stage,
            "action": "forward",
            "reason": "Resume looks great",
            "user_id": "recruiter-1",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_stage_id"] == next_stage

    # Check timeline for transition
    timeline_res = client.get(f"/workflows/{workflow_id}/timeline")
    assert any(
        t["event_type"] == "transitioned" and t["details"]["new_stage_id"] == next_stage
        for t in timeline_res.json()
    )


def test_assign_user(client, db_session):
    workflow_id, _ = test_start_workflow(client, db_session)

    response = client.post(
        f"/workflows/{workflow_id}/assign",
        json={"user_id": "interviewer-1", "role": "technical_interviewer"},
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == "interviewer-1"


def test_approve_stage(client, db_session):
    workflow_id, _ = test_start_workflow(client, db_session)

    response = client.post(
        f"/workflows/{workflow_id}/approve",
        json={
            "status": "approved",
            "reason": "Meets criteria",
            "approver_id": "manager-1",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
