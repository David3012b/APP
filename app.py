from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
import json
import uuid
import traceback

app = Flask(__name__)

# =====================
# Carpetas
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CARPETA_CARNETS = os.path.join(BASE_DIR, "static", "carnets")
os.makedirs(CARPETA_CARNETS, exist_ok=True)

TOKENS_FILE = os.path.join(BASE_DIR, "tokens.json")
if not os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, "w") as f:
        json.dump([], f)

# =====================
# Rutas
# =====================

@app.route("/")
def home():
    return "<h2>Servidor funcionando. Usa el link que te fue enviado.</h2>"

@app.route("/crear_link")
def crear_link():
    token = str(uuid.uuid4())

    with open(TOKENS_FILE, "r") as f:
        tokens = json.load(f)

    tokens.append({"token": token, "usado": False})

    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=4)

    base_url = request.host_url
    link = f"{base_url}form/{token}"
    return f"<h3>Link único:</h3><a href='{link}' target='_blank'>{link}</a>"

@app.route("/form/<token>")
def form_token(token):
    with open(TOKENS_FILE, "r") as f:
        tokens = json.load(f)

    encontrado = next((t for t in tokens if t["token"] == token), None)

    if encontrado is None:
        return "<h1>Enlace inválido</h1>", 403

    if encontrado["usado"]:
        return "<h1>Este enlace ya fue usado</h1>", 403

    return render_template("index.html", token=token)

@app.route("/generar", methods=["POST"])
def generar():
    try:
        token = request.form.get("token")
        if not token:
            return "Token faltante", 403

        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)

        encontrado = next((t for t in tokens if t["token"] == token), None)

        if encontrado is None:
            return "Token inválido", 403

        if encontrado["usado"]:
            return "Este enlace ya fue usado", 403

        # Marcar token como usado
        encontrado["usado"] = True
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f, indent=4)

        nombre = request.form.get("nombre", "").strip()
        documento = request.form.get("documento", "").strip()
        cargo = request.form.get("cargo", "").strip()

        if not (nombre and documento and cargo):
            return "Faltan campos", 400

        plantilla_path = os.path.join(BASE_DIR, "static", "fotos", "plantilla.jpg")

        if not os.path.exists(plantilla_path):
            return "No existe la plantilla", 500

        carnet = Image.open(plantilla_path).convert("RGBA")
        draw = ImageDraw.Draw(carnet)

        # FUENTE CON EL NUEVO TAMAÑO (CAMBIADO A 110)
        try:
            font = ImageFont.truetype("arial.ttf", 1000000)
        except:
            font = ImageFont.load_default()

        color = (20, 60, 20)

        # Ajusta las posiciones si es necesario
        x = 350
        y = 350

        draw.text((x, y), f"Nombre: {nombre}", font=font, fill=color)
        draw.text((x, y + 120), f"Documento: {documento}", font=font, fill=color)
        draw.text((x, y + 240), f"Cargo: {cargo}", font=font, fill=color)

        nombre_archivo = f"carnet_{documento}.png"
        ruta = os.path.join(CARPETA_CARNETS, nombre_archivo)
        carnet.save(ruta)

        return f"Carnet generado:<br><a href='/carnet/{nombre_archivo}' target='_blank'>VER CARNET</a>"

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"

@app.route("/carnet/<filename>")
def carnet(filename):
    return send_from_directory(CARPETA_CARNETS, filename)
