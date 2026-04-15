from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_core.documents import Document


class RAGState(BaseModel):
    query: str
    documents: List[Document] = []   # 🔥 CHANGE HERE
    answer: str = ""
    critique: Dict[str, Any] = {}
    iteration: int = 0
    max_iterations: int = 1