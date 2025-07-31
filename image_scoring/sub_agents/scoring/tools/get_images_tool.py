from google.adk.tools import ToolContext


async def get_image(tool_context: ToolContext):
    try:
        
        artifact_name = (
            f"generated_image_" + str(tool_context.state.get("loop_iteration", 0)) + ".png"
        )
        artifact = await tool_context.load_artifact(artifact_name)
    


        return {
            "status": "success",
            "message": f"Image artifact {artifact_name} successfully loaded."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error loading artifact {artifact_name}: {str(e)}"
        }
