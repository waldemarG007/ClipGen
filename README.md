# ClipGen

<div align="center">
   <img src="screenshots/clipgen-logo.png" alt="ClipGen Logo" width="200"/>
   <p><em>Your AI-powered clipboard sidekick. Instant text correction, translation, and image analysis with your favorite AI models.</em></p>
</div>

## 🚀 Overview

ClipGen is a powerful desktop utility that transforms how you interact with text and images on your computer. By connecting to your favorite AI providers (including **Google Gemini**, **Groq**, **Mistral**, and local **Ollama** models), ClipGen performs instant AI-powered operations on your clipboard content with simple hotkeys.

**Speed is our priority** - ClipGen processes requests in seconds, making it feel like a native part of your operating system rather than an external tool.

![ClipGen in action](screenshots/clipgen-demo.gif)
**[Download ClipGen here](http://vetaone.site/ClipGen/ClipGen.zip)**  
*Important: Don’t forget to configure your API keys in the `settings.json` file!*

## ✨ Features

- 🔌 **Multi-API Support**: Choose your favorite AI provider!
  - **Google Gemini**: For powerful, free, multimodal analysis.
  - **Groq**: For blazing-fast text generation.
  - **Mistral AI**: For high-quality text models.
  - **Ollama**: To use your own local models for maximum privacy and customization.
- ⌨️ **Hotkey-driven workflow** - No need to switch applications.
- ⚙️ **System Tray Integration** - Runs quietly in the background.
- 🚀 **Autostart with Windows** - Launch ClipGen automatically on startup.
- 🖥️ **Global Show/Hide Hotkey** - Access the window from anywhere.
- ✏️ **Customizable Font Size** - Adjust the font size for better readability.
- 🧠 **AI-powered operations**:
  - Grammar, punctuation, and spelling correction
  - Text rewriting and improvement
  - Translation between any of 140+ world languages
  - Explanation of complex terms or concepts
  - Question answering based on clipboard content
  - Image analysis (with supported models like Gemini and Ollama)
  - Custom requests
  - Humorous commentary generation - fully customizable prompts to match your style

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Windows OS (currently Windows-only)

### Setup

1. **Clone the repository**
   ```
   git clone https://github.com/Veta-one/clipgen.git
   cd clipgen
   ```

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Configure ClipGen**
   - Run the application once to generate the `settings.json` file.
   - Open `settings.json` in a text editor.
   - In the settings UI, select your desired AI provider from the dropdown menu.
   - Fill in the required details (like API keys or model names) for your chosen provider.

### Running the Application and Autostart
For the application to work correctly, especially the autostart feature, please follow these steps:

1.  **Place the project folder in a permanent location.** Before running the application for the first time, move the entire `ClipGen` folder to a place where it will stay permanently. Good examples are `C:\Program Files\ClipGen` or `C:\Users\YourUser\Applications\ClipGen`.
    > **Warning:** Do not run the application from your `Downloads` folder if you intend to use the autostart feature, as it may be moved or deleted.

2.  **Run the application** by executing `ClipGen.py` from its new, permanent location.

3.  **Enable Autostart (Optional).** To have ClipGen start automatically with Windows:
    - Open the main window (by default with `Ctrl+Shift+C` or by clicking the tray icon).
    - Go to the "Settings" tab.
    - Check the box labeled **"Start with Windows"**.

The application registers its current path for autostart. If you move the folder *after* enabling this option, it will fail to start. You will need to go back to the settings, disable and then re-enable the autostart option to update the path.

## 📋 Requirements

The `requirements.txt` file contains all necessary dependencies:
```
PyQt5==5.15.9
pyperclip==1.9.0
google-generativeai==0.8.4
pywin32==310
pynput==1.8.0
Pillow==11.1.0
groq==0.9.0
mistralai==0.4.1
ollama==0.3.0
```

## 🔥 How to Use

1. **Start ClipGen** - Run the application. It will minimize to the system tray.
2. **Toggle Window** - Use the global hotkey (`Ctrl+Shift+C` by default) or click the tray icon to show/hide the window.
3. **Select content** - For text, just select it; for images, take a screenshot or copy the image to the clipboard.
4. **Use hotkeys** - Press the appropriate hotkey to perform an action.
5. **See results** - The processed content is automatically pasted back.

## ⚙️ Customization & AI Providers

You can customize ClipGen extensively by editing the `settings.json` file or through the UI.

### General Settings
- `provider`: The active AI provider (`gemini`, `groq`, `mistral`, `ollama`).
- `autostart`: Set to `true` to make ClipGen launch when Windows starts.
- `show_hide_hotkey`: The global hotkey to show or hide the application window.
- `font_size`: The font size for the log text area.

### Provider Settings
In the `providers` section, you can configure each service:
- **Gemini**:
  - `api_key`: Your Google AI Studio API key.
  - `model`: The model to use (e.g., `gemini-1.5-flash-latest`).
- **Groq**:
  - `api_key`: Your GroqCloud API key.
  - `model`: The model to use (e.g., `llama3-8b-8192`).
- **Mistral**:
  - `api_key`: Your Mistral AI API key.
  - `model`: The model to use (e.g., `mistral-small-latest`).
- **Ollama**:
  - `host`: The URL of your local Ollama server (e.g., `http://localhost:11434`).
  - `model`: The name of the local model you want to use (e.g., `llama3`).

### Hotkeys
Customize the AI actions in the `hotkeys` list:
- `combination`: The keyboard shortcut.
- `name`: Display name in the UI.
- `log_color`: Color in the application log.
- `prompt`: The instruction sent to the AI.

## 🚀 Why ClipGen?

ClipGen transforms your computer workflow by eliminating context-switching. Instead of copying and pasting between applications and websites, just select content, press a hotkey, and get the result instantly. This seamless integration creates a new computing experience where AI assistance feels like a natural extension of your keyboard.

## 🔒 Privacy

When using cloud-based providers (Gemini, Groq, Mistral), your clipboard content is sent to their servers for processing. When using **Ollama**, all processing happens on your local machine, and no data leaves your network. ClipGen itself does not store or log your data beyond the current session.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 About the Author

**Vitalii Kalistratov**
- Website: [vetaone.site](https://vetaone.site)
- If you'd like to support this project or say thanks:
  - USDT TRC20: `TEJw2gRrW5Z6Drowk7icjp5DhZvAEPwCYY`

## 🙏 Acknowledgements

- [Google Generative AI](https://github.com/google/generative-ai-python), [Groq](https://groq.com/), [Mistral AI](https://mistral.ai/), and [Ollama](https://ollama.com/) for their powerful APIs and models.
- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) for the UI components.