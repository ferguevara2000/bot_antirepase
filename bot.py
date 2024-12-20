from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Token de tu bot
TOKEN = "7837611356:AAEBYhO4RI82sX4W_YCXzH1XbEwHH6O39tk"

# ID del chat al que enviarás el mensaje (puede ser un chat individual o grupal)
CHAT_ID = "-1002346148753"

# URL de tu web app
WEB_LINK = "https://t.me/resendFer_bot/test"  # Asegúrate de usar el prefijo https://

# URL o ruta local de la imagen
IMAGE_URL = "https://via.placeholder.com/600x400.png?text=Desbloquear+Contenido"  # URL pública de la imagen

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función para enviar un mensaje con un botón de enlace e imagen"""
    bot = context.bot
    message_text = "Haz clic en el botón para desbloquear el contenido."

    # Configuración del botón que actúa como enlace
    button = InlineKeyboardButton(
        text="Desbloquear Contenido",  # Texto del botón
        url=WEB_LINK,                 # URL del enlace
    )

    # Crear el teclado con el botón
    reply_markup = InlineKeyboardMarkup([[button]])

    # Enviar la imagen junto con el texto y el botón
    await bot.send_photo(
        chat_id=CHAT_ID,
        photo=IMAGE_URL,              # URL de la imagen
        caption=message_text,         # Mensaje que acompaña la imagen
        reply_markup=reply_markup,    # Teclado con el botón
    )

def main():
    """Función principal para ejecutar el bot"""
    # Crear la aplicación con el token del bot
    application = Application.builder().token(TOKEN).build()

    # Comandos disponibles
    application.add_handler(CommandHandler("send", send_message))

    # Iniciar el bot
    application.run_polling()
    print("Bot está en funcionamiento...")

if __name__ == "__main__":
    main()