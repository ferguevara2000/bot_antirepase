import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from auth import is_user_authorized
from config import API_URL, API_KEY

API_BASE_URL = f"{API_URL}/get_user_by_id"

estado_edicion = {
    "logo": {},
    "mensaje": {}
}
# Estados para la conversación
ID_CHAT, IMAGE_URL = range(2)

async def menu(update: Update, context: CallbackContext):
    """Envía un mensaje con botones para navegar por el menú."""
    keyboard = [
        [InlineKeyboardButton("Enviar Mensaje", callback_data="enviar_mensaje")],
        [InlineKeyboardButton("Guia de Uso", callback_data="guia_uso")],
        [
            InlineKeyboardButton("Contacto", callback_data="contacto"),
            InlineKeyboardButton("Membresía", callback_data="membresia")
        ],
        [
            InlineKeyboardButton("Comprar", callback_data="comprar"),
            InlineKeyboardButton("Ajustes", callback_data="ajustes")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Por favor selecciona una opción:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Por favor selecciona una opción:", reply_markup=reply_markup)


async def boton_callback(update: Update, context: CallbackContext):
    """Maneja la acción de los botones."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "ajustes":
        # Submenú de ajustes
        ajustes_keyboard = [
            [InlineKeyboardButton("     Editar Logo     ", callback_data="editar_logo")],
            [InlineKeyboardButton("     Editar Mensaje      ", callback_data="editar_mensaje")],
            [InlineKeyboardButton("   Regresar ↩️   ", callback_data="regresar_menu")]
        ]
        ajustes_markup = InlineKeyboardMarkup(ajustes_keyboard)
        await query.edit_message_text("Por favor selecciona una opción:", reply_markup=ajustes_markup)

    elif query.data == "editar_logo":
        # Activar el estado de edición para el logo
        estado_edicion["logo"][user_id] = True
        await query.edit_message_text("Por favor, ingresa el nuevo URL para la imagen del logo:")

    elif query.data == "editar_mensaje":
        # Activar el estado de edición para el mensaje
        estado_edicion["mensaje"][user_id] = True
        await query.edit_message_text("Por favor, ingresa el nuevo mensaje predeterminado:")

    elif query.data == "regresar_menu":
        # Volver al menú principal
        await menu(update, context)


    elif query.data == "enviar_mensaje":

        await query.message.reply_text("Para enviar un mensaje, utiliza el comando /send")



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
                usuario_response = requests.post(
                    API_BASE_URL,
                    json={"p_user_id": user_id},
                    headers={
                        "Content-Type": "application/json",
                        "apikey": API_KEY,
                        "Authorization": f"Bearer {API_KEY}"
                    }
                )

                # Validar que la respuesta tenga contenido
                if usuario_response.status_code == 200 and usuario_response.json():
                    usuario_data = usuario_response.json()[0]  # Supabase devuelve una lista

                    # Actualizar solo el campo default_image_url
                    usuario_data["default_image_url"] = nuevo_url

                    # Aquí puedes implementar la lógica para actualizar el usuario en tu base de datos.
                    # Simulando la actualización exitosa:
                    await update.message.reply_text("✅ Imagen actualizada correctamente.")
                else:
                    await update.message.reply_text("❌ No se encontró al usuario en el API o la respuesta está vacía.")
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
                usuario_response = requests.post(
                    API_BASE_URL,
                    json={"p_user_id": user_id},
                    headers={
                        "Content-Type": "application/json",
                        "apikey": API_KEY,
                        "Authorization": f"Bearer {API_KEY}"
                    }
                )

                # Validar que la respuesta tenga contenido
                if usuario_response.status_code == 200 and usuario_response.json():
                    usuario_data = usuario_response.json()[0]  # Supabase devuelve una lista

                    # Actualizar solo el campo default_message
                    usuario_data["default_message"] = nuevo_mensaje

                    # Aquí puedes implementar la lógica para actualizar el usuario en tu base de datos.
                    # Simulando la actualización exitosa:
                    await update.message.reply_text("✅ Mensaje actualizado correctamente.")
                else:
                    await update.message.reply_text("❌ No se encontró al usuario en el API o la respuesta está vacía.")
            except requests.RequestException as e:
                await update.message.reply_text(f"❌ Error al conectarse con el API: {e}")
        else:
            await update.message.reply_text("❌ El mensaje no puede estar vacío. Por favor, ingresa un mensaje válido.")

        # Restablecer el estado de edición
        estado_edicion["mensaje"][user_id] = False

# Función para validar si un URL es de una imagen válida
def validar_url_imagen(url):
    """Valida si el URL apunta a una imagen, incluso si no termina con una extensión de archivo."""
    try:
        # Validar el formato básico del URL
        patron = re.compile(r'^https?://')
        if not re.match(patron, url):
            return False

        # Realizar una solicitud HEAD para verificar el Content-Type
        response = requests.head(url, allow_redirects=True, timeout=5)
        content_type = response.headers.get("Content-Type", "")
        return content_type.startswith("image/")
    except requests.RequestException:
        return False

# Función para agregar los manejadores de los comandos y botones
def agregar_manejadores(application):
    """Agrega los manejadores para el menú y los botones."""
    application.add_handler(CommandHandler("menu", menu))  # Comando para mostrar el menú
    application.add_handler(CallbackQueryHandler(boton_callback))  # Manejador de las respuestas del menú
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))  # Manejador para el texto