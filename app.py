from flask import Flask, request, render_template
import qrcode
import os
import string
import random

app = Flask(__name__)

# Basit bir hafıza veritabanı (şimdilik RAM üzerinde)
DATABASE = {}

def generate_token(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@app.route("/", methods=["GET", "POST"])
def create_qr():
    if request.method == "POST":
        video_url = request.form["video_url"]
        message = request.form["message"]

        token = generate_token()
        DATABASE[token] = {"video_url": video_url, "message": message}

        # QR içeriği
        qr_data = f"http://localhost:5000/v/{token}"

        # QR oluşturma
        img = qrcode.make(qr_data)
        os.makedirs("static", exist_ok=True)
        qr_path = f"static/{token}.png"
        img.save(qr_path)

        return render_template("create.html", token=token, qr_path=qr_path, qr_data=qr_data)

    return render_template("create.html", token=None)
    

@app.route("/v/<token>")
def view(token):
    if token not in DATABASE:
        return "QR geçersiz veya süresi dolmuş", 404

    data = DATABASE[token]
    return render_template("view.html", video_url=data["video_url"], message=data["message"])


if __name__ == "__main__":
    app.run(debug=True)
