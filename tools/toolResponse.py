from typing import Literal, Optional, Any
from pydantic import BaseModel

class ToolResponse(BaseModel):
    status: Literal["success", "pending", "error"]
    message: Optional[str]
    details: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None