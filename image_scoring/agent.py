import datetime, uuid
from zoneinfo import ZoneInfo
from .sub_agents.prompt import image_generation_prompt_agent 
from .sub_agents.image import image_generation_agent 
from .sub_agents.scoring import scoring_images_prompt 
from .checker_agent import checker_agent_instance
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext


def set_session(callback_context: CallbackContext):
    """
    Sets a unique ID and timestamp in the callback context's state.
    This function is called before the main_loop_agent executes.
    """

    callback_context.state["unique_id"] = str(uuid.uuid4())
    callback_context.state["timestamp"] = datetime.datetime.now(
        ZoneInfo("UTC")
    ).isoformat()


# This agent is responsible for generating and scoring images based on input text.
# It uses a sequential process to:
# 1. Create an image generation prompt from the input text
# 2. Generate images using the prompt
# 3. Score the generated images
# The process continues until either:
# - The image score meets the quality threshold
# - The maximum number of iterations is reached

image_generation_scoring_agent = SequentialAgent(
    name="image_generation_scoring_agent",

    description=(
        """
        Analyzes a input text and creates the image generation prompt, generates the relevant images with imagen3 and scores the images."
        1. Invoke the image_generation_prompt_agent agent to generate the prompt for generating images
        2. Invoke the image_generation_agent agent to generate the images
        3. Invoke the scoring_images_prompt agent to score the images
            """
    ),
    sub_agents=[image_generation_prompt_agent, image_generation_agent, scoring_images_prompt],
)


# --- 5. Define the Loop Agent ---
# The LoopAgent will repeatedly execute its sub_agents in the order they are listed.
# It will continue looping until one of its sub_agents (specifically, the checker_agent's tool)
# sets tool_context.actions.escalate = True.
image_scoring = LoopAgent(
    name="image_scoring",
    description="Repeatedly runs a sequential process and checks a termination condition.",
    sub_agents=[
        image_generation_scoring_agent,  # First, run your sequential process [1]
        checker_agent_instance,  # Second, check the condition and potentially stop the loop [1]
    ],
    before_agent_callback=set_session,
)
root_agent = image_scoring
