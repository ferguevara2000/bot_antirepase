import base64
import requests  # Para realizar solicitudes HTTP
from config import API_URL, API_KEY

def insertar_imagen(new_image_base64, user_id):
    try:
        # Realizar solicitud POST a la API
        response = requests.post(
            f"{API_URL}/insert_image",
            json={"image": new_image_base64,
                  "user_id_input": user_id},
            headers={
                "Content-Type": "application/json",
                "apikey": API_KEY,
                "Authorization": f"Bearer {API_KEY}"
            }
        )

        # Validar el código de estado de la respuesta
        if response.status_code in [200, 204]:
            print("Imagen ingresada correctamente.")

            # Verificar si hay contenido en la respuesta
            if response.text.strip():  # Si la respuesta no está vacía
                return response.json()  # Retorna el contenido en formato JSON
            else:
                return {"message": "Imagen ingresada correctamente, pero no hay contenido en la respuesta."}
        else:
            print(f"Error al ingresar la imagen: {response.status_code}, {response.text}")
            return {"error": response.text, "status_code": response.status_code}

    except Exception as e:
        print(f"Excepción ocurrida: {e}")
        return {"error": str(e)}

def delete_image(user_id):
    try:
        # Realizar solicitud POST a la API
        response = requests.post(
            f"{API_URL}/delete_oldest_image",
            json={"p_user_id": user_id},
            headers={
                "Content-Type": "application/json",
                "apikey": API_KEY,
                "Authorization": f"Bearer {API_KEY}"
            }
        )

        # Validar el código de estado de la respuesta
        if response.status_code in [200, 204]:
            print("Imagen eliminada correctamente.")

            # Verificar si hay contenido en la respuesta
            if response.text.strip():  # Si la respuesta no está vacía
                return response.json()  # Retorna el contenido en formato JSON
            else:
                return {"message": "Imagen eliminada correctamente, pero no hay contenido en la respuesta."}
        else:
            print(f"Error al eliminar la imagen: {response.status_code}, {response.text}")
            return {"error": response.text, "status_code": response.status_code}

    except Exception as e:
        print(f"Excepción ocurrida: {e}")
        return {"error": str(e)}

def get_image(user_id):
    try:
        # Realizar solicitud POST a la API
        response = requests.post(
            f"{API_URL}/get_oldest_image",
            json={"p_user_id": user_id},
            headers={
                "Content-Type": "application/json",
                "apikey": API_KEY,
                "Authorization": f"Bearer {API_KEY}"
            }
        )

        # Validar el código de estado de la respuesta
        if response.status_code in [200, 204]:
            print("Imagen obtenida correctamente.")

            # Verificar si hay contenido en la respuesta
            if response.text.strip():  # Si la respuesta no está vacía
                return response.json()  # Retorna el contenido en formato JSON
            else:
                return {"message": "Imagen obtenida correctamente, pero no hay contenido en la respuesta."}
        else:
            print(f"Error al obtener la imagen: {response.status_code}, {response.text}")
            return {"error": response.text, "status_code": response.status_code}

    except Exception as e:
        print(f"Excepción ocurrida: {e}")
        return {"error": str(e)}
