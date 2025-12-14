from flask import Flask, render_template, request, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import os
import traceback
import json
import uuid

app = Flask(__name__)


CARPETA_CARNETS = "static/carnets"
os.makedirs(CARPETA_CARNETS, exist_ok=True)

TOKENS_FILE = "tokens.json"
if not os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, "w") as f:
        json.dump([], f)


@app.route("/")
def index():
    return "<h2>Por favor, usa el link único que te fue enviado.</h2>"

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
    return f"Link único:<br><br><a href='{link}' target='_blank'>{link}</a>"

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


        encontrado["usado"] = True
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f, indent=4)

      
        nombre = request.form.get("nombre", "").strip()
        documento = request.form.get("documento", "").strip()
        cargo = request.form.get("cargo", "").strip()

        if not (nombre and documento and cargo):
            return "Faltan campos (nombre, documento o cargo).", 400

  
       
        plantilla_path = "static/fotos/plantilla.jpg"

        print("Cargando plantilla desde:", os.path.abspath(plantilla_path))

        if not os.path.exists(plantilla_path):
            return f"NO EXISTE LA PLANTILLA EN: {plantilla_path}", 500

        carnet = Image.open(plantilla_path).convert("RGBA")
        draw = ImageDraw.Draw(carnet)

        
       
        
        try:
            font_texto = ImageFont.truetype("arial.ttf", 48)
        except:
            font_texto = ImageFont.load_default()

        color_texto = (20, 60, 20)

        
      
        
        x = 350
        y = 350

        draw.text((x, y), f"Nombre: {nombre}", font=font_texto, fill=color_texto)
        draw.text((x, y + 90), f"Documento: {documento}", font=font_texto, fill=color_texto)
        draw.text((x, y + 180), f"Cargo: {cargo}", font=font_texto, fill=color_texto)

    
    
        nombre_archivo = f"carnet_{documento}.png"
        ruta = os.path.join(CARPETA_CARNETS, nombre_archivo)
        carnet.save(ruta)

        return f"Carnet generado: <a href='/carnet/{nombre_archivo}' target='_blank'>VER CARNET</a>"

    except Exception:
        return f"<h2>ERROR:</h2><pre>{traceback.format_exc()}</pre>"



@app.route("/carnet/<filename>")
def carnet(filename):
    return send_from_directory(CARPETA_CARNETS, filename)

if __name__ == "__main__":
    app.run()

