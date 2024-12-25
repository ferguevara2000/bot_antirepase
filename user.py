import requests

# Dirección del API
API_URL = "https://webapp-telegram-backend.onrender.com/users"

def cargar_datos_usuarios():
    """Carga los datos de los usuarios desde un API."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Verificar si la solicitud fue exitosa
        return response.json()  # Devuelve una lista de usuarios
    except requests.exceptions.RequestException as e:
        print(f"Error al cargar usuarios desde el API: {e}")
        return []  # Retorna una lista vacía si la solicitud falla

def obtener_datos_usuario(user_id):
    """Obtiene la configuración personalizada (mensaje e imagen) de un usuario."""
    usuarios = cargar_datos_usuarios()

    # Buscar al usuario en la lista de usuarios
    usuario_data = next((usuario for usuario in usuarios if usuario['user_id'] == user_id), None)

    if usuario_data:
        mensaje_predeterminado = usuario_data.get("default_message", "Mensaje predeterminado no encontrado.")
        imagen_predeterminada = usuario_data.get(
            "default_image_url",
            "https://upload.wikimedia.org/wikipedia/commons/6/64/Ejemplo.png"
        )
        return mensaje_predeterminado, imagen_predeterminada

    # Si no se encuentra el usuario, se devuelven valores por defecto
    return "Mensaje no configurado.", "https://upload.wikimedia.org/wikipedia/commons/6/64/Ejemplo.png"

def obtener_image_id_usuario(user_id):
    """Obtiene el image_id de un usuario."""
    usuarios = cargar_datos_usuarios()

    # Buscar al usuario en la lista de usuarios
    usuario_data = next((usuario for usuario in usuarios if usuario['user_id'] == user_id), None)

    if usuario_data:
        return usuario_data.get("image_id", 0)  # Retorna el image_id o 0 como predeterminado

    # Si no se encuentra el usuario, se retorna un valor por defecto
    return 0
