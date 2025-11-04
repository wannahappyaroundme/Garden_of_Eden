"""
Web Search Service
Provides web search capabilities using Tavily API (primary) and DuckDuckGo (fallback)
"""
import os
import time
from typing import Optional
from tavily import TavilyClient
from duckduckgo_search import DDGS

from models.search_models import SearchQuery, SearchResult, WebSearchResponse, SearchTriggerDecision
from utils.logger import get_logger

logger = get_logger(__name__)


class WebSearchService:
    """
    Service for web search using Tavily API (primary) and DuckDuckGo (fallback)
    """

    def __init__(self, tavily_api_key: Optional[str] = None):
        """
        Initialize web search service

        Args:
            tavily_api_key: Optional Tavily API key. If None, uses env var or falls back to DuckDuckGo
        """
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")

        if self.tavily_api_key:
            try:
                self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
                self.use_tavily = True
                logger.info("✅ Tavily client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Tavily: {e}. Falling back to DuckDuckGo")
                self.use_tavily = False
        else:
            logger.info("No Tavily API key found. Using DuckDuckGo for search")
            self.use_tavily = False

        # DuckDuckGo is always available as fallback
        self.ddg_client = DDGS()
        logger.info("✅ Web search service initialized")

    def should_trigger_search(self, user_message: str) -> SearchTriggerDecision:
        """
        Determine if web search should be triggered based on user message

        Args:
            user_message: User's message

        Returns:
            SearchTriggerDecision with reasoning
        """
        # Keywords that indicate need for current/recent information
        current_info_keywords = [
            "최신", "현재", "지금", "오늘", "요즘", "최근",
            "latest", "current", "now", "today", "recent",
            "2024", "2025", "올해", "this year"
        ]

        # Keywords that indicate factual/news queries
        factual_keywords = [
            "뉴스", "소식", "가격", "날씨", "주가",
            "news", "price", "weather", "stock"
        ]

        message_lower = user_message.lower()
        detected_keywords = []
        confidence = 0.0

        # Check for current info keywords
        for keyword in current_info_keywords:
            if keyword in message_lower:
                detected_keywords.append(keyword)
                confidence += 0.3

        # Check for factual keywords
        for keyword in factual_keywords:
            if keyword in message_lower:
                detected_keywords.append(keyword)
                confidence += 0.4

        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)

        should_search = confidence >= 0.3

        reason = ""
        if should_search:
            reason = "Query appears to request current/recent information or facts"
        else:
            reason = "Query seems to be about personal topics or concepts that don't require web search"

        return SearchTriggerDecision(
            should_search=should_search,
            reason=reason,
            detected_keywords=detected_keywords,
            confidence=confidence
        )

    async def search(self, query: SearchQuery) -> WebSearchResponse:
        """
        Perform web search using Tavily (primary) or DuckDuckGo (fallback)

        Args:
            query: Search query

        Returns:
            WebSearchResponse with results
        """
        start_time = time.time()

        try:
            if self.use_tavily:
                return await self._search_tavily(query, start_time)
            else:
                return await self._search_duckduckgo(query, start_time)
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            # Try fallback if Tavily fails
            if self.use_tavily:
                logger.info("Falling back to DuckDuckGo...")
                return await self._search_duckduckgo(query, start_time)
            else:
                # Return empty results
                search_time_ms = (time.time() - start_time) * 1000
                return WebSearchResponse(
                    query=query.query_text,
                    results=[],
                    total_results=0,
                    search_time_ms=search_time_ms,
                    search_provider="none"
                )

    async def _search_tavily(self, query: SearchQuery, start_time: float) -> WebSearchResponse:
        """Search using Tavily API"""
        try:
            response = self.tavily_client.search(
                query=query.query_text,
                max_results=query.max_results,
                search_depth=query.search_depth
            )

            results = []
            for item in response.get('results', []):
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    content=item.get('content', ''),
                    score=item.get('score'),
                    published_date=item.get('published_date')
                )
                results.append(result)

            search_time_ms = (time.time() - start_time) * 1000

            logger.info(f"🔍 Tavily search complete: {len(results)} results in {search_time_ms:.1f}ms")

            return WebSearchResponse(
                query=query.query_text,
                results=results,
                total_results=len(results),
                search_time_ms=search_time_ms,
                search_provider="tavily"
            )

        except Exception as e:
            logger.error(f"❌ Tavily search error: {e}")
            raise

    async def _search_duckduckgo(self, query: SearchQuery, start_time: float) -> WebSearchResponse:
        """Search using DuckDuckGo (free, no API key needed)"""
        try:
            # DuckDuckGo text search
            ddg_results = self.ddg_client.text(
                keywords=query.query_text,
                max_results=query.max_results
            )

            results = []
            for item in ddg_results:
                result = SearchResult(
                    title=item.get('title', ''),
                    url=item.get('href', ''),
                    content=item.get('body', ''),
                    score=None,  # DuckDuckGo doesn't provide scores
                    published_date=None
                )
                results.append(result)

            search_time_ms = (time.time() - start_time) * 1000

            logger.info(f"🔍 DuckDuckGo search complete: {len(results)} results in {search_time_ms:.1f}ms")

            return WebSearchResponse(
                query=query.query_text,
                results=results,
                total_results=len(results),
                search_time_ms=search_time_ms,
                search_provider="duckduckgo"
            )

        except Exception as e:
            logger.error(f"❌ DuckDuckGo search error: {e}")
            raise

    def format_search_results_for_prompt(self, search_response: WebSearchResponse) -> str:
        """
        Format search results for inclusion in LLM prompt

        Args:
            search_response: Search results

        Returns:
            Formatted string for prompt
        """
        if not search_response.results:
            return "No web search results available."

        lines = [f"Web Search Results for: \"{search_response.query}\""]
        lines.append(f"(Source: {search_response.search_provider}, {search_response.total_results} results)")
        lines.append("")

        for i, result in enumerate(search_response.results, 1):
            lines.append(f"{i}. {result.title}")
            lines.append(f"   {result.content[:200]}...")  # First 200 chars
            lines.append(f"   URL: {result.url}")
            lines.append("")

        return "\n".join(lines)
