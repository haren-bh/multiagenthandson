from google.adk.tools import ToolContext


def set_score(tool_context: ToolContext, total_score: int) -> str:
    print(f"total scoreeee is {total_score}")
    tool_context.state["total_score"] = total_score
