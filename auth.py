import requests
from datetime import datetime

# Dirección del API
API_URL = "https://webapp-telegram-backend.onrender.com/users"

# Cargar la lista de usuarios desde el API
def load_users():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Verificar si la solicitud fue exitosa
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al cargar usuarios desde el API: {e}")
        return []

# Verificar si el usuario está autorizado
def is_user_authorized(user_id):
    users = load_users()
    for user in users:
        if user["user_id"] == user_id:
            # Verificar si la fecha de expiración es válida
            expires_at = datetime.fromisoformat(user["expires_at"])
            if expires_at > datetime.now():
                return True
            else:
                return False
    return False

# Obtener el mensaje de autorización
def get_authorization_message(user_id):
    if is_user_authorized(user_id):
        return "¡Autenticación exitosa! Puedes usar el bot."
    else:
        return "No estás autorizado para usar este bot o tu acceso ha expirado."
