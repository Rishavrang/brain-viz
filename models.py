from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name =  Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    role = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    conversation_id = Column(Integer, ForeignKey("conversations.id"))