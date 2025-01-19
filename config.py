import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
WEB_LINK = os.getenv("WEB_LINK")
DEFAULT_MESSAGE = "Haz clic en el botón para desbloquear el contenido."
DEFAULT_IMAGE_URL = "https://via.placeholder.com/600x400.png?text=Desbloquear+Contenido"  # Imagen predeterminada
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")
