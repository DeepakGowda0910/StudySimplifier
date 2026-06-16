from pydantic import BaseModel
from typing import Optional, List

class GenerateRequest(BaseModel):
    tool: str
    chapter: str
    topic: Optional[str] = None
    subject: Optional[str] = None
    board: Optional[str] = None
    course: Optional[str] = None
    stream: Optional[str] = None
    language: str = "English"
    style: str = "standard"

class GenerateResponse(BaseModel):
    content: str
    tool: str
    model_used: str
    xp_awarded: int = 10

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    socratic_mode: bool = False

class DocumentAnalyzeRequest(BaseModel):
    action: str = "summary"
    language: str = "English"

class StudyDataNode(BaseModel):
    name: str
    children: Optional[List['StudyDataNode']] = None
