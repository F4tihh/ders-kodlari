from flask import Flask, request, render_template
import qrcode
import os
import string
import random

app = Flask(__name__)

# -----------------------------
#  BURAYA KENDİ BİLGİSAYAR IP ADRESİNİ YAZ
#  ÖRNEK: 192.168.1.35
#  cmd'de "ipconfig" ile IPv4 Address değerine bakılır.
# -----------------------------
BASE_URL = "http://192.168.1.198:5000"  # ← BUNU KENDİ IP'N İLE DEĞİŞTİR


# Basit RAM içi "veritabanı" (MVP için yeterli)
DATABASE = {}


def generate_token(length=6):
    """Rastgele 6 karakterlik token üretir."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@app.route("/", methods=["GET", "POST"])
def create_qr():
    """
    GET  → Formu gösterir.
    POST → Formdan gelen video_url + message ile token üretir,
            QR oluşturur ve aynı sayfada gösterir.
    """
    if request.method == "POST":
        video_url = request.form["video_url"]
        message = request.form["message"]

        # Token üret ve RAM içi DB'ye kaydet
        token = generate_token()
        DATABASE[token] = {"video_url": video_url, "message": message}

        # QR içine yazılacak olan URL
        qr_data = f"{BASE_URL}/v/{token}"

        # static klasörünü garantiye al
        os.makedirs("static", exist_ok=True)

        # QR resmi üret ve static içine kaydet
        img = qrcode.make(qr_data)
        qr_path = f"static/{token}.png"
        img.save(qr_path)

        # create.html'e token, qr_path ve qr_data'yı gönder
        return render_template("create.html", token=token, qr_path=qr_path, qr_data=qr_data)

    # İlk girişte sadece form gözüksün
    return render_template("create.html", token=None)


@app.route("/v/<token>")
def view(token):
    """
    QR içindeki /v/<token> adresine gelindiğinde:
    - token DB'de varsa ilgili video + mesajı getir
    - view.html ile kullanıcıya göster
    """
    if token not in DATABASE:
        return "QR geçersiz veya süresi dolmuş", 404

    data = DATABASE[token]
    return render_template("view.html", video_url=data["video_url"], message=data["message"])


if __name__ == "__main__":
    # host="0.0.0.0" → Aynı ağdaki telefon vb. cihazlar da erişebilsin
    app.run(host="0.0.0.0", debug=True)
