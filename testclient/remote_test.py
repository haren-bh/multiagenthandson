import vertexai

PROJECT_ID = "datapipeline-372305"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://haren-genai-data"

from vertexai import agent_engines

reasoning_engine_id="projects/85469421903/locations/us-central1/reasoningEngines/7369674597261639680"

#remote agents.
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# Create a session service client
remote_agent = agent_engines.get(reasoning_engine_id)
print(remote_agent)
remote_session=remote_agent.create_session(user_id="u_456")

image_prompt="A cat riding a bicycle"

for event in remote_agent.stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message=image_prompt,
):
    print(event)