from fastapi import FastAPI, APIRouter, File, UploadFile
from pydantic import BaseModel
from PIL import Image
import io

# Criando a instância FastAPI
app = FastAPI()

# Permitir CORS (cross-origin requests)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou defina domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# **Modelos de dados (Pydantic)**

class UserCreate(BaseModel):
    name: str
    cpf: str
    address: str
    email: str


# **Rota de cadastro de usuário**

@app.post("/register")
async def register(user: UserCreate):
    # Aqui você pode salvar no banco de dados (exemplo simples)
    return {"message": f"Usuário {user.name} cadastrado com sucesso!"}


# **Função de validação de documentos (upload de imagem)**

@app.post("/validate-id")
async def validate_id(file: UploadFile = File(...)):
    # Lê o arquivo enviado
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # Aqui você pode usar IA para validação (exemplo básico)
    image.show()  # Apenas exibe a imagem para teste

    return {"message": "Imagem recebida com sucesso!"}


# **Rodando o servidor**
# Para rodar o servidor, basta executar o seguinte comando no terminal:
# uvicorn main:app --reload
