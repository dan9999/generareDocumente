#pip install python-dotenv
import os
from dotenv import load_dotenv

load_dotenv()  # încarcă variabilele din .env
HF_TOKEN = os.getenv("OPENAI_API_KEY")