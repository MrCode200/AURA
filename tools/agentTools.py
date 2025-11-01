from tools import tool_registry
from tools.toolResponse import ToolResponse

#@tool_registry.register_function()
# TODO: under development, not working
def stop_agent():
    """This stops the agent from running. This should be called at the end of the action chaine, after all tools have been called."""
    import src.main

    try:
        src.main.agent.stop()
        return ToolResponse(
            status="success",
            message="Agent stopped successfully.",
        )
    except Exception as e:
        return ToolResponse(
            status="error",
            message="Failed to stop agent.",
            error=str(e)
        )