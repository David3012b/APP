from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
import json
import uuid

app = Flask(__name__)

# =====================
# CONFIG
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CARPETA_CARNETS = os.path.join(BASE_DIR, "static", "carnets")
os.makedirs(CARPETA_CARNETS, exist_ok=True)

PLANTILLA = os.path.join(BASE_DIR, "static", "fotos", "plantilla.jpg")

TOKENS_FILE = os.path.join(BASE_DIR, "tokens.json")
if not os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, "w") as f:
        json.dump([], f)

# =====================
# RUTAS
# =====================

@app.route("/")
def home():
    return "<h2>Servidor activo. Usa el link único.</h2>"

@app.route("/crear_link")
def crear_link():
    token = str(uuid.uuid4())

    with open(TOKENS_FILE, "r") as f:
        tokens = json.load(f)

    tokens.append({"token": token, "usado": False})

    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=4)

    link = f"{request.host_url}form/{token}"
    return f"<h3>Link único:</h3><a href='{link}' target='_blank'>{link}</a>"

@app.route("/form/<token>")
def form_token(token):
    with open(TOKENS_FILE, "r") as f:
        tokens = json.load(f)

    encontrado = next((t for t in tokens if t["token"] == token), None)

    if not encontrado:
        return "Enlace inválido", 403

    if encontrado["usado"]:
        return "Este enlace ya fue usado", 403

    return render_template("index.html", token=token)

@app.route("/generar", methods=["POST"])
def generar():
    tok




