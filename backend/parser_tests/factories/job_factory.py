import uuid

import factory

from app.job.models.job import Job


class JobFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Job
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    title = factory.Faker("job")
    department = "Engineering"
    employment_type = "full_time"
    location = "Remote"
    status = "open"
    tags = ["urgent"]
    hiring_team = {}
    custom_fields = {}
