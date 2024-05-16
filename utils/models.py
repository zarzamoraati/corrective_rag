from pydantic import BaseModel
from fastapi import UploadFile,Form
from typing import Annotated

class CorrectiveItems(BaseModel):
    
    pdf:UploadFile
    question:Annotated[str,Form()]
