from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from stegano_service import encode_message, decode_message

app = Flask(__name__)

# Dossier pour stocker les images téléchargées et générées
UPLOAD_FOLDER = "static/uploads"
ENCODED_FOLDER = "static/encoded"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCODED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ENCODED_FOLDER"] = ENCODED_FOLDER


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/encode", methods=["POST"])
def encode():
    if "image" not in request.files or not request.form.get("message"):
        return render_template("index.html", error="Veuillez sélectionner une image et entrer un message.")
    
    image = request.files["image"]
    message = request.form["message"]

    # Sauvegarder l'image téléchargée
    original_image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(original_image_path)

    # Générer le chemin de l'image encodée
    encoded_image_path = os.path.join(app.config["ENCODED_FOLDER"], f"encoded_{image.filename}")

    try:
        # Encoder le message dans l'image
        encode_message(original_image_path, message, encoded_image_path)
        image_path = url_for("static", filename=f"encoded/encoded_{image.filename}")
        return render_template("index.html", image_path=image_path)
    except ValueError as e:
        return render_template("index.html", error=str(e))


@app.route("/decode", methods=["POST"])
def decode():
    if "image" not in request.files:
        return render_template("index.html", error="Veuillez sélectionner une image.")
    
    image = request.files["image"]

    # Sauvegarder l'image téléchargée
    encoded_image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(encoded_image_path)

    try:
        # Décoder le message depuis l'image
        message = decode_message(encoded_image_path)
        return render_template("index.html", decoded_message=message)
    except ValueError as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True)
