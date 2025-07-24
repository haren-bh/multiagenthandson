import vertexai
from agent import root_agent

PROJECT_ID = "datapipeline-372305" #change this
LOCATION = "us-central1"
STAGING_BUCKET = "gs://haren-genai-data" #change this


from vertexai import agent_engines

#remote agents.
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ]
)

print(remote_app.resource_name)
