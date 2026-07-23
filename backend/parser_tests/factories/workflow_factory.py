import uuid

import factory

from app.workflow.models.workflow import (Pipeline, PipelineStage,
                                          WorkflowInstance)

from .candidate_factory import CandidateFactory
from .job_factory import JobFactory


class PipelineFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Pipeline
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = "Standard Pipeline"
    is_template = True
    job_id = None


class PipelineStageFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PipelineStage
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    pipeline = factory.SubFactory(PipelineFactory)
    name = "Applied"
    order = 1
    requires_approval = False
    is_terminal = False


class WorkflowInstanceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = WorkflowInstance
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    job_id = factory.LazyAttribute(lambda o: JobFactory().id)
    candidate_id = factory.LazyAttribute(lambda o: CandidateFactory().id)
    pipeline_id = factory.LazyAttribute(lambda o: PipelineFactory().id)
    status = "active"
