import asyncio
import psutil
import random
import face_recognition
import numpy as np
import os
from dotenv import load_dotenv
from ollama import AsyncClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from picamera2 import Picamera2

# --- BMO Configuration ---
# Load variables from the .env file in your folder
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else 0
picam2 = Picamera2()

# Model Selection
CHAT_MODEL = "llama3.2:3b"  # Updated from 1b to 3b
VISION_MODEL = "moondream"  # Optimized for Pi 5 vision

# Global States
patrolling = False
intruder_alert_active = False
chat_history = []
current_lang = "English" # Default language

# --- Load Face Recognition ---
try:
    # Specifically looking for admin.jpg as confirmed in your folder
    face_image_path = "admin.jpg"
    
    if not os.path.exists(face_image_path):
        raise FileNotFoundError(f"Could not find {face_image_path}")

    admin_image = face_recognition.load_image_file(face_image_path)
    admin_face_encoding = face_recognition.face_encodings(admin_image)[0]
    known_face_encodings = [admin_face_encoding]
    print(f"✅ BMO memory loaded: Authorized face detected from {face_image_path}")
except Exception as e:
    print(f"⚠️ Warning: Face recognition setup failed: {e}")
    known_face_encodings = []

def is_authorized(update: Update):
    return update.message.from_user.id == ADMIN_ID

# --- BMO Functions ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    msg = "BMO is awake! Ready for admin! 📟" if current_lang == "English" else "BMO đã thức dậy! Sẵn sàng phục vụ admin! 📟"
    await update.message.reply_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    if current_lang == "English":
        msg = ("📟 **BMO Help Menu**\n"
               "/start - Wake me up\n"
               "/status - Check my vitals\n"
               "/look - Let me see the room\n"
               "/patrol - Start security mode\n"
               "/joke - Hear a joke\n"
               "/language - Toggle EN/VN\n"
               "/reset - Clear my memory\n"
               "Or just talk to me!")
    else:
        msg = ("📟 **BMO Menu Trợ Giúp**\n"
               "/start - Đánh thức BMO\n"
               "/status - Kiểm tra thông số hệ thống\n"
               "/look - Xem căn phòng\n"
               "/patrol - Bật chế độ an ninh\n"
               "/joke - Nghe kể chuyện cười\n"
               "/language - Chuyển đổi Anh/Việt\n"
               "/reset - Xóa bộ nhớ\n"
               "Hoặc chỉ cần trò chuyện với BMO!")
    await update.message.reply_text(msg, parse_mode='Markdown')

async def look(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    wait_msg = "BMO is looking..." if current_lang == "English" else "BMO đang quan sát..."
    await update.message.reply_text(wait_msg)
   
    path = "bmo_vision.jpg"
    try:
        picam2.start()
        picam2.capture_file(path)
        picam2.stop()
       
        # Describe in the current language using the Vision-specific model
        prompt = f"Describe the room briefly and act like BMO. Respond in {current_lang}."
        with open(path, 'rb') as f:
            response = await AsyncClient().generate(model=VISION_MODEL, prompt=prompt, images=[f.read()])
       
        await update.message.reply_photo(photo=open(path, 'rb'), caption=f"✨ {response['response']}")
    except Exception as e:
        await update.message.reply_text(f"Vision error: {e}")

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    global current_lang
    if current_lang == "English":
        current_lang = "Vietnamese"
        await update.message.reply_text("Ngôn ngữ đã được chuyển sang tiếng Việt! 🇻🇳")
    else:
        current_lang = "English"
        await update.message.reply_text("Language switched to English! 🇺🇸")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = float(f.read()) / 1000.0
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
   
    if current_lang == "English":
        msg = f"🌡️ Temp: {temp:.1f}C\n🧠 CPU: {cpu}%\n💾 RAM: {ram}%"
    else:
        msg = f"🌡️ Nhiệt độ: {temp:.1f}C\n🧠 CPU: {cpu}%\n💾 RAM: {ram}%"
    await update.message.reply_text(msg)

async def patrol_loop(context: ContextTypes.DEFAULT_TYPE):
    global patrolling, intruder_alert_active
    path = "patrol_vision.jpg"
    while patrolling:
        try:
            picam2.start()
            picam2.capture_file(path)
            picam2.stop()
            img = face_recognition.load_image_file(path)
            face_encs = face_recognition.face_encodings(img)
            found_admin = False
            for fe in face_encs:
                if True in face_recognition.compare_faces(known_face_encodings, fe):
                    found_admin = True
           
            if found_admin:
                msg = "Hi, admin! I see you! 😊" if current_lang == "English" else "Chào admin! BMO thấy bạn rồi! 😊"
                await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
                patrolling = False
                break
            elif len(face_encs) > 0:
                intruder_alert_active = True
                while intruder_alert_active:
                    msg = "🚨 Intruder alert! Who are you?" if current_lang == "English" else "🚨 Cảnh báo có người lạ! Bạn là ai?"
                    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
                    await asyncio.sleep(10)
                patrolling = False
                break
            await asyncio.sleep(5)
        except: await asyncio.sleep(10)

async def patrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    global patrolling
    if patrolling:
        patrolling = False
        msg = "BMO is stopping patrol. 🔋" if current_lang == "English" else "BMO đang dừng tuần tra. 🔋"
        await update.message.reply_text(msg)
    else:
        patrolling = True
        msg = "BMO Security Mode: ONLINE! 🛡️" if current_lang == "English" else "Chế độ an ninh: BẬT! 🛡️"
        await update.message.reply_text(msg)
        asyncio.create_task(patrol_loop(context))

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    global chat_history, intruder_alert_active, patrolling
   
    raw_text = update.message.text
    user_text = raw_text.lower()

    # Reset security state if admin confirms return
    if any(phrase in user_text for phrase in ["okay, i'm back", "i am back", "it's me"]):
        if intruder_alert_active:
            intruder_alert_active = False
            patrolling = False
            msg = "Phew! Welcome back, admin! Turning off alarm mode." if current_lang == "English" else "Phù! Chào mừng admin đã quay lại! Đang tắt chế độ báo động."
            await update.message.reply_text(msg)
            return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    chat_history.append({'role': 'user', 'content': raw_text})
    if len(chat_history) > 10: chat_history = chat_history[-10:]
   
    messages = [{'role': 'system', 'content': f'You are BMO. Child-like and love admin. ALWAYS respond in {current_lang}.'}] + chat_history
    try:
        response = await AsyncClient().chat(model=CHAT_MODEL, messages=messages)
        bot_reply = response['message']['content']
        chat_history.append({'role': 'assistant', 'content': bot_reply})
        await update.message.reply_text(bot_reply)
    except Exception as e:
        await update.message.reply_text(f"Brain fog (Ollama error): {e}")

async def tell_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    if current_lang == "English":
        jokes = ["Why did the computer go to the doctor? Virus!", "Favorite snack? Computer chips!"]
    else:
        jokes = ["Tại sao máy tính đi khám bệnh? Vì nó bị virus!", "Món ăn yêu thích của robot là gì? Chip máy tính!"]
    await update.message.reply_text(random.choice(jokes))

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    global chat_history
    chat_history = []
    msg = "Memory cleared!" if current_lang == "English" else "Bộ nhớ đã được xóa sạch!"
    await update.message.reply_text(msg)

if __name__ == '__main__':
    if not TOKEN:
        print("❌ Error: TELEGRAM_TOKEN not found in .env file!")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).connect_timeout(120).read_timeout(120).build()
   
    # Handlers registered at the end
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("look", look))
    app.add_handler(CommandHandler("patrol", patrol))
    app.add_handler(CommandHandler("joke", tell_joke))
    app.add_handler(CommandHandler("language", set_language))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
   
    print(f"BMO is online! Language: {current_lang} | Brain: {CHAT_MODEL}")
    app.run_polling()

