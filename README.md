

📟 BMO: The Raspberry Pi AI Companion
BMO is a multi-functional, privacy-focused AI companion designed to run locally on a Raspberry Pi 5. It combines LLM-based conversation, computer vision for security, and hardware monitoring into a single child-like personality (inspired by Adventure Time).
✨ Key Features
🤖 Local-First AI: Uses Ollama (Llama 3.2 & Moondream) to chat and describe surroundings without sending data to the cloud.
🛡️ Face-ID Security: Recognizes the owner and enters an "Intruder Alert" mode if a stranger is detected.
📸 Vision: Describe what BMO sees in real-time using the Pi Camera.
🌡️ System Health: Check your Pi's CPU temperature, RAM usage, and vitals via Telegram.
🌐 Bilingual: Native support for English and Vietnamese.
🎨 Modular Personality: Easily swap between a "child-like," "professional," or "sarcastic" BMO via the config file.

🛠️ Prerequisites
Hardware: Raspberry Pi 5 (Recommended) or Pi 4 (8GB), Camera Module (v2 or v3).
Ollama: Must be installed and running on your Pi.
ollama pull llama3.2:3b
ollama pull moondream
Libraries: libcamera and python3-picamera2 installed via apt.

🚀 Installation
1. Clone the Repository
Bash
git clone https://github.com/YOUR_USERNAME/BMO-AI-Companion.git
cd BMO-AI-Companion


2. Set Up the Hybrid Environment
Since this project interacts with physical hardware, we use a virtual environment that bridges to system-site packages to access the camera drivers.
Bash
# Create the bridge environment
python -m venv --system-site-packages venv

# Activate it
source venv/bin/activate

# Install high-level dependencies
pip install python-telegram-bot ollama python-dotenv face_recognition psutil


3. Configuration (The "Secrets")
Rename .env.example to .env.
Add your Telegram Bot Token and Admin Chat ID (use @userinfobot on Telegram to find yours).
Add a photo of yourself named admin.jpg in the root folder for face recognition.

⚙️ Customization
BMO’s soul lives in config.py. You can change the SYSTEM_PROMPT to redefine his personality without touching the core logic:
Python
# config.py example
SYSTEM_PROMPT = "You are BMO. You are playful, imaginative, and speak in short, cute sentences."



📟 Telegram Commands
Command
Description
/start
Wake up BMO.
/look
BMO uses the camera to describe the room.
/patrol
Starts security mode (Face-ID).
/status
Shows Pi CPU Temp and RAM.
/language
Toggle between English/Vietnamese.
/joke
BMO tells a tech-themed joke.
/reset
Clear BMO's short-term memory.


🛡️ Security Note
This project uses a .env file to store sensitive credentials. Never commit your .env file to GitHub. The .gitignore included in this repo is pre-configured to keep your tokens safe.

🤝 Contributing
Feel free to fork this project! If you have ideas for new BMO "apps" or personality modules, please submit a Pull Request.

📜 License
MIT License - See LICENSE for details.



