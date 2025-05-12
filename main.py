from fastapi import FastAPI, HTTPException, UploadFile, File
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

@app.post("/upload_csv")
def upload_csv(arquivo: UploadFile = File(...)):
    try:
        marcadores = []
        for linha in csv.DictReader(io.TextIOWrapper(arquivo.file, encoding="utf-8")):
            try:
                marcadores.append({
                    "tipo": linha.get("tipo_crime", ""),
                    "bairro": linha.get("bairro", ""),
                    "hora": linha.get("hora", ""),
                    "lat": float(linha["latitude"]),
                    "lng": float(linha["longitude"])
                })
            except:
                continue
        return {
            "mensagem": f"Arquivo recebido com {len(marcadores)} registros.",
            "marcadores": marcadores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar CSV: {str(e)}")

