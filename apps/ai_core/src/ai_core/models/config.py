from pydantic import BaseModel
from typing import List, Optional

class Config(BaseModel):
    id: str
    port: int
    work_dir: str
    log_level: str
    deepgram_api_key: str
