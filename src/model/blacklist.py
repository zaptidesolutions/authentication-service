from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BlacklistTokenDTO(BaseModel):
    token: str = Field(..., description="The access token that has been blacklisted")
    revoked_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="The time when the token was revoked"
    )
