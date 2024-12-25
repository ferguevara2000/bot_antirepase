import requests  # Para realizar solicitudes HTTP

# URL base de la API
API_BASE_URL = "https://webapp-telegram-backend.onrender.com"

def actualizar_imagen_api(image_id, image_url):
    """
    Actualiza la URL de una imagen en la API.

    Args:
        chat_id (str): El ID del chat donde se envía el mensaje.
        image_url (str): La URL de la nueva imagen.

    Returns:
        dict: Respuesta de la API.
    """
    try:
        # Realizar solicitud PUT a la API
        response = requests.put(
            f"{API_BASE_URL}/images/{image_id}",
            json={"url": image_url}
        )

        # Validar el código de estado de la respuesta
        if response.status_code == 200:
            return response.json()  # Retorna la respuesta en formato JSON
        else:
            # Levantar una excepción si hay un error en la API
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Manejo de errores HTTP y de red
        return {"error": str(e)}
