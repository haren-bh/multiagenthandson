import vertexai
from vertexai import agent_engines
from typing import Iterator, Dict, Any
import logging
import asyncio
import os
from dotenv import load_dotenv
# Load environment variables from image_scoring/.env
env_path = os.path.join(os.path.dirname(__file__), "..", "image_scoring", ".env")
load_dotenv(env_path)


async def call_agent_engine(
    prompt: str,
    project_id: str,
    location: str,
    staging_bucket: str,
    reasoning_engine_id: str,
    user_id: str = "user_123",
) -> Iterator[Dict[str, Any]]:
    """Initializes Vertex AI, gets a remote agent, creates a session, and streams a query.

    Args:
        prompt: The query to send to the agent.
        project_id: The Google Cloud project ID.
        location: The Google Cloud location for Vertex AI.
        staging_bucket: The GCS bucket for staging.
        reasoning_engine_id: The ID of the deployed agent engine.
        user_id: The ID for the user session.

    Yields:
        Events from the agent's streamed response.
    """
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=staging_bucket,
    )

    # Create a session service client
    remote_agent = agent_engines.get(reasoning_engine_id)
    print(remote_agent)
    remote_session=await remote_agent.async_create_session(user_id="u_456")

    async for event in remote_agent.async_stream_query(
        user_id="u_456",
        session_id=remote_session["id"],
        message=prompt,
    ):
        print(event)

    # Retrieve and print GCS image URIs from the session state
    try:
        from google.adk.sessions import VertexAiSessionService
        engine_id_short = reasoning_engine_id.split('/')[-1]
        session_service = VertexAiSessionService(
            project=project_id,
            location=location,
            agent_engine_id=engine_id_short
        )
        session = await session_service.get_session(
            app_name=engine_id_short,
            user_id="u_456",
            session_id=remote_session["id"]
        )
        if session and session.state:
            gcs_uris = [v for k, v in session.state.items() if k.startswith("generated_image_gcs_uri_")]
            if gcs_uris:
                print("\n" + "="*80)
                print("SUCCESS: Your generated image(s) can be found at the following Cloud Storage address(es):")
                for uri in gcs_uris:
                    print(f"  -> {uri}")
                print("="*80 + "\n")
            else:
                print("\nNo GCS image URIs found in the session state.")
    except Exception as e_state:
        print(f"\nCould not fetch session state from Vertex AI: {e_state}")

def get_agent_engine_list(project_id,location,staging_bucket):
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=staging_bucket,
    )
    engines=agent_engines.AgentEngine.list()
    logging.info(engines)
    return engines




PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("AGENT_ENGINE_LOCATION")
STAGING_BUCKET = f"gs://{os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET')}"

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Prompt the user for REASONING_ENGINE_ID
    print("\nPlease enter your REASONING_ENGINE_ID.")
    print("Hint: It looks like (projects/78833623456/locations/us-central1/reasoningEngines/1153697210060242944)")
    reasoning_engine_id = input("REASONING_ENGINE_ID: ").strip()

    # Prompt the user for the image prompt
    prompt = input("\nDescribe the image you want to create: ").strip()

    try:
        response_stream = asyncio.run(call_agent_engine(
            prompt=prompt,
            project_id=PROJECT_ID,
            location=LOCATION,
            staging_bucket=STAGING_BUCKET,
            reasoning_engine_id=reasoning_engine_id,
        ))
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)