from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
import json
import uuid
import traceback

app = Flask(__name__)

# ================= CONFIG =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CARPETA_CARNETS = os.path.join(BASE_DIR, "static", "carnets")
os.makedirs(CARPETA_CARNETS, exist_ok=True)

PLANTILLA = os.path.join(BASE_DIR, "static", "fotos", "plantilla.jpg")

# 🔑 Tokens
TOKENS_FILE = os.path.join(BASE_DIR, "tokens.json")
if not os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, "w") as f:
        json.dump([], f)

# Tamaño FINAL del carnet (CLAVE DEL ARREGLO)
CARNET_WIDTH = 2000
CARNET_HEIGHT = 1200
# =========================================


@app.route("/")
def index():
    return "<h2>Usa el link único que te fue enviado.</h2>"


# 🔗 Crear link único
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


# 📝 Mostrar formulario solo si el token es válido
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


# 🖨️ Generar carnet
@app.route("/generar", methods=["POST"])
def generar():
    try:
        token = request.form.get("token")
        if not token:
            return "Token faltante", 403

        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)

        encontrado = next((t for t in tokens if t["token"] == token), None)

        if encontrado is None or encontrado["usado"]:
            return "Enlace inválido o ya usado", 403

        # Marcar token como usado
        encontrado["usado"] = True
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f, indent=4)

        nombre = request.form.get("nombre", "").strip()
        documento = request.form.get("documento", "").strip()
        cargo = request.form.get("cargo", "").strip()

        if not (nombre and documento and cargo):
            return "Faltan campos", 400

        # ===== Abrir y REDIMENSIONAR plantilla =====
        carnet = Image.open(PLANTILLA).convert("RGB")
        carnet = carnet.resize((CARNET_WIDTH, CARNET_HEIGHT))
        draw = ImageDraw.Draw(carnet)

        # ===== Fuente (Arial / default) =====
        try:
            font = ImageFont.truetype("arial.ttf", 90)
        except:
            font = ImageFont.load_default()

        color = (30, 60, 30)

        # ===== Posiciones =====
        x = 700
        y = 450

        draw.text((x, y), f"Nombre: {nombre}", fill=color, font=font)
        draw.text((x, y + 130), f"Documento: {documento}", fill=color, font=font)
        draw.text((x, y + 260), f"Cargo: {cargo}", fill=color, font=font)

        # Guardar carnet
        nombre_archivo = f"carnet_{documento}.png"
        ruta = os.path.join(CARPETA_CARNETS, nombre_archivo)
        carnet.save(ruta)

        return f"Carnet generado:<br><a href='/carnet/{nombre_archivo}' target='_blank'>VER CARNET</a>"

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"


@app.route("/carnet/<filename>")
def carnet(filename):
    return send_from_directory(CARPETA_CARNETS, filename)


if __name__ == "__main__":
    app.run(debug=True)


