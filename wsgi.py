"""Ponto de entrada da aplicação (usado pelo Flask e pelo Gunicorn)."""
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402  (precisa carregar o .env antes)

app = create_app()
