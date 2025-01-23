from numbers import Number

import requests
from telegram import Update
from telegram.constants import MessageOriginType
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import TOKEN, API_URL, API_KEY  # Asegúrate de definir `API_KEY` en tu archivo de configuración

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"


async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Verificar que el mensaje no sea None
    if message is None:
        return

    # Caso 1: Mensaje reenviado desde un canal
    if message.forward_origin and message.forward_origin.type == MessageOriginType.CHANNEL:
        forward_origin = message.forward_origin
        chat_id = forward_origin.chat.id
        chat_title = forward_origin.chat.title or "Sin título (canal)"

        # Datos a enviar a la API
        data = {
            "p_chat_id": chat_id,
            "p_name": chat_title,
            "p_user_id": message.from_user.id  # Incluye el ID del usuario que envió el mensaje
        }

        # Configurar encabezados de la solicitud
        headers = {
            "apiKey": API_KEY,
            "Authorization": f"Bearer {API_KEY}",  # Enviar la API key en el encabezado
            "Content-Type": "application/json"
        }

        try:
            # Enviar datos a la API
            response = requests.post(f"{API_URL}/insert_group", json=data, headers=headers)

            # Verificar si la solicitud fue exitosa
            if response.status_code in [201, 204]:  # Suponiendo que la API devuelve un 201 al crear un recurso
                await message.reply_text(f"Canal registrado correctamente:\nID: {chat_id}\nNombre: {chat_title}")
            else:
                # Respuesta en caso de error de la API
                await message.reply_text(
                    f"No se pudo registrar el canal. Respuesta del servidor: {response.status_code}\n{response.text}"
                )
        except requests.exceptions.RequestException as e:
            # Manejo de errores de conexión
            await message.reply_text(f"Ocurrió un error al intentar conectar con la API: {e}")

    # Otros casos: Mensaje reenviado desde un grupo u origen desconocido
    else:
        # Informar al usuario que no es posible registrar ID de grupos privados
        await message.reply_text(
            "Lo siento, el bot no puede obtener el ID de grupos privados o supergrupos. \n"
            "Usa otro bot para obtener el ID de tu grupo."
        )

async def get_chats_by_user(user_id, update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = {
        "p_user_id": user_id  # Incluye el ID del usuario que envió el mensaje
    }

    # Configurar encabezados de la solicitud
    headers = {
        "apiKey": API_KEY,
        "Authorization": f"Bearer {API_KEY}",  # Enviar la API key en el encabezado
        "Content-Type": "application/json"
    }

    try:
        # Enviar datos a la API
        response = requests.post(f"{API_URL}/get_groups_by_user", json=data, headers=headers)

        # Verificar si la solicitud fue exitosa
        if response.status_code in [200, 201, 204]:  # Suponiendo que la API devuelve un 201 al crear un recurso
            return response.json()
        else:
            # Respuesta en caso de error de la API
            print(f"No se pudo obtener la informacion de la api: {response}")
    except requests.exceptions.RequestException as e:
        # Manejo de errores de conexión
        print(f"Ocurrio un error: {e}")

async def verify_chat_exist(chat_id: str, user_id: Number):
    if not chat_id.startswith("-"):
        chat_id = "-" + chat_id

    data = {
        "p_chat_id": chat_id,
        "p_user_id": user_id
    }

    # Configurar encabezados de la solicitud
    headers = {
        "apiKey": API_KEY,
        "Authorization": f"Bearer {API_KEY}",  # Enviar la API key en el encabezado
        "Content-Type": "application/json"
    }

    try:
        # Enviar datos a la API
        response = requests.post(f"{API_URL}/exist_chat_id_by_user", json=data, headers=headers)

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200 and response.content:  # Suponiendo que la API devuelve un 201 al crear un recurso
            return True
        else:
            # Respuesta en caso de error de la API
            print(f"No se pudo obtener la informacion de la api: {response}")
            return False
    except requests.exceptions.RequestException as e:
        # Manejo de errores de conexión
        print(f"Ocurrio un error: {e}")

async def insert_group(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id, chat_title, user_id):
    # Datos a enviar a la API
    data = {
        "p_chat_id": chat_id,
        "p_name": chat_title,
        "p_user_id": user_id  # Incluye el ID del usuario que envió el mensaje
    }

    # Configurar encabezados de la solicitud
    headers = {
        "apiKey": API_KEY,
        "Authorization": f"Bearer {API_KEY}",  # Enviar la API key en el encabezado
        "Content-Type": "application/json"
    }

    try:
        # Enviar datos a la API
        response = requests.post(f"{API_URL}/insert_group", json=data, headers=headers)

        # Verificar si la solicitud fue exitosa
        if response.status_code in [201, 204]:  # Suponiendo que la API devuelve un 201 al crear un recurso
            print(f"Canal registrado correctamente:\nID: {chat_id}\nNombre: {chat_title}")
        else:
            # Respuesta en caso de error de la API
            print(f"No se pudo registrar el canal. Respuesta del servidor: {response.status_code}\n{response.text}")
    except requests.exceptions.RequestException as e:
        # Manejo de errores de conexión
        print(f"Ocurrió un error al intentar conectar con la API: {e}")

async def get_group_name(context, chat_id: str) -> str:
    try:
        # Usamos el bot para obtener información del chat
        chat = await context.bot.get_chat(chat_id)
        return chat.title  # Retornamos el nombre del grupo (title)
    except TelegramError as e:
        # Si ocurre un error, capturamos la excepción
        print(f"Error al obtener el nombre del grupo: {e}")
        return ""