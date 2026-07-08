import os
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from cloudinary_helper import upload_video


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Send me a video and I'll upload it to Cloudinary."
    )


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Works for both videos and documents
    tg_file = None
    filename = "video.mp4"

    if message.video:
        tg_file = message.video
        if tg_file.file_name:
            filename = tg_file.file_name

    elif message.document:
        if message.document.mime_type and message.document.mime_type.startswith("video/"):
            tg_file = message.document
            filename = tg_file.file_name or "video.mp4"

    if tg_file is None:
        return

    status = await message.reply_text("⬇ Downloading video...")

    file = await context.bot.get_file(tg_file.file_id)

    local_path = os.path.join(
        DOWNLOAD_DIR,
        f"{tg_file.file_unique_id}_{filename}"
    )

    await file.download_to_drive(local_path)

    await status.edit_text("☁ Uploading to Cloudinary...")

    try:
        data = upload_video(local_path)

        text = f"""
✅ Upload Successful

📁 Public ID:
<code>{data['public_id']}</code>

🎬 Video URL:
{data['video_url']}

🖼 Thumbnail:
{data['thumbnail_url']}

⏱ Duration:
{data['duration']} sec

📺 Resolution:
{data['width']} x {data['height']}

💾 Size:
{round(data['bytes']/1024/1024,2)} MB
"""

        await status.edit_text(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    except Exception as e:
        await status.edit_text(f"❌ Upload failed\n\n{e}")

    finally:
        if os.path.exists(local_path):
            os.remove(local_path)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.VIDEO | filters.Document.VIDEO,
            handle_video,
        )
    )

    print("Bot Started...")

    app.run_polling()


if __name__ == "__main__":
    main()
