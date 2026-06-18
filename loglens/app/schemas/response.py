from datetime import datetime
from pydantic import BaseModel, ConfigDict

class LogFileResponse(BaseModel):
    id: str
    original_name: str
    content_hash: str
    uploaded_at: datetime
    is_duplicate: bool = False
    
    model_config = ConfigDict(from_attributes=True)