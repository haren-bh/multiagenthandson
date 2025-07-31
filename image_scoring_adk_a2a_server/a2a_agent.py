from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

root_agent = RemoteA2aAgent(
    name="image_scoring",
    description="Agent to give interesting facts.",
    agent_card="http://localhost:8001/a2a/image_scoring/.well-known/agent.json",
    
    # Optional configurations
    timeout=300.0,          # HTTP timeout (seconds)
    httpx_client=None,      # Custom HTTP client
)