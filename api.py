import base64
import requests  # Para realizar solicitudes HTTP
from config import API_URL, API_KEY

# URL base de la API
API_BASE_URL = f"{API_URL}/update_image"


def actualizar_imagen_api(image_id, new_image_base64):
    try:
        # Realizar solicitud POST a la API
        response = requests.post(
            API_BASE_URL,
            json={"image_id": image_id, "new_image_data": new_image_base64},
            headers={
                "Content-Type": "application/json",
                "apikey": API_KEY,
                "Authorization": f"Bearer {API_KEY}"
            }
        )

        # Validar el código de estado de la respuesta
        if response.status_code in [200, 204]:
            print("Imagen actualizada correctamente.")

            # Verificar si hay contenido en la respuesta
            if response.text.strip():  # Si la respuesta no está vacía
                return response.json()  # Retorna el contenido en formato JSON
            else:
                return {"message": "Imagen actualizada correctamente, pero no hay contenido en la respuesta."}
        else:
            print(f"Error al actualizar la imagen: {response.status_code}, {response.text}")
            return {"error": response.text, "status_code": response.status_code}

    except Exception as e:
        print(f"Excepción ocurrida: {e}")
        return {"error": str(e)}

