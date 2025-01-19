import requests
from datetime import datetime
from config import API_KEY, API_URL

# Cargar la lista de usuarios desde Supabase
def load_users():
    try:
        headers = {
            "Content-Type": "application/json",
            "apikey": API_KEY,
            "Authorization": f"Bearer {API_KEY}"
        }
        response = requests.post(f"{API_URL}/get_user_list", headers=headers)  # Hacemos una solicitud POST
        response.raise_for_status()  # Verificar si la solicitud fue exitosa
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al cargar usuarios desde Supabase: {e}")
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