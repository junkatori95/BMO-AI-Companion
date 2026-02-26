# BMO-AI-Companion 📟

BMO is a multi-modal AI assistant powered by a Raspberry Pi 5. It uses Ollama for high-level reasoning and vision, paired with a custom security patrol mode and facial recognition.

## ✨ Features
* **Vision:** Uses `Moondream` to describe surroundings and identify objects via the Pi Camera.
* **Chat:** Powered by `Llama 3.2 3b` for a witty, child-like personality.
* **Security:** Face recognition identifies authorized users (admin) or sounds an intruder alert.
* **Bilingual:** Toggle between English and Vietnamese seamlessly.
* **System Monitor:** Real-time tracking of Pi 5 temperature, CPU, and RAM usage.

## 🛠️ Hardware Requirements
* Raspberry Pi 5 (8GB recommended)
* Raspberry Pi Camera Module (v3 or compatible)
* Active Cooling (Fan) is highly recommended for AI workloads

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/BMO-AI-Companion.git](https://github.com/YOUR_USERNAME/BMO-AI-Companion.git)
   cd BMO-AI-Companion

```

2. **Create a Virtual Environment:**
```bash
python -m venv venv
source venv/bin/activate

```


3. **Configure Environment Variables:**
Create a `.env` file in the root directory to store your secrets safely:
```text
TELEGRAM_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id

```


4. **Add Authorized Face:**
Place a clear photo of your face named `admin.jpg` in the root folder for the security module.

## ⚠️ Troubleshooting (Raspberry Pi 5 Specifics)

### 1. The `dlib` / `face_recognition` Installation

Installing `face_recognition` on a Pi 5 requires compiling `dlib`, which is resource-heavy. If the installation crashes or hangs:

**Solution:** Install system dependencies first, then use the low-memory flag:

```bash
sudo apt update
sudo apt install -y cmake build-essential libopenblas-dev liblapack-dev libjpeg-dev
pip install --no-cache-dir dlib
pip install face_recognition

```

### 2. `ValueError: numpy.dtype size changed`

This occurs due to a conflict between Numpy 2.0 and the Raspberry Pi's `picamera2` drivers.

**Solution:** Force a stable Numpy 1.x version:

```bash
pip uninstall -y numpy
pip install "numpy<2"

```

### 3. Missing Dependencies

Install the remaining BMO tools:

```bash
pip install python-telegram-bot python-dotenv ollama opencv-python-headless psutil

```

## 🚀 Running BMO

Ensure your virtual environment is active and run:

```bash
python bmo.py

```

## 🛡️ Security Note

The `.env` file and `admin.jpg` are listed in the `.gitignore` to prevent your private credentials and biometric data from being published to GitHub. **Never share your `.env` file.**

```

---

### Final Check for GitHub
Before you push, ensure your `.gitignore` file contains these lines to match the README's security promise:

```text
.env
venv/
__pycache__/
*.jpg
*.png


