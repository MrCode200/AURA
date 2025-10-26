from AppOpener import open, close

from tools import tool_registry
from tools.toolResult import ToolResult


@tool_registry.register_function()
def open_app(app_names: str | list[str]) -> dict:
    """
    Opens an application.
    :param app_names: The application name or a list of application names to open
    """
    try:
        open(app_names, match_closest=True, throw_error=True)
        return ToolResult(
            status="success",
            message=f"{app_names} opened successfully",
        ).model_dump()

    except Exception as e:
        return ToolResult(
            status="error",
            message=f"Failed to open {app_names}",
            error=str(e)
        ).model_dump()

@tool_registry.register_function()
def close_app(app_names: str | list[str]) -> dict:
    """
    Closes an application.
    :param app_names: The application name or a list of application names to close
    """
    try:
        close(app_names, match_closest=True, throw_error=True)
        return ToolResult(
            status="success",
            message=f"{app_names} closed successfully"
        ).model_dump()

    except Exception as e:
        return ToolResult(
            status="error",
            message=f"Failed to close {app_names}",
            error=str(e)
        ).model_dump()
