from threading import Thread
from server import start_server  # Importar el servidor Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TOKEN, WEB_LINK  # Importar parámetros desde config.py
from auth import get_authorization_message, is_user_authorized  # Importar autenticación
from menu import agregar_manejadores, menu
from message import send_message  # Importar la función de enviar mensaje

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

    # Inicia el servidor Flask en un hilo paralelo
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()

    # Iniciar el bot
    application.run_polling()
    print("Bot está en funcionamiento...")

if __name__ == "__main__":
    main()
