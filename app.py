import os
from dotenv import load_dotenv   # ✅ ADD
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import shutil
import ollama
from summarizer import summarize_book

# ✅ Load env variables
load_dotenv()

app = FastAPI()

# 📁 Setup folders
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📁 Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Temporary storage (demo)
app_data = {"summary": "", "model": "", "lang": ""}


# 🔹 Home Page
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html"
    )


# 🔹 Check model status
@app.get("/status")
async def get_status():
    status = {"ollama": False, "gemini": True}
    try:
        ollama.list()
        status["ollama"] = True
    except Exception:
        status["ollama"] = False
    return status


# 🔹 Upload + Summarize
@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    language: str = Form("English"),
    model_type: str = Form("ollama"),
):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    summary_text = summarize_book(file_path, language, model_type)

    app_data["summary"] = summary_text
    app_data["model"] = model_type.upper()
    app_data["lang"] = language

    return RedirectResponse(url="/result", status_code=303)


# 🔹 Result Page
@app.get("/result")
async def result(request: Request):
    if not app_data["summary"]:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request,
        "result.html",
        {
            "summary": app_data["summary"],
            "model": app_data["model"],
            "language": app_data["lang"],
        },
    )