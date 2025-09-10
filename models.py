import datetime
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, BIGINT, TIMESTAMP, NVARCHAR, func, DateTime, text
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
    email: Mapped[str]

    accounts: Mapped[List["Account"]] = relationship(back_populates="person")

    def __repr__(self) -> str:
        accountNames = getListValues(self.accounts, "wowACCOUNT")

        return (
            f"Person(pID={self.pID!r}, "
            f"firstNAME={self.firstNAME!r}, "
            f"middleNAME={self.middleNAME!r}, "
            f"lastNAME={self.lastNAME!r}, "
            f"email={self.email!r}, "
            f"accounts={accountNames})"
        )

class Account(Base):
    __tablename__ = "account"

    aID: Mapped[int] = mapped_column(primary_key=True)
    wowACCOUNT: Mapped[str]
    bnetNAME: Mapped[str]
    personID: Mapped[int] = mapped_column(ForeignKey("person.pID"))

    person: Mapped["Person"] = relationship(back_populates="accounts")
    characters: Mapped[List["Character"]] = relationship(back_populates="account")

    def __repr__(self) -> str:
        # Person info
        if self.person:
            personId = self.person.pID
            personFirstName = self.person.firstNAME if self.person.firstNAME else "NO_DATA"
        else:
            personId = "NO_DATA"
            personFirstName = "NO_DATA"

        # Character info using getListValues
        characterNames = getListValues(self.characters, "cNAME")
        characterIds = getListValues(self.characters, "cID")

        return (
            f"Account(aID={self.aID!r}, "
            f"wowACCOUNT={self.wowACCOUNT!r}, "
            f"bnetNAME={self.bnetNAME!r}, "
            f"personID={personId}, "
            f"personFirstName={personFirstName}, "
            f"characterIDs={characterIds}, "
            f"characterNames={characterNames})"
        )

class Character(Base):
    __tablename__ = "character"

    cID: Mapped[int] = mapped_column(primary_key=True)
    cRV: Mapped[datetime.datetime] = mapped_column(DateTime, server_default = text("GETDATE()"))
    cextID: Mapped[Optional[str]]
    cNAME: Mapped[str]
    cREALM: Mapped[str]
    cFACTION: Mapped[str]
    cRACE: Mapped[str]
    cGUILD: Mapped[Optional[str]]
    accountID: Mapped[int] = mapped_column(ForeignKey("account.aID"))

    account: Mapped["Account"] = relationship(back_populates="characters")
    dungeonruns: Mapped[List["DungeonRun"]] = relationship(back_populates="character")
    levelhistory: Mapped[List["CharacterLevelHistory"]] = relationship(back_populates="character")

    def __repr__(self) -> str:
            # Account info
        if self.account:
            accountBnetName = self.account.bnetNAME if self.account.bnetNAME else "NO_DATA"
        else:
            accountBnetName = "NO_DATA"

        # LevelHistory info
        levelsReached = getListValues(self.levelhistory, "clvlhxNUMBER")

        return( f"Character(cID={self.cID!r}, "
                f"cNAME={self.cNAME!r}, "
                f"cREALM={self.cREALM!r}, "
                f"cFACTION={self.cFACTION!r}, "
                f"cRACE={self.cRACE!r}, "
                f"cGUILD={self.cGUILD!r}, "
                f"accountID={self.accountID}, "
                f"accountBnetName={accountBnetName}, "
                f"levelHistoryIDs={levelsReached})"
        )

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

    dungeonruns: Mapped[List["DungeonRun"]] = relationship(back_populates="dungeon")

    def __repr__(self) -> str:
        # DungeonRun info


        return (
            f"Dungeon(dID={self.dID!r}, "
            f"dungeonID={self.dungeonID!r}, "
            f"dungeonNAME={self.dungeonNAME!r}, "
            f"dungeonZONE={self.dungeonZONE!r}, "
            f"dungeonERA={self.dungeonERA!r}, "
            f"dungeonminLVL={self.dungeonminLVL!r}, "
            f"dungeonmaxLVL={self.dungeonmaxLVL!r}, "
            f"dungeonmaxPLAYERS={self.dungeonmaxPLAYERS if self.dungeonmaxPLAYERS is not None else 'NO_DATA'}"
        )

class DungeonRun(Base):
    __tablename__ = "dungeonrun"

    dungeonrunID: Mapped[int] = mapped_column(primary_key=True)
    RV: Mapped[datetime.datetime] = mapped_column(DateTime, server_default = text("GETDATE()"))
    extID: Mapped[Optional[str]]
    startDT: Mapped[str]
    stopDT: Mapped[str]
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

    character: Mapped["Character"] = relationship(back_populates="dungeonruns")
    dungeon: Mapped["Dungeon"] = relationship(back_populates="dungeonruns")

    def __repr__(self) -> str:
        # Character info
        if self.character:
            characterId = self.character.cID
            characterName = self.character.cNAME if self.character.cNAME else "NO_DATA"
        else:
            characterId = "NO_DATA"
            characterName = "NO_DATA"

        # Dungeon info
        if self.dungeon:
            dungeonId = self.dungeon.dID
            dungeonName = self.dungeon.dungeonNAME if self.dungeon.dungeonNAME else "NO_DATA"
        else:
            dungeonId = "NO_DATA"
            dungeonName = "NO_DATA"

        return (
            f"DungeonRun(dungeonrunID={self.dungeonrunID!r}, "
            f"extID={self.extID!r}, "
            f"startDT={self.startDT!r}, "
            f"stopDT={self.stopDT!r}, "
            f"startLVL={self.startLVL!r}, "
            f"stopLVL={self.stopLVL!r}, "
            f"startXP={self.startXP!r}, "
            f"stopXP={self.stopXP!r}, "
            f"startREST={self.startREST!r}, "
            f"stopREST={self.stopREST!r}, "
            f"startGOLD={self.startGOLD!r}, "
            f"stopGOLD={self.stopGOLD!r}, "
            f"characterdungeonROLE={self.characterdungeonROLE!r}, "
            f"characterID={characterId}, "
            f"characterName={characterName}, "
            f"dungeonID={dungeonId}, "
            f"dungeonName={dungeonName})"
        )

class LevelReference(Base):
    __tablename__ = "levelreference"

    lvlID: Mapped[int] = mapped_column(primary_key=True)
    lvlNUMBER: Mapped[int]
    lvlmaxXP: Mapped[int]

class CharacterLevelHistory(Base):
    __tablename__ = "characterlevelhistory"

    clvlhxID: Mapped[int] = mapped_column(primary_key=True)
    clvlhxRV: Mapped[datetime.datetime] = mapped_column(DateTime, server_default = text("GETDATE()"))
    clvlhxNUMBER: Mapped[int]
    clvlhxXP: Mapped[int]
    characterID: Mapped[int] = mapped_column(ForeignKey("character.cID"))

    character: Mapped["Character"] = relationship(back_populates="levelhistory")

    def __repr__(self) -> str:
        # Character info
        if self.character:
            characterId = self.character.cID
            characterName = self.character.cNAME if self.character.cNAME else "NO_DATA"
        else:
            characterId = "NO_DATA"
            characterName = "NO_DATA"

        return (
            f"CharacterLevelHistory(clvlhxID={self.clvlhxID!r}, "
            f"clvlhxNUMBER={self.clvlhxNUMBER!r}, "
            f"clvlhxXP={self.clvlhxXP!r}, "
            f"characterID={characterId}, "
            f"characterName={characterName})"
        )

def getListValues(objects: List[DeclarativeBase], attributeName: str) -> List:
    """
    /**
     * @brief Extracts values of a specified attribute from SQLAlchemy model instances.
     *
     * Replaces missing or None values with "NO_DATA". Returns ["NO_DATA"] if the list is empty.
     *
     * @param objects        List of SQLAlchemy model instances.
     * @param attributeName  Attribute name to extract.
     * @return List of attribute values with missing data replaced by "NO_DATA".
     */
    """
    results: List = []

    if not objects:
        results.append("NO_DATA")
        return results

    for obj in objects:
        value = getattr(obj, attributeName, None)
        if value is None:
            results.append("NO_DATA")
        else:
            results.append(value)

    return results
