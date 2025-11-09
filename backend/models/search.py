"""
Search Models for AI Chat Assistant

Data models for search functionality across conversations, files, and notes.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum
import uuid


class SearchType(str, Enum):
    """Types of search operations"""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    REGEX = "regex"


class SearchScope(str, Enum):
    """What to search across"""
    ALL = "all"
    CONVERSATIONS = "conversations"
    FILES = "files"
    NOTES = "notes"


class SearchResultType(str, Enum):
    """Type of search result"""
    CONVERSATION = "conversation"
    MESSAGE = "message"
    FILE = "file"
    NOTE = "note"


class SearchFilter(BaseModel):
    """Search filter criteria"""
    model_config = ConfigDict(from_attributes=True)

    date_from: Optional[datetime] = Field(None, description="Start date for search")
    date_to: Optional[datetime] = Field(None, description="End date for search")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    project_id: Optional[str] = Field(None, description="Filter by project ID")
    ai_provider: Optional[str] = Field(None, description="Filter by AI provider")
    file_types: Optional[List[str]] = Field(None, description="Filter by file extensions")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    min_score: Optional[float] = Field(None, description="Minimum relevance score (0-1)")


class SearchQuery(BaseModel):
    """Search query parameters"""
    model_config = ConfigDict(from_attributes=True)

    query: str = Field(..., description="Search query string")
    search_type: SearchType = Field(SearchType.SEMANTIC, description="Type of search")
    scope: SearchScope = Field(SearchScope.ALL, description="What to search")
    filters: Optional[SearchFilter] = Field(None, description="Additional filters")
    limit: int = Field(50, description="Maximum number of results")
    offset: int = Field(0, description="Results offset for pagination")
    sort_by: str = Field("relevance", description="Sort field: relevance, date, type")
    sort_order: str = Field("desc", description="Sort order: asc, desc")


class SearchResult(BaseModel):
    """Individual search result"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique result identifier")
    type: SearchResultType = Field(..., description="Type of result")
    title: str = Field(..., description="Display title")
    content: str = Field(..., description="Content snippet or preview")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")
    source_id: str = Field(..., description="ID of the source item")
    source_type: str = Field(..., description="Type of source (conversation, file, note)")
    highlights: Optional[List[str]] = Field(None, description="Highlighted matching text")


class SearchResults(BaseModel):
    """Search results container"""
    model_config = ConfigDict(from_attributes=True)

    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of matching results")
    results: List[SearchResult] = Field(default_factory=list, description="Search results")
    search_time: float = Field(..., description="Search execution time in seconds")
    facets: Optional[Dict[str, Any]] = Field(None, description="Search facets for filtering")


class SearchIndex(BaseModel):
    """Search index metadata"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Index identifier")
    name: str = Field(..., description="Index name")
    scope: SearchScope = Field(..., description="Index scope")
    total_documents: int = Field(0, description="Total indexed documents")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last index update")
    status: str = Field("active", description="Index status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Index metadata")


class SearchSuggestion(BaseModel):
    """Search suggestion"""
    model_config = ConfigDict(from_attributes=True)

    text: str = Field(..., description="Suggested search text")
    type: str = Field(..., description="Suggestion type (query, correction, related)")
    confidence: float = Field(..., description="Suggestion confidence score")


class AdvancedSearchQuery(BaseModel):
    """Advanced search with multiple criteria"""
    model_config = ConfigDict(from_attributes=True)

    queries: List[str] = Field(..., description="Multiple search queries (AND logic)")
    exclude_terms: Optional[List[str]] = Field(None, description="Terms to exclude")
    exact_phrases: Optional[List[str]] = Field(None, description="Exact phrases to match")
    filters: Optional[SearchFilter] = Field(None, description="Additional filters")
    limit: int = Field(50, description="Maximum number of results")
    offset: int = Field(0, description="Results offset for pagination")


class SearchAnalytics(BaseModel):
    """Search usage analytics"""
    model_config = ConfigDict(from_attributes=True)

    total_searches: int = Field(0, description="Total number of searches performed")
    average_results: float = Field(0.0, description="Average number of results per search")
    popular_queries: List[Dict[str, Any]] = Field(default_factory=list, description="Most popular search queries")
    search_types_usage: Dict[str, int] = Field(default_factory=dict, description="Usage by search type")
    average_search_time: float = Field(0.0, description="Average search execution time")
    period_start: datetime = Field(..., description="Analytics period start")
    period_end: datetime = Field(..., description="Analytics period end")