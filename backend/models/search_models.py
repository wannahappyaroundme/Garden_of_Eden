"""
WebSearch Models
Data structures for web search functionality
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SearchQuery(BaseModel):
    """Query for web search"""
    query_text: str
    max_results: int = Field(default=3, ge=1, le=10, description="Maximum number of search results")
    search_depth: str = Field(default="basic", description="Search depth: 'basic' or 'advanced'")

    class Config:
        json_schema_extra = {
            "example": {
                "query_text": "최신 머신러닝 트렌드 2024",
                "max_results": 3,
                "search_depth": "basic"
            }
        }


class SearchResult(BaseModel):
    """A single search result"""
    title: str
    url: str
    content: str
    score: Optional[float] = Field(default=None, description="Relevance score")
    published_date: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Machine Learning Trends 2024",
                "url": "https://example.com/ml-trends",
                "content": "The top machine learning trends for 2024 include...",
                "score": 0.95,
                "published_date": "2024-01-15"
            }
        }


class WebSearchResponse(BaseModel):
    """Response from web search"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    search_provider: str = Field(description="tavily, duckduckgo, etc.")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "최신 머신러닝 트렌드 2024",
                "results": [],
                "total_results": 3,
                "search_time_ms": 523.4,
                "search_provider": "tavily"
            }
        }


class SearchTriggerDecision(BaseModel):
    """Decision on whether to trigger web search"""
    should_search: bool
    reason: str
    detected_keywords: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

    class Config:
        json_schema_extra = {
            "example": {
                "should_search": True,
                "reason": "Query asks about current events or recent information",
                "detected_keywords": ["최신", "2024", "트렌드"],
                "confidence": 0.85
            }
        }
