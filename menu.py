import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, filters

API_BASE_URL = "https://webapp-telegram-backend.onrender.com/users"

estado_edicion = {
    "logo": {},
    "mensaje": {}
}

# Función para mostrar el menú
async def menu(update: Update, context: CallbackContext):
    """Envía un mensaje con botones para navegar por el menú."""
    keyboard = [
        [
            InlineKeyboardButton("Editar Logo", callback_data="editar_logo"),
            InlineKeyboardButton("Editar Mensaje", callback_data="editar_mensaje")
        ],
        [
            InlineKeyboardButton("Membresía", callback_data="fecha_expiracion"),
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

    user_id = query.from_user.id  # ID del usuario

    if query.data == "editar_logo":
        estado_edicion["logo"][user_id] = True
        await query.edit_message_text(text="Por favor, ingresa el nuevo URL de la imagen del logo:")
    elif query.data == "editar_mensaje":
        estado_edicion["mensaje"][user_id] = True
        await query.edit_message_text(text="Por favor, ingresa el nuevo mensaje predeterminado:")
    elif query.data == "fecha_expiracion":
        # Obtener la fecha de expiración del usuario desde el API
        try:
            usuario_response = requests.get(f"{API_BASE_URL}/{user_id}")
            if usuario_response.status_code == 200:
                usuario_data = usuario_response.json()
                fecha_expiracion = usuario_data.get("expires_at", "No disponible")
                await query.edit_message_text(text=f"📅 Tu membresía expira en la siguiente fecha: {fecha_expiracion}")
            else:
                await query.edit_message_text(text="❌ No se pudo obtener la fecha de expiración.")
        except requests.RequestException as e:
            await query.edit_message_text(text=f"❌ Error al conectarse con el API: {e}")
    elif query.data == "ayuda":
        # Mensaje de ayuda con comandos disponibles
        mensaje_ayuda = (
            "📋 *Comandos del bot:*\n"
            "/start - Inicia el bot.\n"
            "/send - Enviar un mensaje o URL.\n\n"
            "Si necesitas asistencia adicional, contacta al administrador. \n"
            "Contacto: @antonio674"
        )
        await query.edit_message_text(text=mensaje_ayuda, parse_mode="Markdown")

# Función para manejar la entrada de nuevos datos (logo o mensaje)
async def manejar_mensaje(update: Update, context: CallbackContext):
    """Maneja el mensaje del usuario para editar el logo o el mensaje."""
    user_id = update.message.from_user.id

    # Si el usuario está editando el logo
    if estado_edicion["logo"].get(user_id, False):
        nuevo_url = update.message.text

        # Validar si el URL es válido
        if validar_url_imagen(nuevo_url):
            try:
                # Obtener datos actuales del usuario desde la API
                usuario_response = requests.get(f"{API_BASE_URL}/{user_id}")
                if usuario_response.status_code == 200:
                    usuario_data = usuario_response.json()

                    # Actualizar solo el campo default_image_url
                    usuario_data["default_image_url"] = nuevo_url

                    # Enviar la actualización al API
                    actualizar_response = requests.put(f"{API_BASE_URL}/{user_id}", json=usuario_data)
                    if actualizar_response.status_code == 200:
                        await update.message.reply_text("✅ Imagen actualizada correctamente.")
                    else:
                        await update.message.reply_text("❌ Error al actualizar la imagen en el API.")
                else:
                    await update.message.reply_text("❌ No se encontró al usuario en el API.")
            except requests.RequestException as e:
                await update.message.reply_text(f"❌ Error al conectarse con el API: {e}")
        else:
            await update.message.reply_text("❌ El URL proporcionado no es válido. Por favor, ingresa un URL de imagen válido.")

        # Restablecer el estado de edición
        estado_edicion["logo"][user_id] = False

    # Si el usuario está editando el mensaje
    elif estado_edicion["mensaje"].get(user_id, False):
        nuevo_mensaje = update.message.text

        # Validar que el mensaje no esté vacío
        if nuevo_mensaje.strip():
            try:
                # Obtener datos actuales del usuario desde la API
                usuario_response = requests.get(f"{API_BASE_URL}/{user_id}")
                if usuario_response.status_code == 200:
                    usuario_data = usuario_response.json()

                    # Actualizar solo el campo default_message
                    usuario_data["default_message"] = nuevo_mensaje

                    # Enviar la actualización al API
                    actualizar_response = requests.put(f"{API_BASE_URL}/{user_id}", json=usuario_data)
                    if actualizar_response.status_code == 200:
                        await update.message.reply_text("✅ Mensaje actualizado correctamente.")
                    else:
                        await update.message.reply_text("❌ Error al actualizar el mensaje en el API.")
                else:
                    await update.message.reply_text("❌ No se encontró al usuario en el API.")
            except requests.RequestException as e:
                await update.message.reply_text(f"❌ Error al conectarse con el API: {e}")
        else:
            await update.message.reply_text("❌ El mensaje no puede estar vacío. Por favor, ingresa un mensaje válido.")

        # Restablecer el estado de edición
        estado_edicion["mensaje"][user_id] = False

# Función para validar si un URL es de una imagen válida
def validar_url_imagen(url):
    """Valida si el URL es de una imagen válida."""
    patron = re.compile(r'^(https?://.*\.(?:png|jpg|jpeg|gif|webp))$')
    return re.match(patron, url) is not None

# Función para agregar los manejadores de los comandos y botones
def agregar_manejadores(application):
    """Agrega los manejadores para el menú y los botones."""
    application.add_handler(CommandHandler("menu", menu))  # Comando para mostrar el menú
    application.add_handler(CallbackQueryHandler(boton_callback))  # Manejador de las respuestas del menú
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))  # Manejador para el texto