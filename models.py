from datetime import datetime
from optparse import Option
from turtle import back
from typing import List
from typing import Optional
from pandas import Timestamp
from sqlalchemy import ForeignKey, true
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
    pextID: Mapped[Optional[str]]
    firstNAME: Mapped[str]
    middleNAME: Mapped[Optional[str]]
    lastNAME: Mapped[str]
    email: Mapped[str]
    pcreationDT: Mapped[Timestamp]

    accounts: Mapped[List["Account"]] = relationship(back_populates="person")

    def __repr__(self) -> str:
        return f"Person(pID={self.pID!r}, pextID={self.pextID!r}, firstNAME={self.firstNAME!r}, middleNAME={self.firstNAME!r}, lastNAME{self.lastNAME!r}, email={self.email!r}, pcreationDT={self.pcreationDT!r}"

class Account(Base):
    __tablename__ = "account"

    aID: Mapped[int] = mapped_column(primary_key=true)
    aextID: Mapped[Optional[str]]
    bnetNAME: Mapped[str]
    personID: Mapped[int] = mapped_column(ForeignKey("person.pID"))

    person: Mapped[List["Person"]] = relationship(back_populates="accounts")

    def __repr__(self) -> str:
        return f"Account(aID={self.aID!r}, aextID={self.aextID!r}, bnetNAME={self.bnetNAME!r}, personID={self.personID!r})"
