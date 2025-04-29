from fastapi import FastAPI, Request, Form, UploadFile, File, RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from models import Fan, SessionLocal
import pytesseract
from PIL import Image

# Configuração do Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Instância do FastAPI
app = FastAPI()

# Servir arquivos estáticos (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Configura Jinja2 para renderizar HTML
templates = Jinja2Templates(directory="frontend")

# Página inicial: formulário de cadastro
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("web_app_furia.html", {"request": request})

# Página de upload de documento
@app.get("/upload", response_class=HTMLResponse)
async def get_upload_page(request: Request):
    return templates.TemplateResponse("upload_app.html", {"request": request})

# Página de painel admin
@app.get("/admin", response_class=HTMLResponse)
async def view_admin_panel(request: Request):
    db = SessionLocal()
    fans = db.query(Fan).all()
    db.close()
    return templates.TemplateResponse("admin.html", {"request": request, "fans": fans})

# Processamento do cadastro
@app.post("/register")
async def register_user(
    name: str = Form(...),
    cpf: str = Form(...),
    address: str = Form(...),
    email: str = Form(...),
):
    db = SessionLocal()
    fan = Fan(name=name, cpf=cpf, address=address, email=email)
    db.add(fan)
    db.commit()
    db.refresh(fan)
    db.close()

    # Redireciona para a página de sucesso após o cadastro
    return RedirectResponse(url=f"/success/{fan.id}", status_code=303)

# Página de sucesso após o cadastro
@app.get("/success/{fan_id}", response_class=HTMLResponse)
async def success_page(request: Request, fan_id: int):
    db = SessionLocal()
    fan = db.query(Fan).filter(Fan.id == fan_id).first()
    db.close()
    return templates.TemplateResponse("success.html", {"request": request, "fan": fan})

# Processamento do upload e validação de identidade
@app.post("/validate-id")
async def validate_id(file: UploadFile = File(...)):
    save_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        image = Image.open(save_path)
        text = pytesseract.image_to_string(image, lang='por')
        print("Texto extraído do documento:")
        print(text)

        # Simples validação baseada em palavras-chave
        if "FURIA" in text or "Romulo" in text:
            return RedirectResponse(url="/validated", status_code=303)  # Redireciona para a página de sucesso
        else:
            return {"message": "Documento inválido ou ilegível."}
    except Exception as e:
        return {"error": str(e)}

# Página de validação bem-sucedida
@app.get("/validated", response_class=HTMLResponse)
async def validated_page(request: Request):
    return templates.TemplateResponse("validated.html", {"request": request})

from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import tweepy
import facebook
import spacy

# Carregar o modelo de NLP
nlp = spacy.load('pt_core_news_sm')

# Funções para autenticação e interação com as APIs
# Twitter (X)
def get_user_tweets(username):
    consumer_key = 'SUA_CONSUMER_KEY'
    consumer_secret = 'SUA_CONSUMER_SECRET'
    access_token = 'SEU_ACCESS_TOKEN'
    access_token_secret = 'SEU_ACCESS_TOKEN_SECRET'
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    
    tweets = api.user_timeline(screen_name=username, count=10, tweet_mode="extended")
    tweet_texts = [tweet.full_text for tweet in tweets]
    return tweet_texts

# Instagram e Facebook
access_token = 'SEU_ACCESS_TOKEN'
graph = facebook.GraphAPI(access_token)

def get_instagram_profile_data(username):
    return graph.get_object(f'{username}?fields=id,name,followers_count,media')

def get_facebook_profile_data(username):
    return graph.get_object(f'{username}?fields=id,name,followers_count,posts')

# Função para verificar se o conteúdo é relevante para e-sports
def check_relevance(content):
    doc = nlp(content)
    esports_keywords = ['FURIA', 'CS:GO', 'gaming', 'e-sports', 'torneio', 'competição']
    
    for token in doc:
        if token.text.lower() in esports_keywords:
            return True
    return False

# Função de validação de redes sociais
@app.post("/validate-social")
async def validate_social_profile(url: str = Form(...)):
    if "twitter.com" in url:
        username = url.split('/')[-1]
        tweets = get_user_tweets(username)
        if any(check_relevance(tweet) for tweet in tweets):
            return {"message": "Conteúdo relevante encontrado no Twitter!"}
        else:
            raise HTTPException(status_code=400, detail="Conteúdo não relevante no perfil do Twitter.")
    
    elif "instagram.com" in url:
        profile_data = get_instagram_profile_data(url.split('/')[-1])
        for post in profile_data['media']['data']:
            if check_relevance(post['caption']):
                return {"message": "Conteúdo relevante encontrado no Instagram!"}
        raise HTTPException(status_code=400, detail="Conteúdo não relevante no perfil do Instagram.")

    elif "facebook.com" in url:
        profile_data = get_facebook_profile_data(url.split('/')[-1])
        for post in profile_data['posts']['data']:
            if check_relevance(post['message']):
                return {"message": "Conteúdo relevante encontrado no Facebook!"}
        raise HTTPException(status_code=400, detail="Conteúdo não relevante no perfil do Facebook.")
    
    else:
        raise HTTPException(status_code=400, detail="URL de rede social não reconhecida.")

# Código restante para o FastAPI
app = FastAPI()

# Configuração do Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Instância do FastAPI
app = FastAPI()

# Servir arquivos estáticos (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Configura Jinja2 para renderizar HTML
templates = Jinja2Templates(directory="frontend")

# Página inicial: formulário de cadastro
@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("web_app_furia.html", {"request": request})

# Página de upload de documento
@app.get("/upload", response_class=HTMLResponse)
async def get_upload_page(request: Request):
    return templates.TemplateResponse("upload_app.html", {"request": request})

# Página de painel admin
@app.get("/admin", response_class=HTMLResponse)
async def view_admin_panel(request: Request):
    db = SessionLocal()
    fans = db.query(Fan).all()
    db.close()
    return templates.TemplateResponse("admin.html", {"request": request, "fans": fans})

# Processamento do cadastro
@app.post("/register")
async def register_user(
    name: str = Form(...),
    cpf: str = Form(...),
    address: str = Form(...),
    email: str = Form(...),
):
    db = SessionLocal()
    fan = Fan(name=name, cpf=cpf, address=address, email=email)
    db.add(fan)
    db.commit()
    db.refresh(fan)
    db.close()

    # Redireciona para a página de sucesso após o cadastro
    return RedirectResponse(url=f"/success/{fan.id}", status_code=303)

# Página de sucesso após o cadastro
@app.get("/success/{fan_id}", response_class=HTMLResponse)
async def success_page(request: Request, fan_id: int):
    db = SessionLocal()
    fan = db.query(Fan).filter(Fan.id == fan_id).first()
    db.close()
    return templates.TemplateResponse("success.html", {"request": request, "fan": fan})

# Processamento do upload e validação de identidade
@app.post("/validate-id")
async def validate_id(file: UploadFile = File(...)):
    save_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        image = Image.open(save_path)
        text = pytesseract.image_to_string(image, lang='por')
        print("Texto extraído do documento:")
        print(text)

        # Simples validação baseada em palavras-chave
        if "FURIA" in text or "Romulo" in text:
            return RedirectResponse(url="/validated", status_code=303)  # Redireciona para a página de sucesso
        else:
            return {"message": "Documento inválido ou ilegível."}
    except Exception as e:
        return {"error": str(e)}

# Página de validação bem-sucedida
@app.get("/validated", response_class=HTMLResponse)
async def validated_page(request: Request):
    return templates.TemplateResponse("validated.html", {"request": request})
