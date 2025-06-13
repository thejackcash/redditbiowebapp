import os
import random
import json
from flask import Flask, request, render_template, send_file
from openai import OpenAI

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

with open("telegram.json", "r") as f:
    model_handles = json.load(f)

client = OpenAI(api_key=OPENAI_API_KEY)

CTA_OPTIONS = [
    "tele 👉", "tg:", "telegram:", "teleme:", "telegrm:", "tele.", "teleg:", "tele📥:"
]

def obfuscate(handle):
    return ''.join(random.choice((c.upper(), c.lower())) for c in handle)

def generate_bio(model: str, city: str) -> str:
    handle = model_handles.get(model.lower())
    if not handle:
        return "❌ Model not found in telegram.json."

    cta = random.choice(CTA_OPTIONS)
    obfuscated_handle = obfuscate(handle)

    prompt = (
        f"You are an AI that writes long-form Tinder bios designed to drive traffic to the middle of the profile,\n"
        f"where the Telegram prompt is placed.\n\n"
        f"The model you’re writing for is: {model}, a flirtatious and friendly girl from {city}.\n"
        f"Your goal is to generate a bio that:\n"
        f"- Sounds like a real girl texting her thoughts\n"
        f"- Is between 425–475 characters\n"
        f"- Uses lowercase and emotional hooks\n"
        f"- Guides the reader toward the Telegram handle\n"
        f"- Ends with something like: {cta};{obfuscated_handle}\n\n"
        f"Important: Do not mention OnlyFans. Write casually with human imperfections.\n\n"
        f"Now write the bio:"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        model = request.form.get("model")
        city = request.form.get("city")
        if not model or not city:
            return "Missing model or city", 400
        bio = generate_bio(model, city)
        output_path = "generated_bio.txt"
        with open(output_path, "w") as f:
            f.write(bio)
        return send_file(output_path, as_attachment=True)
    return render_template("form.html")

if __name__ == "__main__":
    app.run(debug=True)
