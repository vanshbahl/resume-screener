import sys
sys.path.append('.')
from app.core.database import Base
import app.models.domain
print("Tables in Base.metadata:")
for t in Base.metadata.tables.keys():
    print(f" - {t}")
