from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
import csv
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_users_db = {
    "teste@bh.com": {
        "senha": "123456",
        "data_criacao": "2025-05-10",
        "dias_de_teste": 7,
        "permissao": "GCM"
    }
}

class Login(BaseModel):
    email: str
    senha: str

@app.post("/cadastro")
def cadastro(dados: Login):
    if dados.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Usuário já cadastrado")

    fake_users_db[dados.email] = {
        "senha": dados.senha,
        "data_criacao": datetime.now().strftime("%Y-%m-%d"),
        "dias_de_teste": 7,
        "permissao": "GCM"
    }
    return {"mensagem": "Usuário cadastrado com sucesso. Você já pode fazer login."}

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
        "token": "token_fake",
        "permissao": user["permissao"]
    }

@app.post("/upload_csv")
def upload_csv(arquivo: UploadFile = File(...)):
    try:
        marcadores = []
        wrapper = io.TextIOWrapper(arquivo.file, encoding="utf-8")
        leitor = csv.DictReader(wrapper)
        for linha in leitor:
            if "latitude" in linha and "longitude" in linha:
                try:
                    lat = float(linha["latitude"])
                    lng = float(linha["longitude"])
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        marcadores.append({
                            "tipo": linha.get("tipo_crime", ""),
                            "bairro": linha.get("bairro", ""),
                            "hora": linha.get("hora", ""),
                            "lat": lat,
                            "lng": lng
                        })
                except:
                    continue
        wrapper.detach()
        return {
            "mensagem": f"Arquivo processado com {len(marcadores)} registros válidos.",
            "marcadores": marcadores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar CSV: {str(e)}")
