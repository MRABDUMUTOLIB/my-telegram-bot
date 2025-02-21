import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

# 🔴 .env faylini yuklash
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PRIVATE_CHANNEL = os.getenv("PRIVATE_CHANNEL")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# 📌 Videolarni saqlash uchun lug‘at
video_storage = {}

# 📌 Start buyrug'i va obuna tugmalari
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    btn_private = InlineKeyboardButton("🔒 Kanalga Obuna Bo‘lish", url="https://t.me/YOUR_CHANNEL")
    btn_check = InlineKeyboardButton("✅ Obunani Tekshirish", callback_data="check_subs")
    keyboard.add(btn_private, btn_check)

    await message.answer("❗ Iltimos, kanalga obuna bo‘ling:", reply_markup=keyboard)

# 📌 Obunani tekshirish
@dp.callback_query_handler(lambda c: c.data == "check_subs")
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    try:
        member = await bot.get_chat_member(chat_id=PRIVATE_CHANNEL, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            await bot.send_message(user_id, "✅ Tabriklaymiz! Siz kanalga obuna bo‘lgansiz.")
        else:
            await bot.send_message(user_id, "❗ Iltimos, kanalga obuna bo‘ling va qaytadan tekshiring.")
    except:
        await bot.send_message(user_id, "❗ Xatolik! Kanal mavjud emas yoki token noto‘g‘ri.")

# 📌 👑 Faqat bot egasi video yuklay oladi
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def save_video(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return await message.answer("❌ Siz video yuklay olmaysiz!")

    video_file_id = message.video.file_id
    await message.answer("✅ Video qabul qilindi! Endi unga raqamli kod yozing. (Masalan: `1`)")

    @dp.message_handler(lambda msg: msg.text.isdigit())  # Faqat raqamlar qabul qilinadi
    async def assign_code(msg: types.Message):
        code = msg.text.strip()
        
        if code in video_storage:
            await msg.answer(f"⚠️ {code} kodi allaqachon mavjud! Boshqa raqam kiriting.")
        else:
            video_storage[code] = video_file_id
            await msg.answer(f"✅ Video {code} kodi bilan saqlandi!")
            dp.message_handlers.unregister(assign_code)  # Faqat bitta kod olish uchun

# 📌 👤 Foydalanuvchilar raqam yuborsa, unga video jo‘natish
@dp.message_handler(lambda message: message.text.isdigit())
async def send_video(message: types.Message):
    video_code = message.text.strip()

    if video_code in video_storage:
        video_file_id = video_storage[video_code]
        await message.answer_video(video_file_id)
    else:
        await message.answer("❌ Bunday kodga mos video topilmadi!")

# 📌 BOTNI ISHGA TUSHIRISH
if __name__ == "__main__":
    executor.start_polling(dp)
