# 🛠️ Creating Tools for the Agent

Extend the agent’s capabilities by creating **custom tools**! Tools are Python functions that the agent can **discover, register, and execute dynamically**. By following these guidelines, your tools will be **reliable, efficient, and agent-friendly**.

---

## 1️⃣ Mandatory Imports

Every tool file must include:

```python
from tools import tool_registry  # Required for agent discovery
from tools.toolResponse import ToolResponse  # Standardized output


@tool_registry.register_function()
def example_tool(param: str) -> dict:
    """
    A brief description of what the tool does.

    :param param: Explain the input in a simple, clear way
    :return: A dictionary containing status, message, and optional metadata
    """
    try:
        # Tool logic here
        result = f"Processed {param}"
        return ToolResponse(
            status="success",
            message=result
        ).model_dump()
    except Exception as e:
        return ToolResponse(
            status="error",
            message="Failed to process the input",
            error=str(e)
        ).model_dump()
```
## 🧩 ToolResult: Standardized Output

All tools should return a `ToolResult`. This ensures the agent can handle responses consistently.

`ToolResult` arguments:

- **status (required)** — "success" | "pending" | "error"
- **message** (required) — human-readable summary
- **details** (optional) — dictionary with extra info, e.g., {"attempted_action": "open_app"}
- **error** (optional) — string description of what went wrong
- **metadata** (optional) — structured data for the agent, e.g., {"app_version": "1.2.3"}

💡 Tip: Always provide message and meaningful error details for better agent understanding.