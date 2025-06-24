from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app_context import get_agent_executor
from utils.session import generate_session_id
import logging

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/session")
async def get_session_id():
    session_id = generate_session_id()
    logging.info(f"[session] New session created: {session_id}")
    return {"session_id": session_id}

@router.post("/chat/{session_id}")
async def chat_with_user(session_id: str, request: Request):
    try:
        user_input = await request.json()
        message = user_input.get("message")

        if not message:
            raise ValueError("No input message provided")

        logging.info(f"[chat] Session: {session_id}, User message: {message}")

        agent_executor = get_agent_executor(session_id)
        response = await agent_executor.ainvoke({"input": message})

        return {"response": response["output"]}

    except Exception as e:
        logging.exception(f"[chat] Error in session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong while processing your message.")
