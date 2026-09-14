from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.sql import func
from database import Base

class Studies(Base):
    __tablename__ = "studies"

    id = Column(String, primary_key=True)
    name = Column(String(255))
    author = Column(String(255))
    publish_date = Column(String)

class Coordinate(Base):
    __tablename__ = "coordinates"

    id = Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    study_id = Column(String, ForeignKey("studies.id"))

class Concept(Base):
    __tablename__ = "concepts"

    name =  Column(String(255))
    id =  Column(Integer, primary_key=True)

class Study_concept(Base):
    __tablename__ = "study_concepts"

    id = Column(Integer, primary_key=True)
    weight = Column(Float)
    study_id = Column(String, ForeignKey("studies.id"))
    concepts_id = Column(Integer, ForeignKey("concepts.id"))
