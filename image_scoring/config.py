import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME") or os.getenv("GCS_BUCKET_NAME")
SCORE_THRESHOLD = int(os.getenv("SCORE_THRESHOLD", 45))
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", 1))
IMAGEN_MODEL = os.getenv("IMAGEN_MODEL", "gemini-3.1-flash-lite-image")
IMAGEN_REGION = os.getenv("IMAGEN_REGION", "global")
GENAI_MODEL = os.getenv("GENAI_MODEL", "gemini-3.5-flash")

