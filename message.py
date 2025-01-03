from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import re
from auth import is_user_authorized  # Verificar autorización
from user import obtener_datos_usuario, obtener_image_id_usuario  # Lógica de usuario
from api import actualizar_imagen_api  # Llamadas a la API
from config import WEB_LINK  # Enlace del botón

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función para enviar un mensaje con un botón de enlace y la imagen predeterminada a un chat especificado."""
    bot = context.bot
    user_id = update.effective_user.id

    # Verificar si el usuario está autorizado
    if not is_user_authorized(user_id):
        await update.message.reply_text(
            "No estás autorizado para usar este bot o tu acceso ha expirado."
        )
        return

    args = context.args  # Obtiene los argumentos del comando

    # Validar que se hayan pasado los argumentos necesarios
    if len(args) != 2:
        await update.message.reply_text(
            "Uso incorrecto del comando.\n\n"
            "Formato correcto: /send <chat_id> <image_url>"
        )
        return

    # Obtener el ID del chat del primer argumento
    chat_id = args[0]

    # Validar formato del chat ID (puede ser un número o un número con prefijo '-')
    if not re.match(r"^-?\d+$", chat_id):
        await update.message.reply_text("El ID del chat proporcionado no es válido.")
        return

    # Obtener la URL de la imagen del segundo argumento
    image_url = args[1]

    # Validar formato de la URL (opcional, para mayor robustez)
    if not image_url.startswith("http"):
        await update.message.reply_text("Proporcione una URL válida para la imagen.")
        return

    # Obtener los datos predeterminados del usuario
    mensaje_predeterminado, imagen_predeterminada = obtener_datos_usuario(user_id)

    # Configuración del botón que actúa como enlace
    button = InlineKeyboardButton(
        text="Desbloquear Contenido",  # Texto del botón
        url=WEB_LINK,                 # URL del enlace
    )

    # Crear el teclado con el botón
    reply_markup = InlineKeyboardMarkup([[button]])

    try:
        # Obtener el image_id del usuario
        image_id = obtener_image_id_usuario(user_id)

        # Llamar a la API para actualizar la imagen
        api_response = actualizar_imagen_api(image_id, image_url)

        # Verificar si hubo un error en la API
        if "error" in api_response:
            await update.message.reply_text(f"Error al actualizar la API: {api_response['error']}")
            return

        # Enviar la imagen predeterminada junto con el mensaje y el botón al chat especificado
        await bot.send_photo(
            chat_id=chat_id,
            photo=imagen_predeterminada,  # Imagen predeterminada
            caption=mensaje_predeterminado,  # Mensaje predeterminado
            reply_markup=reply_markup,   # Teclado con el botón
        )
        await update.message.reply_text(
            f"Mensaje enviado al chat {chat_id}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error al enviar el mensaje: {e}")
