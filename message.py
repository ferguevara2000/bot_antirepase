from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
import re
import base64
from auth import is_user_authorized  # Verificar autorización
from user import obtener_datos_usuario, obtener_image_id_usuario  # Lógica de usuario
from api import actualizar_imagen_api  # Llamadas a la API
from config import WEB_LINK  # Enlace del botón

# Diccionario para almacenar el estado temporal de los usuarios
USER_STATE = {}

# Paso 1: Inicio del comando /send
async def iniciar_envio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de envío solicitando el ID del chat."""
    user_id = update.effective_user.id

    # Verificar si el usuario está autorizado
    if not is_user_authorized(user_id):
        await update.message.reply_text(
            "No estás autorizado para usar este bot o tu acceso ha expirado."
        )
        return

    # Guardar el estado del usuario
    USER_STATE[user_id] = {"step": "awaiting_chat_id"}

    await update.message.reply_text("Por favor, proporcione el ID del chat de destino:")

# Paso 2: Recepción del ID del chat
async def recibir_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe y valida el ID del chat del usuario."""
    user_id = update.effective_user.id
    if user_id not in USER_STATE or USER_STATE[user_id].get("step") != "awaiting_chat_id":
        return

    chat_id = update.message.text

    # Validar formato del chat ID
    if not re.match(r"^-?\d+$", chat_id):
        await update.message.reply_text("El ID del chat proporcionado no es válido.")
        return

    # Guardar el ID del chat en el estado del usuario
    USER_STATE[user_id]["chat_id"] = chat_id
    USER_STATE[user_id]["step"] = "awaiting_image"

    await update.message.reply_text("Por favor, envíe la imagen que desea reenviar:")

# Paso 3: Recepción de la imagen
async def recibir_imagen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la imagen, la convierte a Base64 y actualiza la API."""
    user_id = update.effective_user.id
    if user_id not in USER_STATE or USER_STATE[user_id].get("step") != "awaiting_image":
        return

    # Validar que el mensaje tenga una imagen
    if not update.message.photo:
        await update.message.reply_text("Por favor, envíe una imagen válida.")
        return

    # Obtener el archivo de la imagen más grande enviada
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    # Descargar la imagen
    image_path = f"{user_id}_temp_image.jpg"
    await file.download_to_drive(image_path)

    # Convertir la imagen a Base64
    try:
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        await update.message.reply_text(f"Error al procesar la imagen: {e}")
        return

    # Obtener el image_id del usuario
    image_id = obtener_image_id_usuario(user_id)
    print("Imagen Id: ",image_id)

    # Actualizar la imagen en la API
    api_response = actualizar_imagen_api(image_id, image_base64)
    if "error" in api_response:
        print(f"Error al actualizar la imagen en la API: {api_response['error']}")
        await update.message.reply_text(f"Error al actualizar la imagen")
        return

    # Enviar el mensaje al chat de destino
    await enviar_mensaje_destino(update, context, USER_STATE[user_id]["chat_id"])

    # Limpiar el estado del usuario
    del USER_STATE[user_id]

# Paso 4: Enviar el mensaje al chat de destino
async def enviar_mensaje_destino(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str):
    """Envía el mensaje al chat de destino con la imagen actualizada."""
    user_id = update.effective_user.id

    # Obtener los datos predeterminados del usuario
    mensaje_predeterminado, imagen_predeterminada = obtener_datos_usuario(user_id)

    # Configuración del botón que actúa como enlace
    button = InlineKeyboardButton(
        text="Desbloquear Contenido",
        url=WEB_LINK,
    )
    reply_markup = InlineKeyboardMarkup([[button]])

    try:
        # Enviar la imagen y el mensaje al chat de destino
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=imagen_predeterminada,
            caption=mensaje_predeterminado,
            reply_markup=reply_markup,
        )
        await update.message.reply_text(f"Mensaje enviado exitosamente al chat {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"Error al enviar el mensaje: {e}")
