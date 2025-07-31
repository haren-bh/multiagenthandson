import vertexai
from .agent import root_agent
import os
import glob # To easily find the wheel file

PROJECT_ID = "datapipeline-372305" #change this
LOCATION = "us-central1"
STAGING_BUCKET = "gs://haren-genai-data" #change this

from vertexai import agent_engines

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=open(os.path.join(os.getcwd(), "requirements.txt")).readlines()+["Users/bharen/code/cloud/Agents/image-scoring/image_scoring/dist/image_scoring-0.1.0-py3-none-any.whl"],
    extra_packages=[
        "/Users/bharen/code/cloud/Agents/image-scoring/image_scoring/dist/image_scoring-0.1.0-py3-none-any.whl", # Add the GCS URI of your wheel file
    ]
)

print(remote_app.resource_name)
