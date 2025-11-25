import os
from dotenv import load_dotenv
import google.generativeai as genai

# .env-Datei laden
load_dotenv()

API_KEY = os.getenv("Gemini_api_key")
if not API_KEY:
    print("Fehler: Gemini API-Schlüssel in .env nicht konfiguriert")
    exit(1)

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.0-flash"

def image_to_text(image_path: str) -> str:
    """Konvertiert Bildtext zu Text mittels Gemini API"""
    model = genai.GenerativeModel(MODEL_NAME)

    with open(image_path, "rb") as f:
        img_data = f.read()

    response = model.generate_content(
        [
            {"mime_type": "image/png", "data": img_data},
            "Lies NUR den Text im Bild aus und gib ihn als reinen Text zurück in folgenden Format: !!! Dein erkannter Text: <Text>"
        ]
    )

    return response.text

if __name__ == "__main__":
    screenshot_path = "test_images/image.png"
    text = image_to_text(screenshot_path)
    print(text)
