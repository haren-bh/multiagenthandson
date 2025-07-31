from ... import config
from google.adk.agents import Agent
from .prompt import PROMPT
from ..tools.fetch_policy_tool import get_policy

image_generation_prompt_agent = Agent(
    name="image_generation_prompt_agent",
    model=config.GENAI_MODEL,
    description=("You are an expert in creating imagen3 prompts for image generation"),
    instruction=(PROMPT),
    tools=[get_policy],
    output_key="imagen_prompt",  # gets stored in session.state
)
