from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import TOKEN  # Importar el token desde config.py
from auth import get_authorization_message  # Importar autenticación
from menu import agregar_manejadores, menu
from message import iniciar_envio, recibir_imagen, recibir_chat_id  # Importar la función de enviar mensaje
from chats import handle_forwarded_message

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
    application.add_handler(CommandHandler("send", iniciar_envio))
    application.add_handler(CommandHandler("menu", menu))  # Agregar el comando /menu

    # Agregar el manejador para mensajes reenviados
    application.add_handler(MessageHandler(filters.FORWARDED, handle_forwarded_message))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_chat_id))
    application.add_handler(MessageHandler(filters.PHOTO, recibir_imagen))

    # Llamar la función que agrega los manejadores del menú
    agregar_manejadores(application)

    # Iniciar el bot
    application.run_polling()
    print("Bot está en funcionamiento...")
