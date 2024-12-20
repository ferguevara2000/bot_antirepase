# bot.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import re  # Para validar el formato del chat ID
from config import TOKEN, WEB_LINK, IMAGE_URL  # Importar los parámetros desde config.py

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función para enviar un mensaje con un botón de enlace e imagen a un chat especificado"""
    bot = context.bot
    args = context.args  # Obtiene los argumentos del comando

    # Validar que se haya pasado un ID de chat como argumento
    if len(args) < 1:
        await update.message.reply_text(
            "Por favor, proporciona el ID del chat al que deseas enviar el mensaje.\n\n"
            "Uso: /send <chat_id>"
        )
        return

    # Obtener el ID del chat del argumento
    chat_id = args[0]

    # Validar formato del chat ID (puede ser un número o un número con prefijo '-')
    if not re.match(r"^-?\d+$", chat_id):
        await update.message.reply_text("El ID del chat proporcionado no es válido.")
        return

    message_text = "Haz clic en el botón para desbloquear el contenido."

    # Configuración del botón que actúa como enlace
    button = InlineKeyboardButton(
        text="Desbloquear Contenido",  # Texto del botón
        url=WEB_LINK,                 # URL del enlace
    )

    # Crear el teclado con el botón
    reply_markup = InlineKeyboardMarkup([[button]])

    try:
        # Enviar la imagen junto con el texto y el botón al chat especificado
        await bot.send_photo(
            chat_id=chat_id,
            photo=IMAGE_URL,              # URL de la imagen
            caption=message_text,         # Mensaje que acompaña la imagen
            reply_markup=reply_markup,    # Teclado con el botón
        )
        await update.message.reply_text(f"Mensaje enviado al chat {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"Error al enviar el mensaje: {e}")

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
