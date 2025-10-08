# ClipGen

<div align="center">
   <img src="screenshots/clipgen-logo.png" alt="ClipGen Logo" width="200"/>
   <p><em>AI-powered clipboard enhancement utility with hotkeys for instant text correction, translation, rewriting, and image analysis using Google Gemini API.</em></p>
</div>

## 🚀 Overview

ClipGen is a powerful desktop utility that transforms how you interact with text and images on your computer. Using the Google Gemini API, ClipGen performs instant AI-powered operations on your clipboard content with simple hotkeys.

**Speed is our priority** - ClipGen processes short texts in under 0.5 seconds and longer texts in just seconds, making it feel like a native part of your operating system rather than an external tool.

![ClipGen in action](screenshots/clipgen-demo.gif)
**[Download ClipGen here](http://vetaone.site/ClipGen/ClipGen.zip)**  
*Important: Don’t forget to replace the API key in the `settings.json` configuration file with your own! You can get a free API key at [Google AI Studio](https://aistudio.google.com/u/0/apikey).*

## 💰 Completely FREE to Use!

ClipGen uses Google's **models/gemini-2.0-flash-exp** model, which comes with **1,000 FREE requests per day** on the Google Gemini API! This means:

- ✅ **No subscription fees**
- ✅ **No usage charges**
- ✅ **No credit card required**
- ✅ **Powerful AI completely free**

With 1,000 daily requests, you can process hundreds of texts and extract information from images without paying a cent. The model offers an excellent balance of intelligence and speed, enabling all of ClipGen's powerful features at zero cost.

## ✨ Features

- 🆓 **Completely free** - 1,000 requests per day at no cost
- 🔄 **Ultra-fast processing** - Get results for short texts in milliseconds and longer texts in seconds
- ⌨️ **Hotkey-driven workflow** - No need to switch applications
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
  - Image analysis, text extraction, and explanation
  - Custom requests
  - Humorous commentary generation - fully customizable prompts to match your style

## 📸 Screenshots

### Main Interface
![Main Interface](screenshots/main-interface.png)

### Grammar Correction Example
![Grammar Correction](screenshots/correction-example.png)

### Image Analysis Example
![Image Analysis](screenshots/image-analysis.png)

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Windows OS (currently Windows-only)
- Google Gemini API key (free to obtain)

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

3. **Get a FREE Google Gemini API key**
   - Visit [Google AI Studio](https://aistudio.google.com/u/0/apikey) directly
   - Create a new API key (no credit card required)
   - Copy your API key
   - You'll get 1,000 free requests per day with this key!

4. **Configure ClipGen**
   - Open `settings.json` in a text editor.
   - Replace the placeholder API key with your own:
     ```json
     {
         "api_key": "YOUR_API_KEY_HERE"
     }
     ```

5. **Run the application**
   ```
   python ClipGen.py
   ```

## 📋 Requirements

Create a file named `requirements.txt` with the following content:

```
pillow
pyperclip
google-generativeai
pywin32
pynput
PyQt5
```

## 🔥 How to Use

1. **Start ClipGen** - Run the application. It will minimize to the system tray.
2. **Toggle Window** - Use the global hotkey (`Ctrl+Shift+C` by default) or click the tray icon to show/hide the window.
3. **Select content** - For text, just select it (no need to copy); for images, take a screenshot or copy the image to clipboard.
4. **Use hotkeys** - Press the appropriate hotkey to perform an action.
5. **See results** - The processed content is automatically pasted back.

### Hotkey Reference

| Hotkey | Function | Description |
|--------|----------|-------------|
| Ctrl+Shift+C (default) | Show/Hide Window | Toggles the visibility of the main application window |
| Ctrl+F1 | Correction | Fixes grammar, punctuation, and spelling |
| Ctrl+F2 | Rewrite | Improves text clarity and readability |
| Ctrl+F3 | Translation | Translates text between any of 140+ languages |
| Ctrl+F6 | Explanation | Explains complex concepts in simple terms |
| Ctrl+F7 | Answer | Answers questions in the clipboard |
| Ctrl+F8 | Custom Request | Performs the specified task |
| Ctrl+F9 | Comment | Generates humorous comments |
| Ctrl+F10 | Image Analysis | Analyzes images, extracts text, and explains content |

## 💡 Use Cases

- **Writers/Editors**: Instantly polish sentences without switching to grammar tools
- **Multilingual Communication**: Quickly translate messages between any languages
- **Students**: Get explanations for complex terms or concepts
- **Developers**: Clean up error messages or extract text from screenshots
- **Social Media**: Understand memes or images when context is unclear
- **Everyday Use**: Fix typos in any text field across applications

## ⚙️ Customization

You can customize ClipGen extensively by editing the `settings.json` file:

```json
{
    "api_key": "YOUR_API_KEY_HERE",
    "autostart": false,
    "show_hide_hotkey": "Ctrl+Shift+C",
    "font_size": 10,
    "hotkeys": [
        {
            "combination": "Ctrl+F1",
            "name": "Correction",
            "log_color": "#FFFFFF",
            "prompt": "Please correct the following text..."
        },
        ...
    ]
}
```

Each aspect can be customized:
- `autostart`: Set to `true` to make ClipGen launch when Windows starts.
- `show_hide_hotkey`: The global hotkey to show or hide the application window.
- `font_size`: The font size for the log text area.
- `hotkeys`: Customize the AI actions:
  - `combination`: The keyboard shortcut.
  - `name`: Display name in the UI.
  - `log_color`: Color in the application log.
  - `prompt`: The instruction sent to Gemini AI.

## 🚀 Why ClipGen?

ClipGen transforms your computer workflow by eliminating context-switching. Instead of:

1. Writing text in one application
2. Opening a grammar tool or translator in another window
3. Copying text to the new tool
4. Waiting for processing
5. Copying the result
6. Switching back to your original application
7. Pasting the result

With ClipGen, the process becomes:
1. Write text in any application
2. Press a hotkey
3. Continue working with corrected text

This seamless integration creates a new computing experience where AI assistance feels like a natural extension of your keyboard.

## 🧠 About the AI Model

ClipGen uses the powerful **models/gemini-2.0-flash-exp** model from Google, which offers:

- **Fast response times** - Perfect for real-time text processing
- **High accuracy** - Excellent results for grammar, translation, and analysis tasks
- **Multimodal capabilities** - Analyzes both text and images effortlessly
- **1,000 free API calls daily** - More than enough for personal and professional use

## 🔒 Privacy

ClipGen processes text locally and only sends content to Google Gemini API when a hotkey is pressed. No data is stored or logged beyond the current session.

## 📅 In the plans
- Add macOS and Linux support.
- Expand functionality to work with other APIs.
- Improve the interface and add hotkey settings.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 About the Author

**Vitalii Kalistratov**
- Website: [vetaone.site](https://vetaone.site)
- If you'd like to support this project or say thanks:
  - USDT TRC20: `TEJw2gRrW5Z6Drowk7icjp5DhZvAEPwCYY`

## 🙏 Acknowledgements

- [Google Generative AI](https://github.com/google/generative-ai-python) for the Gemini API and free tier access
- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) for the UI components