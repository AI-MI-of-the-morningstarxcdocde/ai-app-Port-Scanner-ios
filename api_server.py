from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from scanner.port_scanner import run_scan
from wireless.wireless_attacks import run_attack
from ai.predictive_model import predict_open_ports
from utils.chatbot import Chatbot

app = FastAPI(title="Advanced Port Scanner API", version="1.0")

chatbot = Chatbot()

class ScanRequest(BaseModel):
    target: str
    ports: Optional[str] = "1-1000"
    scan_type: Optional[str] = "all"

class WirelessAttackRequest(BaseModel):
    target: str

class ChatbotRequest(BaseModel):
    message: str

@app.post("/scan/port")
async def port_scan(request: ScanRequest):
    try:
        results = []
        # run_scan yields (progress, line), collect lines
        for progress, line in run_scan(request.target, request.scan_type):
            results.append(line)
        return {"target": request.target, "ports": request.ports, "scan_type": request.scan_type, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan/predictive")
async def predictive_scan(target: str):
    try:
        open_ports = predict_open_ports(target)
        return {"target": target, "predicted_open_ports": open_ports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/attack/wireless")
async def wireless_attack(request: WirelessAttackRequest):
    try:
        run_attack(request.target)
        return {"target": request.target, "status": "Wireless attack completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chatbot")
async def chatbot_interact(request: ChatbotRequest):
    try:
        response = chatbot.process_input(request.message)
        return {"message": request.message, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
