"""
Search API for AI Chat Assistant

REST API endpoints for advanced search across conversations, files, and notes.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from backend.services.search_service import SearchService
from backend.models.search import (
    SearchQuery, SearchResults, SearchResult, SearchIndex,
    SearchSuggestion, AdvancedSearchQuery, SearchAnalytics,
    SearchScope, SearchType
)

# Create router
router = APIRouter(prefix="/api/search", tags=["search"])

# Dependency to get search service
def get_search_service() -> SearchService:
    """Dependency to get search service instance"""
    return SearchService()


@router.post("/", response_model=SearchResults)
async def search(
    search_query: SearchQuery,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Perform search across conversations, files, and notes.

    - **query**: Search query string
    - **search_type**: Type of search (exact, fuzzy, semantic, regex)
    - **scope**: What to search (all, conversations, files, notes)
    - **filters**: Additional filter criteria
    - **limit**: Maximum number of results (default: 50)
    - **offset**: Results offset for pagination (default: 0)
    - **sort_by**: Sort field (relevance, date, type)
    - **sort_order**: Sort order (asc, desc)
    """
    try:
        return search_service.search(search_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/advanced", response_model=SearchResults)
async def advanced_search(
    advanced_query: AdvancedSearchQuery,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Perform advanced search with multiple criteria and exclusions.

    - **queries**: Multiple search queries (AND logic)
    - **exclude_terms**: Terms to exclude from results
    - **exact_phrases**: Exact phrases that must be present
    - **filters**: Additional filter criteria
    - **limit**: Maximum number of results
    - **offset**: Results offset for pagination
    """
    try:
        return search_service.advanced_search(advanced_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced search failed: {str(e)}")


@router.get("/suggest", response_model=List[SearchSuggestion])
async def get_suggestions(
    q: str = Query(..., description="Partial search query"),
    limit: int = Query(5, description="Maximum number of suggestions"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Get search suggestions based on partial query.

    - **q**: Partial search query string
    - **limit**: Maximum number of suggestions to return
    """
    try:
        return search_service.get_search_suggestions(q, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.post("/index/build")
async def build_index(
    scope: SearchScope = SearchScope.ALL,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Build search index for specified scope.

    - **scope**: What to index (all, conversations, files, notes)
    """
    try:
        index = search_service.build_index(scope)
        return {
            "message": f"Search index built successfully",
            "index": index.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build index: {str(e)}")


@router.get("/indices", response_model=List[SearchIndex])
async def list_indices(
    search_service: SearchService = Depends(get_search_service)
):
    """
    List all available search indices.
    """
    try:
        return search_service.list_indices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list indices: {str(e)}")


@router.delete("/index/{index_id}")
async def clear_index(
    index_id: str,
    search_service: SearchService = Depends(get_search_service)
):
    """
    Clear a specific search index.

    - **index_id**: ID of the index to clear
    """
    try:
        search_service.clear_index(index_id)
        return {"message": f"Search index {index_id} cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {str(e)}")


@router.delete("/indices")
async def clear_all_indices(
    search_service: SearchService = Depends(get_search_service)
):
    """
    Clear all search indices.
    """
    try:
        search_service.clear_index()
        return {"message": "All search indices cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear indices: {str(e)}")


@router.get("/analytics", response_model=SearchAnalytics)
async def get_analytics(
    search_service: SearchService = Depends(get_search_service)
):
    """
    Get search usage analytics.
    """
    try:
        return search_service.get_analytics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.get("/quick")
async def quick_search(
    q: str = Query(..., description="Search query"),
    scope: SearchScope = Query(SearchScope.ALL, description="Search scope"),
    limit: int = Query(10, description="Maximum results"),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Quick search with simplified parameters.

    - **q**: Search query string
    - **scope**: What to search (all, conversations, files, notes)
    - **limit**: Maximum number of results
    """
    try:
        search_query = SearchQuery(
            query=q,
            scope=scope,
            limit=limit,
            search_type=SearchType.SEMANTIC
        )
        results = search_service.search(search_query)
        return {
            "query": q,
            "total_results": results.total_results,
            "results": [result.model_dump() for result in results.results[:limit]],
            "search_time": results.search_time
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Quick search failed: {str(e)}")