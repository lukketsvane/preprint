# Define a variable to hold the state of web scraping checkbox
web_scraping_enabled = False  # This value can be updated based on the checkbox value from the front-end
from typing import List
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import json
import os

# Importing the ResearchAgent and PDF processing function
from agent.research_agent import ResearchAgent
from actions.file_scrape import load_and_process_pdfs

app = FastAPI()
app.mount("/site", StaticFiles(directory="client"), name="site")
app.mount("/static", StaticFiles(directory="static"), name="static")
# Dynamic directory for outputs once first research is run
@app.on_event("startup")
def startup_event():
    if not os.path.isdir("outputs"):
        os.makedirs("outputs")
    app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

templates = Jinja2Templates(directory="client")

class ResearchRequest(BaseModel):
    task: str
    report_type: str
    agent: str

# WebSocket manager placeholder for the example
class WebSocketManager:
    async def connect(self, websocket):
        pass

    async def disconnect(self, websocket):
        pass

    async def start_streaming(self, task, report_type, agent, agent_role_prompt, websocket):
        pass

manager = WebSocketManager()

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse('index.html', {"request": request, "report": None})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith("start"):
                json_data = json.loads(data[6:])
                task = json_data.get("task")
                report_type = json_data.get("report_type")
                agent = json_data.get("agent")
                agent_role_prompt = None  # Placeholder for the example

                research_agent = ResearchAgent(agent, websocket, agent_role_prompt)  # Pass the agent_role_prompt
                await research_agent.process(task, report_type, agent_role_prompt)

    except WebSocketDisconnect:
        pass
