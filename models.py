import datetime
from typing import List
from typing import Optional
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
    firstNAME: Mapped[str]
    middleNAME: Mapped[Optional[str]]
    lastNAME: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    pcreationDT: Mapped[datetime.datetime] = mapped_column(server_default = func.CURRENT_TIMESTAMP())
    #lastmodDT: Mapped[datetime.datetime] = mapped_column

    accounts: Mapped[List["Account"]] = relationship()

    def __repr__(self) -> str:
        return f"Person(pID={self.pID!r}, firstNAME={self.firstNAME!r}, middleNAME={self.middleNAME!r}, lastNAME{self.lastNAME!r}, email={self.email!r}, pcreationDT={self.pcreationDT!r})"

class Account(Base):
    __tablename__ = "account"

    aID: Mapped[int] = mapped_column(primary_key=True)
    wowACCOUNT: Mapped[str]
    bnetNAME: Mapped[str]
    personID: Mapped[int] = mapped_column(ForeignKey("person.pID"))

    person: Mapped["Person"] = relationship()
    characters: Mapped[List["Character"]] = relationship()

    def __repr__(self) -> str:
        return f"Account(aID={self.aID!r}, wowACCOUNT={self.wowACCOUNT!r}, bnetNAME={self.bnetNAME!r}, personID={self.personID!r}, person={self.person!r}, characters={self.characters!r})"

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
    dungeonruns: Mapped[List["DungeonRun"]] = relationship()
    levelhistory: Mapped[List["CharacterLevelHistory"]] = relationship()

    def __repr__(self) -> str: 
        return f"Character(cNAME={self.cNAME!r}, cREALM={self.cREALM!r}, cFACTION={self.cFACTION!r}, cRACE={self.cRACE!r}, cGUILD={self.cGUILD!r}, accountID={self.accountID}, cID={self.cID!r}, account={self.account!r})"
       

class Dungeon(Base):
    __tablename__ = "dungeon"

    dID: Mapped[int] = mapped_column(primary_key=True)
    dungeonID: Mapped[int]
    dungeonNAME: Mapped[str]
    dungeonZONE: Mapped[str]
    dungeonERA: Mapped[str]
    dungeonminLVL: Mapped[int]
    dungeonmaxLVL: Mapped[int]
    dungeonmaxPLAYERS: Mapped[Optional[int]]
    
    dungeonruns = Mapped[List["DungeonRun"]] = relationship()

class DungeonRun(Base):
    __tablename__ = "dungeonrun"

    dungeonrunID: Mapped[int] = mapped_column(primary_key=True)
    RV: Mapped[datetime.datetime] = mapped_column(server_default = func.CURRENT_TIMESTAMP())
    extID: Mapped[Optional[str]]
    startDT: Mapped[datetime.datetime]
    stopDT: Mapped[datetime.datetime]
    startLVL: Mapped[int]
    stopLVL: Mapped[int]
    startXP: Mapped[int]
    stopXP: Mapped[int]
    startREST: Mapped[int]
    stopREST: Mapped[int]
    startGOLD: Mapped[int]
    stopGOLD: Mapped[int]
    characterdungeonROLE: Mapped[str]
    dungeonID: Mapped[str] = mapped_column(ForeignKey("dungeon.dID"))
    characterID: Mapped[int] = mapped_column(ForeignKey("character.cID"))

    character= Mapped["Character"] = relationship()
    dungeon= Mapped["Dungeon"] = relationship()

class LevelReference(Base):
    __tablename__ = "levelreference"

    lvlID: Mapped[int] = mapped_column(primary_key=True)
    lvlNUMBER: Mapped[int]
    lvlmaxXP: Mapped[int]

class CharacterLevelHistory(Base):
    __tablename__ = "characterlevelhistory"

    clvlhxID: Mapped[int] = mapped_column(primary_key=True)
    clvlhxRV: Mapped[datetime.datetime] = mapped_column(server_default = func.CURRENT_TIMESTAMP())
    clvlhxNUMBER: Mapped[int]
    clvlhxXP: Mapped[int]
    characterID: Mapped[int] = mapped_column(ForeignKey="Character.cID")
    