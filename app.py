from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from anthropic import Anthropic
from database import SessionLocal, engine, Base
from models import User, Conversation, Message
from neuro_models import Studies, Coordinate, Concept, Study_concept, RateLimit
from neuro_queries import get_regions_for_concept
from prompt import explanation_system_prompt, extraction_system_prompt
from datetime import datetime, date
import os

load_dotenv()
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS","http://localhost:5173")
origin_list = ALLOWED_ORIGINS.split(",")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

concept_extraction_tool = {
    "name": "extract_concepts",
    "description":"Extract cognitive/psychological/emotional concepts mentioned or implied in the user's message that relate to brain function.",
    "input_schema": {
        "type":"object",
        "properties": {
            "concepts": {
                "type":"array",
                "items": {"type":"string"},
                "description":"List of up to 3 concept names representing the scenario, using standard, single-word or short well-established neuroscience/psychology terms — the kind that appear in real cognitive neuroscience research abstracts, e.g. 'fear', 'anxiety', 'memory', 'navigation', 'attention', 'reward', 'stress', 'emotion', 'language', 'decision-making'. These terms are matched against a fixed scientific vocabulary, so prefer the single most standard, general term for an idea rather than a descriptive phrase or compound label. For example, use 'fear' instead of 'fear of snakes' or 'evolutionary preparedness toward snakes'; use 'threat' instead of 'threat detection system'. If you're unsure whether a precise term exists, choose the closest common, general term rather than a more specific or compound one — a slightly broader match is better than no match. Return up to 3 concepts, prioritizing the most central and relevant concepts, and do not add concepts simply to reach 3. Return an empty list only if truly no relevant concept applies."
            }
        },
        "required":["concepts"]
    }
}

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
def chat(request: ChatRequest, http_request: Request):
    db = SessionLocal()
    client_ip = http_request.client.host
    today = str(date.today())
    row = db.query(RateLimit).filter(RateLimit.ip==client_ip, RateLimit.date==today).first()
    if row is None:
        user_limit = RateLimit(ip = client_ip, date = today, count = 1)
        db.add(user_limit)
        db.commit()
    elif row.count < 10:
        row.count += 1
        db.commit()
    else:
        raise HTTPException(status_code=429, detail="Prompt limit has been hit.")

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
        messages = messages_history,
        system = extraction_system_prompt,
        tools = [concept_extraction_tool]
    )
    reply_text = None
    reply2_text = None
    concept_list = None
    top_studies =[]
    coordinates = []
    CONFIDENCE_THRESHOLD = 0.30
    MAX_TOTAL_POINTS = 10
    coordinate_part = None
    narrative_part = None

    for block in response.content:
        if block.type == "text":
            reply_text = block.text
        if block.type == "tool_use":
            concept_list = block.input["concepts"]
            concept_list = concept_list[:3]

            # Stage 1: gather all candidate coordinates, grouped by concept
            coords_by_concept = {}
            for concept_name in concept_list:
                current_region = get_regions_for_concept(concept_name, db)
                coords_by_concept[concept_name] = current_region["coordinates"]
                top_studies.extend(current_region["top_studies"])

            # Stage 2: filter out weak evidence (below threshold) per concept
            filtered_by_concept = {}
            for concept_name, coords in coords_by_concept.items():
                filtered_by_concept[concept_name] = [c for c in coords if c["weight"] >= CONFIDENCE_THRESHOLD]

            # Stage 3: guarantee each concept its single strongest point, if it has any
            selected = []
            selected_keys = set()
            for concept_name in concept_list:
                candidates = filtered_by_concept.get(concept_name, [])
                if candidates:
                    best = max(candidates, key=lambda c: c["weight"])
                    best["concept"] = concept_name
                    selected.append(best)
                    selected_keys.add((best["study_name"], best["x"], best["y"], best["z"]))

            # Stage 4: fill remaining slots with the next-highest weights overall
            remaining_pool = []
            for concept_name, coords in filtered_by_concept.items():
                for c in coords:
                    key = (c["study_name"], c["x"], c["y"], c["z"])
                    if key not in selected_keys:
                        c["concept"] = concept_name
                        remaining_pool.append(c)
            remaining_pool.sort(key=lambda c: c["weight"], reverse=True)

            for c in remaining_pool:
                if len(selected) >= MAX_TOTAL_POINTS:
                    break
                key = (c["study_name"], c["x"], c["y"], c["z"])
                if key not in selected_keys:
                    selected.append(c)
                    selected_keys.add(key)

            # Stage 5: order by concept, assign global point numbers and evidence_strength labels
            selected.sort(key=lambda c: concept_list.index(c["concept"]))
            for i, c in enumerate(selected):
                c["point_number"] = i + 1
                if c["weight"] > 0.75:
                    c["evidence_strength"] = "High"
                elif c["weight"] > 0.50:
                    c["evidence_strength"] = "Medium"
                else:
                    c["evidence_strength"] = "Low"

            coordinates = selected

    if reply_text==None:
            reply_text=""

    if concept_list:
        second_message_history=""
        for concept in concept_list:
            second_message_history+=(f'The concepts are {concept}')
        for coordinate in coordinates:
            second_message_history+=(f'The coordinate point number is {coordinate["point_number"]} with coordinates {coordinate["x"]} {coordinate["y"]} {coordinate["z"]} and confidence is {coordinate["evidence_strength"]} related to the study {coordinate["study_name"]} by {coordinate["study_author"]}')

        second_conversation = [{"role":"user", "content":second_message_history}]

        response = client.messages.create(
                model="claude-sonnet-5",
                max_tokens=4000,
                system = explanation_system_prompt,
                messages = second_conversation
            )
        
        for block in response.content:
                if block.type == "text":
                   reply2_text = block.text
                   narrative_part, coordinate_part = reply2_text.split("## Coordinate Summary")
                   coordinate_part = '## Coordinate Summary' + coordinate_part
        if reply2_text is None:
            reply2_text = ""
        if reply_text != "":
             reply_text += " " + reply2_text
        else:
             reply_text += reply2_text

    if reply_text=="":
            reply_text="Second reply did not trigger.."

    if narrative_part == None:
        narrative_part = reply_text

    assistant_message =  Message(conversation_id=request.conversation_id, role = "assistant", content = reply_text)
    db.add(assistant_message)
    db.commit()
    
    return {"reply": reply_text, "coordinates": coordinates, "detected_concepts":concept_list, "narrative_part":narrative_part, "coordinate_part":coordinate_part}


@app.post("/new-conversation")
def conversation(req : ConversationRequest):
    db = SessionLocal()
    user_conversation = Conversation(user_id=None, name=req.name)
    db.add(user_conversation)
    db.commit()

    db.refresh(user_conversation)

    return {"conversation": req.name, "id":user_conversation.id}
