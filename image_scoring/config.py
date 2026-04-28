import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME") or os.getenv("GCS_BUCKET_NAME")
SCORE_THRESHOLD = int(os.getenv("SCORE_THRESHOLD", 45))
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", 1))
IMAGEN_MODEL = os.getenv("IMAGEN_MODEL", "imagen-3.0-generate-002")
GENAI_MODEL = os.getenv("GENAI_MODEL", "gemini-2.5-flash")
