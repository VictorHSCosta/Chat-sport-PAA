from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import time
import random

class QuestionRequest(BaseModel):
    message: str

class QuestionResponse(BaseModel):
    answer: str
    success: bool
    message: str = ""

class HealthResponse(BaseModel):
    status: str
    message: str

app = FastAPI(
    title="Chat Sport FAST API",
    description="API rápida para testes sem RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FAST_RESPONSES = {
    "default": [
        "Ótima pergunta sobre futebol! 🏈",
        "Interessante questão esportiva! ⚽",
        "Vou te ajudar com essa pergunta sobre esportes!",
        "Excelente pergunta sobre futebol!",
    ],
    "keywords": {
        "pele": "Pelé (1940-2022) é considerado o Rei do Futebol! Nasceu como Edson Arantes do Nascimento, conquistou 3 Copas do Mundo (1958, 1962, 1970) pelo Brasil, marcou mais de 1000 gols na carreira, jogou no Santos FC e no New York Cosmos. É uma lenda eterna do esporte! ⚽👑",
        "história": "Pelé começou sua carreira no Santos aos 15 anos, tornou-se o jogador mais jovem a marcar em uma Copa do Mundo aos 17 anos em 1958. Revolucionou o futebol com sua técnica, velocidade e carisma, sendo embaixador do esporte mundialmente.",
        "messi": "Lionel Messi é um dos maiores jogadores de todos os tempos, com 8 Bolas de Ouro! Argentino, conquistou a Copa do Mundo de 2022 e tem uma carreira brilhante no Barcelona e PSG.",
        "ronaldo": "Cristiano Ronaldo é uma lenda viva do futebol mundial! Português, 5 Bolas de Ouro, goleador histórico da Champions League.",
        "palmeiras": "Palmeiras é o atual campeão da Libertadores e tem uma rica história no futebol brasileiro! Conhecido como Verdão, tem uma das maiores torcidas do país.",
        "flamengo": "Flamengo é o time mais popular do Brasil e tem milhões de torcedores! Rubro-Negro carioca com história vitoriosa.",
        "copa": "A Copa do Mundo é o maior evento do futebol mundial, acontecendo a cada 4 anos! A próxima será em 2026 nos EUA, Canadá e México.",
        "brasil": "O Brasil é o país com mais títulos de Copa do Mundo: 5 conquistas (1958, 1962, 1970, 1994, 2002)! Terra do futebol arte.",
        "champions": "A Champions League é a principal competição de clubes da Europa! O torneio mais prestigioso do futebol de clubes.",
        "santos": "Santos FC é o clube onde Pelé brilhou! Time da Vila Belmiro, berço de grandes craques do futebol brasileiro.",
        "mundo": "O futebol é o esporte mais popular do mundo, praticado em todos os continentes e unindo pessoas de todas as culturas! ⚽🌍"
    }
}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        message="API rápida funcionando!"
    )

@app.post("/chat", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    print(f"🚀 [FAST] Pergunta recebida: {request.message}")
    
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Pergunta não pode estar vazia"
        )
    
    time.sleep(0.3)
    
    message_lower = request.message.lower()
    
    found_responses = []
    
    for keyword, response in FAST_RESPONSES["keywords"].items():
        if keyword in message_lower:
            found_responses.append(response)
    
    if found_responses:
        answer = found_responses[0] if len(found_responses) == 1 else " | ".join(found_responses[:2])
        return QuestionResponse(
            answer=answer,
            success=True,
            message="Resposta rápida baseada em palavra-chave"
        )
    
    answer = random.choice(FAST_RESPONSES["default"])
    
    return QuestionResponse(
        answer=f"{answer} Você perguntou: '{request.message}' - Esta é uma API de teste rápida. Para respostas mais detalhadas, use a API principal na porta 8000.",
        success=True,
        message="Resposta rápida gerada"
    )

@app.get("/")
async def root():
    return {
        "message": "Chat Sport FAST API",
        "version": "1.0.0",
        "note": "Versão rápida para testes",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "api_fast:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
