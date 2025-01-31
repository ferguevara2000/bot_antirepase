import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from auth import is_user_authorized
from config import API_URL, API_KEY

estado_edicion = {
    "logo": {},
    "mensaje": {}
}

async def menu(update: Update, context: CallbackContext):
    """Envía un mensaje con botones para navegar por el menú."""
    keyboard = [
        [InlineKeyboardButton("Enviar Mensaje", callback_data="enviar_mensaje")],
        [InlineKeyboardButton("Guia de Uso", callback_data="guia_uso")],
        [InlineKeyboardButton("Contacto", callback_data="contacto")],
        [InlineKeyboardButton("Estado de Suscripción", callback_data="membresia")],
        [InlineKeyboardButton("Compra", callback_data="comprar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Por favor selecciona una de las opciones disponibles:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Por favor selecciona una de las opciones disponibles:", reply_markup=reply_markup)


async def boton_callback(update: Update, context: CallbackContext):
    """Maneja la acción de los botones."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "enviar_mensaje":
        await query.message.reply_text("Para enviar un mensaje, utiliza el comando /send")


def agregar_manejadores(application):
    """Agrega los manejadores para el menú y los botones."""
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(boton_callback))
