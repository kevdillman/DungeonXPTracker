import datetime
from optparse import Option
from turtle import back
from typing import List
from typing import Optional
from pandas import Timestamp
from sqlalchemy import ForeignKey, BIGINT, TIMESTAMP, NVARCHAR, func
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

print("models imported.")

class Base(DeclarativeBase):
    type_annotation_map = {
        int: BIGINT,
        datetime.datetime: TIMESTAMP(timezone=True),
        str: String().with_variant(NVARCHAR, "mssql"),
    }

class Person(Base):
    __tablename__ = "person"

    pID: Mapped[int] = mapped_column(primary_key=True)
    pextID: Mapped[Optional[str]]
    firstNAME: Mapped[str]
    middleNAME: Mapped[Optional[str]]
    lastNAME: Mapped[str]
    email: Mapped[str]
    pcreationDT: Mapped[datetime.datetime] = mapped_column(server_default = func.CURRENT_TIMESTAMP())

    accounts: Mapped[List["Account"]] = relationship(back_populates="person")

    def __repr__(self) -> str:
        return f"Person(pID={self.pID!r}, pextID={self.pextID!r}, firstNAME={self.firstNAME!r}, middleNAME={self.firstNAME!r}, lastNAME{self.lastNAME!r}, email={self.email!r}, pcreationDT={self.pcreationDT!r}"
    
class Account(Base):
    __tablename__ = "account"

    aID: Mapped[int] = mapped_column(primary_key=True)
    aextID: Mapped[Optional[str]]
    bnetNAME: Mapped[str]
    personID: Mapped[int] = mapped_column(ForeignKey("person.pID"))

    person: Mapped["Person"] = relationship(back_populates="accounts")
    characters: Mapped[List["Character"]] = relationship(back_populates="account")

    def __repr__(self) -> str:
        return f"Account(aID={self.aID!r}, aextID={self.aextID!r}, bnetNAME={self.bnetNAME!r}, personID={self.personID!r})"

class Character(Base):
    __tablename__ = "character"

    cID: Mapped[int] = mapped_column(primary_key=True)
    cRV: Mapped[datetime.datetime] = mapped_column(server_default = func.CURRENT_TIMESTAMP())
    cextID: Mapped[Optional[str]]
    cNAME: Mapped[str]
    cREALM: Mapped[str]
    cFACTION: Mapped[str]
    cRACE: Mapped[str]
    cGUILD: Mapped[Optional[str]]
    accountID: Mapped[int] = mapped_column(ForeignKey("account.aID"))

    account: Mapped["Account"] = relationship(back_populates="characters")
    #dungeons: Mapped["DungeonRun"] = relationship(back_populates="character")

    def __repr__(self) -> str: 
        return f"Character(cNAME={self.cNAME!r}, cREALM={self.cREALM!r}, cFACTION={self.cFACTION!r}, cRACE={self.cRACE!r}, cGUILD={self.cGUILD!r}, accountID={self.accountID}, cID={self.cID!r})"
    