import os
import re
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "9269356076:AAGDArYj5-CMtcCvchBGGQG7PUsRW1FWxjw"
CHANNEL_URL = "https://t.me/+UyBmDcQRKORlNGI1"
GUIDE_VIEWER_URL = "https://ibb.co/Q7w4QQXh"
LOCAL_IMAGE_PATH = "guide.png"  # Agar folder/repo mein image rakhe toh yahi naam rakhna

bot = telebot.TeleBot(BOT_TOKEN)


def get_direct_image_url(viewer_url: str):
    """ImgBB viewer page se direct i.ibb.co image URL nikalne ki koshish karta hai."""
    try:
        resp = requests.get(viewer_url, timeout=15)
        resp.raise_for_status()
        match = re.search(r"https://i\.ibb\.co/[A-Za-z0-9_-]+/[^\s\"'<>]+", resp.text)
        if match:
            return match.group(0)
    except Exception as e:
        print(f"Viewer page fetch error: {e}")
    return None


def send_tutorial_photo(chat_id: int):
    caption = "📸 HOW TO JOIN & VERIFY (Step 1 + Step 2) 👇"

    # 1. Pehle local file check karega
    if os.path.exists(LOCAL_IMAGE_PATH):
        with open(LOCAL_IMAGE_PATH, "rb") as img:
            bot.send_photo(chat_id, img, caption=caption)
        return True

    # 2. Warna viewer link se direct image nikal kar bhejega
    direct_url = get_direct_image_url(GUIDE_VIEWER_URL)
    if direct_url:
        try:
            img_resp = requests.get(direct_url, timeout=15)
            img_resp.raise_for_status()
            bot.send_photo(chat_id, img_resp.content, caption=caption)
            return True
        except Exception as e:
            print(f"Direct image send error: {e}")

    return False


@bot.message_handler(commands=["start"])
def start_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 JOIN OUR CHANNEL", url=CHANNEL_URL))
    markup.add(InlineKeyboardButton("✅ I HAVE JOINED", callback_data="/claim"))

    sent_photo = send_tutorial_photo(message.chat.id)

    text = (
        "🔥 *WELCOME TO MOHIT FZX BOT* 🔥\n\n"
        "📢 Is bot ko use karne ke liye aapko hamara official channel join karna zaroori hai!\n\n"
        f"🖼️ Guide Link: {GUIDE_VIEWER_URL}\n\n"
        "👇 Niche diye gaye button par click karke channel join karein:"
    )

    if not sent_photo:
        text += "\n\n⚠️ _Photo direct load nahi ho paayi, upar diye gaye Guide Link par click karke dekh lein._"

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "/claim")
def claim_handler(call):
    bot.answer_callback_query(call.id, "Verified!")
    bot.send_message(
        call.message.chat.id,
        "✅ *I HAVE JOINED* tap ho gaya! Yahan aage ka claim/reward ya menu flow aayega.",
        parse_mode="Markdown"
    )


if __name__ == "__main__":
    print("Bot chal raha hai...")
    bot.infinity_polling(skip_pending=True)
