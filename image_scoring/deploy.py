import vertexai
from .agent import root_agent
import os
import glob # To easily find the wheel file

PROJECT_ID = "" #TODO change this 変更してください
LOCATION = "us-central1"
STAGING_BUCKET = "" #TODO change this　変更してください, 例: gs://bucket-name

from vertexai import agent_engines

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)


remote_app = agent_engines.create(
    agent_engine=root_agent,
    requirements=open(os.path.join(os.getcwd(), "requirements.txt")).readlines()+["./dist/image_scoring-0.1.0-py3-none-any.whl"],#TODO 確認
    extra_packages=[
        "./dist/image_scoring-0.1.0-py3-none-any.whl", #TODO 確認
    ]
)

print(remote_app.resource_name)
