# ======================================================
# SIGNALCHECK API – APP.PY (SINCRONIZADO CON POPUP V2.1)
# ======================================================

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import time

# 🔥 IMPORT REAL
from backend.engine import analyze_context

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VerifyRequest(BaseModel):
    url: str
    text: str

def generate_analysis_key(url: str, text: str) -> str:
    content_hash = hashlib.sha256(text.encode()).hexdigest()
    base = f"{url}|{content_hash}|v13"
    return hashlib.sha256(base.encode()).hexdigest()

@app.post("/v3/verify")
async def verify(req: VerifyRequest, request: Request):
    # Verificación de ID de extensión
    extension_id = request.headers.get("x-extension-id")
    if not extension_id:
        raise HTTPException(status_code=401, detail="Extensión no autorizada")

    try:
        # Ejecutar el motor que ya sabemos que funciona
        result = analyze_context(req.text, req.url)
        
        # Mapeo de datos para el popup.js
        analysis_data = {
            "score": int(result.get("score", 0)),
            "level": result.get("level", "green"), # Mantenemos red/yellow/green para el badge
            "message": result.get("message", "Análisis completado"),
            "confidence": float(result.get("confidence", 0)),
            "pro": result.get("pro", {})
        }

        # Respuesta con la estructura que espera popup.js
        return {
            "status": "success",
            "meta": { 
                "plan": "pro" if request.headers.get("x-pro-token") else "free",
                "timestamp": int(time.time())
            },
            "analysis": analysis_data,
            "analysis_key": generate_analysis_key(req.url, req.text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"status": "SignalCheck API running"}