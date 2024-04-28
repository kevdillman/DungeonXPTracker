from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

print("models imported.")

class Base(DeclarativeBase):
    pass

class Person(Base):
    __tablename__ = "person"

    pID: Mapped[int] = mapped_column(primary_key=True)
