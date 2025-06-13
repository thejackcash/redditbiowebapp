import os
import random
import json
from flask import Flask, request, send_file
from openai import OpenAI

app = Flask(__name__)

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Load telegram.json mapping
with open("telegram.json", "r") as f:
    model_handles = json.load(f)

# Initialize OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

CTA_OPTIONS = [
    "tele 👉", "tg:", "telegram:", "teleme:", "telegrm:", "tele.", "teleg:", "tele📥:"
]

def obfuscate(handle):
    return ''.join(random.choice((c.upper(), c.lower())) for c in handle)

def generate_bio(model, city):
    handle = model_handles.get(model.lower())
    if not handle:
        return "❌ Model not found in telegram.json."

    cta = random.choice(CTA_OPTIONS)
    obfuscated = obfuscate(handle)

    prompt = (
        f"You are an AI that writes long-form Tinder bios designed to drive traffic to the middle of the profile,\n"
        f"where the Telegram prompt is placed.\n\n"
        f"The model you’re writing for is: {model}, a flirtatious and friendly girl from {city}.\n"
        f"Your goal is to generate a bio that:\n"
        f"- Sounds like a real girl texting her thoughts\n"
        f"- Is between 425–475 characters\n"
        f"- Uses lowercase and emotional hooks\n"
        f"- Guides the reader toward the Telegram handle\n"
        f"- Ends with something like: {cta};{obfuscated}\n\n"
        f"Important: Do not mention OnlyFans. Write casually with human imperfections.\n\n"
        f"Now write the bio:"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route("/", methods=["GET"])
def form():
    return """
    <form method="post" action="/generate">
        <input name="model" placeholder="Model Name" required>
        <input name="city" placeholder="City" required>
        <button type="submit">Generate</button>
    </form>
    """

@app.route("/generate", methods=["POST"])
def handle_generate():
    model = request.form.get("model", "")
    city = request.form.get("city", "")
    bio = generate_bio(model, city)

    with open("generated_bio.txt", "w", encoding="utf-8") as f:
        f.write(bio)

    return send_file("generated_bio.txt", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
