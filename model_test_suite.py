import os
import json
import csv
import base64
import time
from datetime import datetime
import google.generativeai as genai
from mistralai import Mistral
from groq import Groq
from PIL import Image

# --- Konfiguration ---
SETTINGS_FILE = "settings.json"
IMAGE_PATH = "test_images/image.png"
PROMPT = "Extrahiere den gesamten Text aus diesem Bild. Gib ausschließlich den transkribierten Text zurück, ohne zusätzliche Kommentare oder Formatierungen."
CSV_OUTPUT_FILE = "model_test_results.csv"
REQUEST_PAUSE_SECONDS = 2

# --- Hilfsfunktionen ---

def load_api_keys():
    """Lädt die API-Schlüssel aus der Einstellungsdatei."""
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            return {
                "gemini": config.get("gemini_api_key"),
                "mistral": config.get("mistral_api_key"),
                "groq": config.get("groq_api_key"),
            }
    except FileNotFoundError:
        print(f"FEHLER: Die Einstellungsdatei '{SETTINGS_FILE}' wurde nicht gefunden.")
        return None

def encode_image_to_base64(image_path):
    """Kodiert ein Bild in einen Base64-String."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"FEHLER: Die Bilddatei '{image_path}' wurde nicht gefunden.")
        return None

def write_to_csv(writer, provider, model, prompt, response):
    """Schreibt eine Ergebniszeile in die CSV-Datei."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_prompt = f"{prompt} (Bild: {os.path.basename(IMAGE_PATH)})"
    cleaned_response = ' '.join(str(response).splitlines())
    writer.writerow([timestamp, provider, model, full_prompt, cleaned_response])
    print(f"  - Ergebnis für {model} gespeichert.")

# --- Hauptlogik ---

def main():
    """Führt den Modell-Test-Suite aus."""
    print("Starte den Modell-Test-Suite...")

    api_keys = load_api_keys()
    if not api_keys:
        return

    with open(CSV_OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Zeitstempel", "Anbieter", "Modell", "Prompt", "Antwort"])

        # --- Gemini-Tests ---
        print("\n--- Teste Gemini-Modelle ---")
        gemini_api_key = api_keys.get("gemini")
        if not gemini_api_key or "YOUR_API_KEY_HERE" in gemini_api_key:
            print("WARNUNG: Gemini API-Schlüssel nicht konfiguriert. Überspringe Tests.")
        else:
            try:
                genai.configure(api_key=gemini_api_key)
                gemini_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                image = Image.open(IMAGE_PATH)

                for model_info in gemini_models:
                    model_name = model_info.name
                    print(f"Teste Modell: {model_name}...")
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content([PROMPT, image])
                        result = response.text.strip()
                    except Exception as e:
                        result = f"FEHLER: {e}"
                    write_to_csv(csv_writer, "Gemini", model_name, PROMPT, result)
                    time.sleep(REQUEST_PAUSE_SECONDS)
            except Exception as e:
                print(f"FEHLER bei der Initialisierung von Gemini: {e}")

        # --- Mistral-Tests ---
        print("\n--- Teste Mistral-Modelle ---")
        mistral_api_key = api_keys.get("mistral")
        if not mistral_api_key or "YOUR_API_KEY_HERE" in mistral_api_key:
            print("WARNUNG: Mistral API-Schlüssel nicht konfiguriert. Überspringe Tests.")
        else:
            try:
                mistral_client = Mistral(api_key=mistral_api_key)
                base64_image = encode_image_to_base64(IMAGE_PATH)
                mistral_models = mistral_client.models.list()

                for model_info in mistral_models.data:
                    model_name = model_info.id
                    print(f"Teste Modell: {model_name}...")
                    try:
                        # Korrekter Aufbau für Anfragen an die Mistral-API
                        messages = [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": PROMPT},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                            ]
                        }]
                        response = mistral_client.chat(model=model_name, messages=messages)
                        result = response.choices[0].message.content.strip()
                    except Exception as e:
                        result = f"FEHLER: {e}"
                    write_to_csv(csv_writer, "Mistral", model_name, PROMPT, result)
                    time.sleep(REQUEST_PAUSE_SECONDS)
            except Exception as e:
                print(f"FEHLER bei der Initialisierung von Mistral: {e}")

        # --- Groq-Tests ---
        print("\n--- Teste Groq-Modelle ---")
        groq_api_key = api_keys.get("groq")
        if not groq_api_key or "YOUR_API_KEY_HERE" in groq_api_key:
            print("WARNUNG: Groq API-Schlüssel nicht konfiguriert. Überspringe Tests.")
        else:
            try:
                groq_client = Groq(api_key=groq_api_key)
                base64_image = encode_image_to_base64(IMAGE_PATH)

                if base64_image:
                    groq_models = groq_client.models.list()

                    for model_info in groq_models.data:
                        model_name = model_info.id
                        print(f"Teste Modell: {model_name}...")
                        try:
                            chat_completion = groq_client.chat.completions.create(
                                messages=[{
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": PROMPT},
                                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                                    ],
                                }],
                                model=model_name,
                            )
                            result = chat_completion.choices[0].message.content.strip()
                        except Exception as e:
                            result = f"FEHLER: {e}"
                        write_to_csv(csv_writer, "Groq", model_name, PROMPT, result)
                        time.sleep(REQUEST_PAUSE_SECONDS)
            except Exception as e:
                print(f"FEHLER bei der Initialisierung von Groq: {e}")

    print(f"\nTest-Suite abgeschlossen. Ergebnisse wurden in '{CSV_OUTPUT_FILE}' gespeichert.")

if __name__ == "__main__":
    main()
