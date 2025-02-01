import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
import re
import base64
from auth import is_user_authorized  # Verificar autorización
from user import obtener_datos_usuario, obtener_image_id_usuario, obtener_timer_usuario  # Lógica de usuario
from api import actualizar_imagen_api  # Llamadas a la API
from config import WEB_LINK, API_KEY, API_URL  # Enlace del botón
from chats import get_chats_by_user, verify_chat_exist, get_group_name, insert_group

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

    chats_list = await get_chats_by_user(user_id, update, context)

    # Construir una cadena con el formato deseado
    formatted_chats = "\n".join(
        [f"- {chat['name']}:  `{chat['chat_id']}`" for chat in chats_list]  # Usar bloque de código Markdown
    )

    await update.message.reply_text(
        f"Por favor, proporcione el ID del chat de destino:\n\n"
        f"Listado de IDs registrados:\n"
        f"{formatted_chats}\n\n"
        f"El ID de tu grupo o canal se agregará automáticamente a la lista al enviar un mensaje.",
        parse_mode="Markdown"
    )

# Paso 2: Recepción del ID del chat
async def recibir_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe y valida el ID del chat del usuario."""
    user_id = update.effective_user.id

    if user_id not in USER_STATE:
        USER_STATE[user_id] = {}

    chat_id = update.message.text

    # Verificar si el chat_id no comienza con "-"
    if not chat_id.startswith("-"):
        chat_id = "-" + chat_id

    # Validar formato del chat ID
    if not re.match(r"^-?\d+$", chat_id):
        await update.message.reply_text("El ID del chat proporcionado no es válido.")
        return

    # Obtener el nombre del grupo/canal si existe
    chat_title = await get_group_name(context, chat_id)

    # Registrar el grupo si no existe
    if not await verify_chat_exist(chat_id, user_id):
        await insert_group(update, context, chat_id, chat_title, user_id)

    # Guardar el último chat_id para el usuario
    USER_STATE[user_id]["chat_id"] = chat_id
    USER_STATE[user_id]["step"] = "awaiting_image"

    await update.message.reply_text("Por favor, envíe la imagen que desea reenviar:")


# Recepción de la imagen (envío automático al último chat_id)
async def recibir_imagen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la imagen, la convierte a Base64 y actualiza la API."""
    user_id = update.effective_user.id

    if user_id not in USER_STATE or "chat_id" not in USER_STATE[user_id]:
        await update.message.reply_text("No se encontró un chat_id registrado. Por favor, proporcione uno primero usando el comando /send")
        return

    # Obtener el último chat_id del usuario
    chat_id = USER_STATE[user_id]["chat_id"]

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

    # Actualizar la imagen en la API
    api_response = actualizar_imagen_api(image_id, image_base64)
    if "error" in api_response:
        print(f"Error al actualizar la imagen en la API: {api_response['error']}")
        await update.message.reply_text(f"Error al actualizar la imagen")
        return

    # Enviar el mensaje al último chat_id
    await enviar_mensaje_destino(update, context, chat_id)

    # No eliminar el estado, mantenerlo para futuras solicitudes
    USER_STATE[user_id]["step"] = "awaiting_image"

# Modifica la función enviar_mensaje_destino para reemplazar el mensaje original
async def enviar_mensaje_destino(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: str):
    """Envía el mensaje al chat de destino con la imagen obtenida desde la API."""
    user_id = update.effective_user.id

    # Obtener el ID de la imagen y descargarla desde la API
    image_id = obtener_image_id_usuario(user_id)
    print(image_id)
    image_path = await obtener_imagen_desde_api(int(image_id))

    if not image_path:
        await update.message.reply_text("No se pudo obtener la imagen desde la API.")
        return

    # Configuración del botón que actúa como enlace
    button = InlineKeyboardButton(
        text="Desbloquear Contenido",
        url=WEB_LINK,
    )
    reply_markup = InlineKeyboardMarkup([[button]])

    # Obtener los datos predeterminados del usuario
    mensaje_predeterminado, imagen_predeterminada = obtener_datos_usuario(user_id)

    try:
        # Enviar la imagen al chat de destino
        original_message = await context.bot.send_photo(
            chat_id=chat_id,
            photo=imagen_predeterminada,
            caption=mensaje_predeterminado,
            reply_markup=reply_markup,
        )

        # Obtener el message_id del mensaje original
        message_id = original_message.message_id

        #Obtener el timer del usuario
        user_timer = obtener_timer_usuario(user_id)
        print("timer: ", user_timer)

        # Programar la eliminación del mensaje original y reemplazarlo
        context.job_queue.run_once(
            eliminar_y_reemplazar_mensaje,
            when=user_timer,  # Tiempo en segundos
            data={  # Aquí pasamos chat_id dentro de 'data'
                "chat_id": chat_id,
                "message_id": message_id,
                "photo_path": f"{user_id}_temp_image.jpg",
            },
        )

        await update.message.reply_text(f"Mensaje enviado con exito al chat: {chat_id}")

    except Exception as e:
        await update.message.reply_text(f"Error al enviar el mensaje: {e}")
    finally:
        # Elimina el archivo temporal si ya no es necesario
        if os.path.exists(image_path):
            os.remove(image_path)


async def obtener_imagen_desde_api(image_id: int):
    """Obtiene la imagen en base64 desde la API y la decodifica."""
    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY,
        "Authorization": f"Bearer {API_KEY}",
    }
    payload = {"image_id": image_id}

    try:
        response = requests.post(f"{API_URL}/get_image_by_id", json=payload, headers=headers)

        # Verificar si la solicitud fue exitosa (HTTP 200)
        if response.status_code == 200:
            # La respuesta es una cadena en Base64
            image_base64 = response.text.strip()
            return image_base64
        else:
            print(f"Error: Código de estado {response.status_code}")
            print("Respuesta:", response.text)
            return None
    except Exception as e:
        print(f"Error al obtener la imagen desde la API: {e}")
        return None

async def eliminar_y_reemplazar_mensaje(context):
    """Elimina el mensaje original y lo reemplaza con la foto enviada originalmente."""
    job_data = context.job.data
    chat_id = job_data.get("chat_id")
    try:
        # Eliminar el mensaje original
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=job_data["message_id"],
        )

        # Enviar nuevamente la foto sin el botón
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=open(job_data["photo_path"], "rb"),
        )
    except Exception as e:
        print(f"Error al reemplazar el mensaje: {e}")
    finally:
        # Eliminar el archivo temporal
        if os.path.exists(job_data["photo_path"]):
            os.remove(job_data["photo_path"])