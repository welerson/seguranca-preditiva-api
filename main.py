from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

app = FastAPI()

# Permitir requisições externas (como do Netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou especifique: ["https://seuapp.netlify.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Usuário de teste
fake_users_db = {
    "teste@bh.com": {
        "senha": "123456",
        "data_criacao": "2025-05-10",
        "dias_de_teste": 7,
        "permissao": "GCM"
    }
}

# Modelo de entrada
class Login(BaseModel):
    email: str
    senha: str

# Rota de login
@app.post("/login")
def login(dados: Login):
    user = fake_users_db.get(dados.email)
    if not user or user["senha"] != dados.senha:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    data_criacao = datetime.strptime(user["data_criacao"], "%Y-%m-%d")
    fim_teste = data_criacao + timedelta(days=user["dias_de_teste"])
    expirado = datetime.now() > fim_teste

    return {
        "status": "ok",
        "expirado": expirado,
        "token": "token_fake_seguranca",
        "permissao": user["permissao"]
    }

# Executa no ambiente do Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
