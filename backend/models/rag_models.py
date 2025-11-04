"""
RAG (Retrieval-Augmented Generation) Models
Data structures for semantic search and conversation retrieval
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RetrievedConversation(BaseModel):
    """A conversation retrieved through semantic search"""
    conversation_id: str
    user_id: str
    similarity_score: float = Field(ge=0.0, le=1.0, description="Cosine similarity score")
    user_message: str
    ai_response: str
    created_at: datetime
    main_topic: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123",
                "user_id": "user_001",
                "similarity_score": 0.85,
                "user_message": "SLAM 알고리즘에 대해 알려줘",
                "ai_response": "SLAM (Simultaneous Localization and Mapping)은...",
                "created_at": "2024-01-15T10:30:00",
                "main_topic": "SLAM algorithms"
            }
        }


class RAGQuery(BaseModel):
    """Query for semantic search"""
    query_text: str
    user_id: str
    k: int = Field(default=5, ge=1, le=20, description="Number of results to retrieve")
    min_similarity: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum similarity threshold")

    class Config:
        json_schema_extra = {
            "example": {
                "query_text": "컴퓨터 비전 프로젝트를 어떻게 시작해야 할까?",
                "user_id": "user_001",
                "k": 5,
                "min_similarity": 0.5
            }
        }


class RAGSearchResult(BaseModel):
    """Result of a RAG semantic search"""
    query: str
    retrieved_conversations: List[RetrievedConversation]
    total_results: int
    search_time_ms: float

    class Config:
        json_schema_extra = {
            "example": {
                "query": "컴퓨터 비전 프로젝트 시작하기",
                "retrieved_conversations": [],
                "total_results": 3,
                "search_time_ms": 45.2
            }
        }
