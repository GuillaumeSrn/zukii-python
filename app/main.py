from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route("/analyse", methods=["POST"])
def analyse_csv():
    file = request.files["file"]
    df = pd.read_csv(file)
    # Exemple d'analyse simple
    summary = df.describe().to_dict()
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
