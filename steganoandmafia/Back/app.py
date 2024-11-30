import os
from flask import Flask, request, render_template, send_from_directory, url_for
from stegano_service import encode_message, decode_message, encrypt_message, decrypt_message, generate_key
from itsdangerous import URLSafeTimedSerializer, BadData

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
ENCODED_FOLDER = "encoded"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ENCODED_FOLDER"] = ENCODED_FOLDER
app.secret_key = "supersecretkey"  # Remplacez par une clé sécurisée
serializer = URLSafeTimedSerializer(app.secret_key)

# Créez les dossiers nécessaires
# madam jai utiliser chat gpt dsl
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCODED_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("welcomepage.html")

@app.route("/hide_message")
def HideMessage():
    return render_template('hide_message.html')

@app.route("/faq")
def Faq():
    return render_template('faq.html')

@app.route("/extract_message")
def ExtractMessage():
    return render_template('extract_message.html')

@app.route("/encode", methods=["POST"])
def encode():
    if "image" not in request.files or not request.form.get("message") or not request.form.get("encryption_type"):
        return render_template("hide_message.html", error="Veuillez remplir tous les champs du formulaire.")

    image = request.files["image"]
    if image.filename == '':
        return render_template("hide_message.html", error="Veuillez sélectionner une image.")
    
    message = request.form["message"]
    encryption_type = request.form["encryption_type"]

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(image_path)

    try:
        key = generate_key(encryption_type)
        encrypted_message = encrypt_message(message, key)
        encoded_image_path = encode_message(image_path, encrypted_message)

        final_encoded_path = os.path.join(app.config["ENCODED_FOLDER"], os.path.basename(encoded_image_path))
        os.rename(encoded_image_path, final_encoded_path)

        encoded_image_url = url_for("download_file", filename=os.path.basename(final_encoded_path))

        return render_template(
            "operation_succ.html",
            encoded_image=encoded_image_url,
            generated_key=key.hex(),
            share_link=url_for("generate_temporary_link", filename=os.path.basename(final_encoded_path), _external=True)
        )
    except ValueError as e:
        return render_template("hide_message.html", error=str(e))

@app.route("/decode", methods=["POST"])
def decode():
    if "image" not in request.files or not request.form.get("key"):
        return render_template("extract_message.html", error="Veuillez remplir tous les champs du formulaire.")

    image = request.files["image"]
    if image.filename == '':
        return render_template("extract_message.html", error="Veuillez sélectionner une image.")
    
    key_hex = request.form["key"]
    key = bytes.fromhex(key_hex)

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(image_path)

    try:
        extracted_message = decode_message(image_path)
        decrypted_message = decrypt_message(extracted_message, key)

        return render_template("operation_succ.html", decoded_message=decrypted_message)
    except ValueError as e:
        return render_template("extract_message.html", error=str(e))

@app.route("/download/<filename>")
def download_file(filename):
    """Permet le téléchargement d'une image encodée."""
    return send_from_directory(app.config["ENCODED_FOLDER"], filename, as_attachment=True)

@app.route("/generate_temporary_link/<filename>", methods=["GET", "POST"])
def generate_temporary_link(filename):
    if request.method == "POST":
        password = request.form.get("password")
        if not password:
            return render_template("temporary_link.html", error="Veuillez fournir un mot de passe.", link=None)
        
        token = serializer.dumps({"filename": filename, "password": password})
        temporary_url = url_for("access_temporary_link", token=token, _external=True)
        return render_template("temporary_link.html", link=temporary_url)
    
    return render_template("temporary_link.html", link=None)

@app.route("/temporary_link/<token>", methods=["GET", "POST"])
def access_temporary_link(token):
    try:
        data = serializer.loads(token, max_age=86400)  # Valide pour 24 heures
        filename = data["filename"]
        stored_password = data["password"]
    except BadData:
        return render_template("index.html", error="Lien expiré ou invalide.")

    if request.method == "POST":
        password = request.form.get("password")
        if password != stored_password:
            return render_template("temporary_link.html", error="Mot de passe incorrect.", link=None)

        return send_from_directory(app.config["ENCODED_FOLDER"], filename, as_attachment=True)
    
    return render_template("temporary_link.html", link=None)

if __name__ == "__main__":
    app.run(debug=True)
