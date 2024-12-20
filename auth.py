import json
from datetime import datetime

# Cargar la lista de usuarios desde el archivo JSON
def load_users(file_path="users.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
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
