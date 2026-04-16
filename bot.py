import asyncio
import logging
import os
print("=== ALL ENVIRONMENT VARIABLES ===")
for key, value in os.environ.items():
    if 'TOKEN' in key or 'API' in key:
        print(f"{key}={value[:10]}...")
print("=================================")
from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from gmailnator_client import GmailnatorClient
from config import TELEGRAM_TOKEN, RAPIDAPI_KEY, RAPIDAPI_HOST, CHECK_ATTEMPTS, CHECK_INTERVAL_FIRST, CHECK_INTERVAL_SECOND

# Настройка таймаутов для запросов к Telegram
request_kwargs = {
    'connect_timeout': 60.0,
    'read_timeout': 60.0,
    'write_timeout': 60.0,
    'pool_timeout': 60.0,
}
request = HTTPXRequest(**request_kwargs)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logging.getLogger("httpx").setLevel(logging.WARNING)


class FacebookCodeBot:
    def __init__(self):
        self.client = GmailnatorClient(RAPIDAPI_KEY, RAPIDAPI_HOST)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🔐 *Uniacc Facebook Code Bot*\n\n"
            "I help you get verification codes from Facebook.\n\n"
            "*How it works:*\n"
            "1️⃣ Request a verification code from Facebook to your email\n"
            "2️⃣ Send me that email address\n"
            "3️⃣ I'll find the code and send it to you\n\n"
            "*Commands:*\n"
            "/start - Start the bot\n"
            "/help - Get help\n\n"
            "*Example:*\n"
            "`Mail.from.link@gmail.com`\n\n"
            "Need help? @Uniacc\\_store",
            parse_mode='Markdown'
        )

    async def handle_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle email to search for verification code"""
        email = update.message.text.strip()

        # Validate email
        if '@' not in email or '.' not in email:
            await update.message.reply_text(
                "❌ Please send a valid email address.\n\n"
                "Example: `Mail.from.link@gmail.com`",
                parse_mode='Markdown'
            )
            return

        status_msg = await update.message.reply_text(
            f"📧 `{email}`\n"
            f"🔄 Searching for code...\n"
            f"⏳ {CHECK_ATTEMPTS} checks (at {CHECK_INTERVAL_FIRST} and {CHECK_INTERVAL_FIRST + CHECK_INTERVAL_SECOND} seconds)",
            parse_mode='Markdown'
        )

        try:
            # Search for verification code
            verification_code = await asyncio.to_thread(
                self.client.find_verification_code,
                email=email,
                attempts=CHECK_ATTEMPTS,
                interval_first=CHECK_INTERVAL_FIRST,
                interval_second=CHECK_INTERVAL_SECOND
            )

            if verification_code:
                await status_msg.edit_text(
                    f"✅ *Verification code found!*\n\n"
                    f"📧 `{email}`\n\n"
                    f"🔐 `{verification_code}`",
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
            else:
                await status_msg.edit_text(
                    f"❌ *Code not found*\n\n"
                    f"📧 `{email}`\n\n"
                    f"Please try:\n"
                    f"• Request a new verification code\n"
                    f"• Check the email address is correct",
                    parse_mode='Markdown'
                )

        except Exception as e:
            logger.error(f"Error processing {email}: {e}")
            await status_msg.edit_text(
                f"❌ *Error*\n\n"
                f"📧 `{email}`\n\n"
                f"```\n{str(e)[:150]}\n```",
                parse_mode='Markdown'
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📚 *Help & Instructions*\n\n"
            "*How to get a verification code:*\n\n"
            "1. Request a verification code from Facebook\n"
            "2. Facebook will send an email with subject \"Verify your business email\"\n"
            "3. Copy the email address and send it to me\n"
            "4. I'll find the 6-digit code and send it to you\n\n"
            f"*Limitations:*\n"
            f"• {CHECK_ATTEMPTS} checks (at {CHECK_INTERVAL_FIRST} and {CHECK_INTERVAL_FIRST + CHECK_INTERVAL_SECOND} seconds)\n"
            f"• Works only with emails from Facebook\n\n"
            "*Commands:*\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n\n"
            "Need help? @Uniacc\\_store",
            parse_mode='Markdown'
        )


def main():
    if not TELEGRAM_TOKEN:
        print("❌ Error: TELEGRAM_TOKEN not found in .env")
        return

    print("🤖 Starting Facebook Code Bot...")
    print("✅ Gmailnator client ready")
    print(f"⚙️ Settings: {CHECK_ATTEMPTS} checks (at {CHECK_INTERVAL_FIRST} and {CHECK_INTERVAL_FIRST + CHECK_INTERVAL_SECOND} seconds)")

    bot = FacebookCodeBot()
    app = Application.builder().token(TELEGRAM_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("help", bot.help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_email))

    print("✅ Bot is running and ready!")
    print("📌 Waiting for emails to search for verification codes")
    app.run_polling()


if __name__ == "__main__":
    main()