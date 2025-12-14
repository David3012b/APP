from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

# ================= CONFIG =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PLANTILLA = os.path.join(BASE_DIR, "static", "plantilla.png")
FONT_PATH = os.path.join(BASE_DIR, "static", "Montserrat-Regular.ttf")
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "carnets")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Tamaño final del carnet (clave)
CARNET_WIDTH = 2000
CARNET_HEIGHT = 1200
# ==========================================


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form["nombre"]
        documento = request.form["documento"]
        cargo = request.form["cargo"]

        # Abrir y REDIMENSIONAR plantilla
        img = Image.open(PLANTILLA).convert("RGB")
        img = img.resize((CARNET_WIDTH, CARNET_HEIGHT))

        draw = ImageDraw.Draw(img)

        # FUENTES (AHORA SÍ FUNCIONA)
        font_nombre = ImageFont.truetype(FONT_PATH, 120)
        font_datos = ImageFont.truetype(FONT_PATH, 85)

        color = (40, 80, 45)

        # Posiciones
        x = 750
        y = 450

        draw.text((x, y), f"Nombre: {nombre}", fill=color, font=font_nombre)
        draw.text((x, y + 170), f"Documento: {documento}", fill=color, font=font_datos)
        draw.text((x, y + 290), f"Cargo: {cargo}", fill=color, font=font_datos)

        # Guardar carnet
        output_path = os.path.join(OUTPUT_DIR, f"{documento}.png")
        img.save(output_path)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)


