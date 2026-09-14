from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from anthropic import Anthropic
from database import SessionLocal, engine, Base
from models import User, Conversation, Message
import os

load_dotenv()

app = FastAPI()
Base.metadata.create_all(bind=engine)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    conversation_id : int

class ConversationRequest(BaseModel):
    name : str

@app.get("/hello")
def say_hello():
    return {"message" : "Hello from backend"}

@app.get("/conversation_starter")
def conv_start():
    return FileResponse("index.html")


@app.post("/chat")
def chat(request: ChatRequest):
    db = SessionLocal()
    conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    user_message = Message(conversation_id = request.conversation_id, role = "user", content=request.message)
    db.add(user_message)
    db.commit()

    messages_history = []

    for msg in (db.query(Message).filter(Message.conversation_id == request.conversation_id).all()):
        messages_history.append({"role": msg.role, "content": msg.content})

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1000,
        messages = messages_history
    )
    for block in response.content:
        if block.type == "text":
           assistant_message =  Message(conversation_id=request.conversation_id, role = "assistant", content = block.text)
           db.add(assistant_message)
           db.commit()
           return {"reply": block.text}


@app.post("/new-conversation")
def conversation(req : ConversationRequest):
    db = SessionLocal()
    user_conversation = Conversation(user_id=None, name=req.name)
    db.add(user_conversation)
    db.commit()

    db.refresh(user_conversation)

    return {"conversation": req.name, "id":user_conversation.id}
