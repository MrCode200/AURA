from typing import Literal, Optional, Any
from pydantic import BaseModel

class ToolResponse(BaseModel):
    """
    A response from a tool.
    :param status: The status of the tool response
    :param message: The message of the tool response
    :param details: The details of the tool response
    :param error: The error of the tool response
    :param metadata: The metadata of the tool response.
    """
    status: Literal["success", "pending", "cancelled", "error"]
    message: Optional[str] = None
    details: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None