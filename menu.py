from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler

# Función para mostrar el menú
async def menu(update: Update, context: CallbackContext):
    """Envía un mensaje con botones para navegar por el menú."""
    keyboard = [
        [
            InlineKeyboardButton("Editar Logo", callback_data="editar_logo"),
            InlineKeyboardButton("Editar Mensaje", callback_data="editar_mensaje")
        ],
        [
            InlineKeyboardButton("Fecha de Expiración", callback_data="fecha_expiracion"),
            InlineKeyboardButton("Ayuda", callback_data="ayuda")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('Por favor selecciona una opción:', reply_markup=reply_markup)

# Función para manejar los botones del menú
async def boton_callback(update: Update, context: CallbackContext):
    """Maneja la acción de los botones."""
    query = update.callback_query
    await query.answer()

    if query.data == "editar_logo":
        await query.edit_message_text(text="Aquí puedes editar el logo.")
    elif query.data == "editar_mensaje":
        await query.edit_message_text(text="Aquí puedes editar el mensaje.")
    elif query.data == "fecha_expiracion":
        await query.edit_message_text(text="Aquí puedes ver la fecha de expiración.")
    elif query.data == "ayuda":
        await query.edit_message_text(text="Aquí puedes obtener ayuda.")

# Función para agregar los manejadores de los comandos y botones
def agregar_manejadores(application):
    """Agrega los manejadores para el menú y los botones."""
    application.add_handler(CommandHandler("menu", menu))  # Comando para mostrar el menú
    application.add_handler(CallbackQueryHandler(boton_callback))  # Manejador de las respuestas del menú
