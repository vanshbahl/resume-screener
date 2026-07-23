import uuid

import factory

from app.candidate.models.candidate import Candidate


class CandidateFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Candidate
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    status = "applied"
    tags = ["python", "senior"]
    custom_fields = {"first_name": "Test", "last_name": "Candidate"}
