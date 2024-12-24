from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import re  # Para validar el formato del chat ID
from config import TOKEN, WEB_LINK  # Importar parámetros desde config.py
from auth import get_authorization_message, is_user_authorized  # Importar autenticación
from user import obtener_datos_usuario  # Importar la lógica de usuario
from menu import agregar_manejadores, menu

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función para enviar un mensaje con un botón de enlace, mensaje personalizado e imagen a un chat especificado."""
    bot = context.bot
    user_id = update.effective_user.id

    # Verificar si el usuario está autorizado
    if not is_user_authorized(user_id):
        await update.message.reply_text(
            "No estás autorizado para usar este bot o tu acceso ha expirado."
        )
        return

    args = context.args  # Obtiene los argumentos del comando

    # Validar que se hayan pasado argumentos
    if len(args) < 1:
        await update.message.reply_text(
            "Por favor, proporciona al menos el ID del chat.\n\n"
            "Uso: /send <chat_id> [mensaje] [url_imagen]"
        )
        return

    # Obtener el ID del chat del argumento
    chat_id = args[0]

    # Validar formato del chat ID (puede ser un número o un número con prefijo '-')
    if not re.match(r"^-?\d+$", chat_id):
        await update.message.reply_text("El ID del chat proporcionado no es válido.")
        return

    # Obtener los datos del usuario (mensaje e imagen)
    mensaje_predeterminado, imagen_predeterminada = obtener_datos_usuario(user_id)

    # Detectar si el último argumento es un enlace (URL)
    if len(args) > 2 and args[-1].startswith("http"):
        image_url = args[-1]  # Último argumento como URL de la imagen
        message_text = " ".join(args[1:-1])  # El resto como mensaje personalizado
    else:
        image_url = imagen_predeterminada  # URL de la imagen predeterminada
        message_text = " ".join(args[1:]) if len(args) > 1 else mensaje_predeterminado

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
            photo=image_url,             # URL de la imagen
            caption=message_text,        # Mensaje que acompaña la imagen
            reply_markup=reply_markup,   # Teclado con el botón
        )
        await update.message.reply_text(f"Mensaje enviado al chat {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"Error al enviar el mensaje: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start para autenticar usuarios"""
    user_id = update.effective_user.id
    message = get_authorization_message(user_id)  # Verificar autorización
    await update.message.reply_text(message)

def main():
    """Función principal para ejecutar el bot"""
    # Crear la aplicación con el token del bot
    application = Application.builder().token(TOKEN).build()

    # Comandos disponibles
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("send", send_message))
    application.add_handler(CommandHandler("menu", menu))  # Agregar el comando /menu

    # Llamar la función que agrega los manejadores del menú
    agregar_manejadores(application)

    # Iniciar el bot
    application.run_polling()
    print("Bot está en funcionamiento...")

if __name__ == "__main__":
    main()
