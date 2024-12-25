from flask import Flask
import os

def start_server():
    """Inicia un servidor Flask para cumplir con el requisito de Render."""
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "El bot está funcionando en Render."

    # Obtén el puerto de la variable de entorno o usa el puerto 5000 por defecto
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
