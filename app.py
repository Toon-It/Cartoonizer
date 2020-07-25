import os
from flask import Flask, render_template, request

app = Flask(__name__)
UPLOAD_FOLDER = "static/upload/"
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        image_file = request.files["image"]
        if image_file:
            image_location = os.path.join(UPLOAD_FOLDER, image_file.filename)
            image_file.save(image_location)
            return render_template('toon_it.html', predictions=1)
    return render_template('toon_it.html', predictions=0)

if __name__ == "__main__":
    app.run(port=1200,debug=True)
