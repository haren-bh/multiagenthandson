import vertexai
from image_scoring.agent import root_agent
import os
import glob # To easily find the wheel file
from dotenv import load_dotenv, dotenv_values

# Load environment variables from image_scoring/.env
env_path = os.path.join(os.path.dirname(__file__), "..", "image_scoring", ".env")
load_dotenv(env_path)
deploy_env_vars = {k: str(v) for k, v in dotenv_values(env_path).items() if v is not None}

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = f"gs://{os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET')}"

from vertexai import agent_engines

client=vertexai.Client(
    project=PROJECT_ID,
    location=LOCATION,
)


remote_app = client.agent_engines.create(
    agent=root_agent,
    config={
        "display_name": "image-scoring",
        "staging_bucket": STAGING_BUCKET,
        "requirements": open(os.path.join(os.getcwd(), "requirements.txt")).readlines() + ["./dist/image_scoring-0.1.0-py3-none-any.whl"],
        "extra_packages": [
            "./dist/image_scoring-0.1.0-py3-none-any.whl",
        ],
        "env_vars": deploy_env_vars
    }
)

print(f"DEBUG: AgentEngine attributes: {dir(remote_app)}")
try:
    print(remote_app.api_resource.name)
except AttributeError:
    print("Could not find resource_name, check DEBUG output above.")
