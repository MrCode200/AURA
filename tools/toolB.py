from tools import tool_registry

@tool_registry.register_function()
def tool_b():
    """Ignore this Tool!"""
    return "Tool B"