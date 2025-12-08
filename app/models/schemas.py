from pydantic import BaseModel
from pydantic import Field
from datetime import datetime
from typing   import Optional

#
class QueryResponse(BaseModel):
    user_id:    str      = Field(..., description="ID of the user associated with the request")
    request_id: str      = Field(..., description="Unique ID generated for this request")
    
    query: Optional[str] = Field(..., description="Original query sent by the user")
    
    resultado:  str      = Field(..., description="Processed result or system output")
    timestamp:  datetime = Field(..., description="Timestamp of request processing")