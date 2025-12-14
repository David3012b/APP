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
CARPETA_FUENTES = os.path.join(BASE_DIR, "static", "fonts")
CARPETA_FOTOS = os.path.join(BASE_DIR, "static", "fotos")

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
    return "<h2>Servidor funcionando</h2>"

@app.route("/crear_link")
def crear_link():
    token = str(uuid.uuid4())

    with open(TOKENS_FILE, "r") as f:
        tokens = json.load(f)

    tokens.append({"token": token, "usado": False})

    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=4)

    link = f"{request.host_url}form/{token}"
    return f"<a href='{link}' target='_blank'>{link}</a>"

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
    try:
        token = request.form.get("token")

        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)

        encontrado = next((t for t in tokens if t["token"] == token), None)

        if not encontrado or encontrado["usado"]:
            return "Token inválido o usado", 403

        encontrado["usado"] = True
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f, indent=4)

        nombre = request.form["nombre"].strip()
        documento = request.form["documento"].strip()
        cargo = request.form["cargo"].strip()

        plantilla = Image.open(
            os.path.join(CARPETA_FOTOS, "plantilla.jpg")
        ).convert("RGBA")

        draw = ImageDraw.Draw(plantilla)

        # =====================
        # FUENTE REAL
        # =====================
        font_path = os.path.join(CARPETA_FUENTES, "Montserrat-Bold.ttf")
        font_nombre = ImageFont.truetype(font_path, 80)
        font_datos = ImageFont.truetype(font_path, 60)

        color = (20, 60, 20)

        # =====================
        # POSICIONES (AJUSTA A TU PLANTILLA)
        # =====================
        draw.text((350, 350), nombre, font=font_nombre, fill=color)
        draw.text((350, 450), f"Documento: {documento}", font=font_datos, fill=color)
        draw.text((350, 530), f"Cargo: {cargo}", font=font_datos, fill=color)

        nombre_archivo = f"carnet_{documento}.png"
        ruta = os.path.join(CARPETA_CARNETS, nombre_archivo)
        plantilla.save(ruta)

        return f"<a href='/carnet/{nombre_archivo}' target='_blank'>VER CARNET</a>"

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"

@app.route("/carnet/<filename>")
def carnet(filename):
    return send_from_directory(CARPETA_CARNETS, filename)

if __name__ == "__main__":
    app.run(debug=True)
