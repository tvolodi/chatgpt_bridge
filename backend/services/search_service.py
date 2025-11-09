"""
Search Service for AI Chat Assistant

Advanced search service for finding content across conversations, files, and notes
with filtering, ranking, and relevance scoring.
"""

import re
import time
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import math
import hashlib

from backend.models.search import (
    SearchQuery, SearchResults, SearchResult, SearchResultType,
    SearchFilter, SearchType, SearchScope, SearchIndex,
    SearchSuggestion, AdvancedSearchQuery, SearchAnalytics
)
from backend.models.conversation import ConversationContext, ConversationMessage
from backend.models.chat_session import ChatSession, Message
from backend.models.file_management import File, FileSummary, FileSearchRequest
from backend.services.conversation_service import ConversationService
from backend.services.file_management_service import FileManagementService
from backend.services.chat_session_service import ChatSessionService


class SearchService:
    """Advanced search service for AI Chat Assistant"""

    def __init__(self, base_path: str = None):
        """
        Initialize search service

        Args:
            base_path: Base directory for storing search indices. Defaults to user data directory.
        """
        if base_path is None:
            # Use platform-appropriate data directory
            if os.name == 'nt':  # Windows
                base_path = os.path.join(os.environ.get('APPDATA', ''), 'AI_Chat_Assistant')
            else:  # Unix-like systems
                base_path = os.path.join(os.path.expanduser('~'), '.local', 'share', 'ai_chat_assistant')

        self.base_path = Path(base_path)
        self.index_path = self.base_path / "search_index"
        self.analytics_path = self.base_path / "search_analytics"

        # Ensure directories exist
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.analytics_path.mkdir(parents=True, exist_ok=True)

        # Initialize services
        self.conversation_service = ConversationService()
        self.file_service = FileManagementService()
        self.chat_session_service = ChatSessionService()

        # Search analytics
        self.analytics_file = self.analytics_path / "analytics.json"
        self._load_analytics()

        # In-memory index for faster searching (in production, use a proper search engine)
        self.indices: Dict[str, SearchIndex] = {}
        self.document_store: Dict[str, Dict[str, Any]] = {}
        self.term_index: Dict[str, Set[str]] = defaultdict(set)  # term -> document_ids

    def _load_analytics(self):
        """Load search analytics from file"""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.analytics = SearchAnalytics(**data)
            except Exception:
                self.analytics = self._create_default_analytics()
        else:
            self.analytics = self._create_default_analytics()

    def _create_default_analytics(self) -> SearchAnalytics:
        """Create default analytics object"""
        return SearchAnalytics(
            total_searches=0,
            average_results=0.0,
            popular_queries=[],
            search_types_usage={},
            average_search_time=0.0,
            period_start=datetime.now(),
            period_end=datetime.now()
        )

    def _save_analytics(self):
        """Save search analytics to file"""
        try:
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(self.analytics.model_dump(), f, indent=2, default=str)
        except Exception:
            pass  # Don't fail search operations due to analytics save issues

    def _update_analytics(self, query: str, search_type: str, result_count: int, search_time: float):
        """Update search analytics"""
        self.analytics.total_searches += 1
        self.analytics.average_results = (
            (self.analytics.average_results * (self.analytics.total_searches - 1)) + result_count
        ) / self.analytics.total_searches
        self.analytics.average_search_time = (
            (self.analytics.average_search_time * (self.analytics.total_searches - 1)) + search_time
        ) / self.analytics.total_searches

        # Update search types usage
        self.analytics.search_types_usage[search_type] = (
            self.analytics.search_types_usage.get(search_type, 0) + 1
        )

        # Update popular queries
        query_found = False
        for q in self.analytics.popular_queries:
            if q['query'] == query:
                q['count'] += 1
                query_found = True
                break

        if not query_found:
            self.analytics.popular_queries.append({'query': query, 'count': 1})

        # Keep only top 10 popular queries
        self.analytics.popular_queries.sort(key=lambda x: x['count'], reverse=True)
        self.analytics.popular_queries = self.analytics.popular_queries[:10]

        self.analytics.period_end = datetime.now()
        self._save_analytics()

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for indexing and searching"""
        if not text:
            return []

        # Convert to lowercase and split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        # Remove common stop words
        stop_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                     'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'some', 'that', 'the',
                     'to', 'was', 'will', 'with', 'would'}
        return [token for token in tokens if token not in stop_words and len(token) > 1]

    def _calculate_relevance_score(self, query_terms: List[str], document_terms: List[str],
                                 document: Dict[str, Any]) -> float:
        """Calculate relevance score using TF-IDF like scoring"""
        if not query_terms or not document_terms:
            return 0.0

        # Term frequency in document
        doc_term_freq = defaultdict(int)
        for term in document_terms:
            doc_term_freq[term] += 1

        # Calculate score
        score = 0.0
        for query_term in query_terms:
            if query_term in doc_term_freq:
                # TF * IDF approximation (simplified)
                tf = doc_term_freq[query_term] / len(document_terms)
                # Simple IDF approximation based on document frequency
                df = len(self.term_index.get(query_term, set()))
                idf = math.log(max(1, len(self.document_store) / max(1, df))) + 1  # Add 1 to avoid zero
                score += tf * idf

        # Boost recent documents
        if 'created_at' in document and document['created_at']:
            try:
                created_date = datetime.fromisoformat(document['created_at'])
                days_old = (datetime.now() - created_date).days
                recency_boost = max(0.1, 1.0 / (1.0 + days_old / 30.0))  # Boost recent content
                score *= recency_boost
            except:
                pass

        return min(1.0, score)  # Cap at 1.0

    def _extract_highlights(self, text: str, query_terms: List[str], max_length: int = 200) -> List[str]:
        """Extract highlighted snippets from text"""
        if not text or not query_terms:
            return []

        highlights = []
        text_lower = text.lower()

        for term in query_terms:
            start = 0
            while True:
                pos = text_lower.find(term, start)
                if pos == -1:
                    break

                # Extract context around the match
                start_pos = max(0, pos - max_length // 2)
                end_pos = min(len(text), pos + len(term) + max_length // 2)

                snippet = text[start_pos:end_pos]
                if start_pos > 0:
                    snippet = "..." + snippet
                if end_pos < len(text):
                    snippet += "..."

                highlights.append(snippet)
                start = pos + 1

                if len(highlights) >= 3:  # Limit highlights per term
                    break

        return list(set(highlights))  # Remove duplicates

    def _index_chat_session(self, chat_session: ChatSession, messages: List[Message] = None) -> Dict[str, Any]:
        """Index a chat session for search"""
        content_parts = [
            chat_session.title or "",
            chat_session.description or "",
        ]

        # Add message content
        if messages:
            for message in messages:
                content_parts.extend([
                    message.content or "",
                    message.role or "",
                ])

        full_content = " ".join(content_parts)
        tokens = self._tokenize(full_content)

        doc = {
            'id': f"session_{chat_session.id}",
            'type': 'conversation',
            'title': chat_session.title or "Untitled Session",
            'content': full_content[:1000],  # Limit content for storage
            'tokens': tokens,
            'metadata': {
                'session_id': str(chat_session.id),
                'project_id': str(chat_session.project_id),
                'message_count': chat_session.message_count,
                'is_active': chat_session.is_active,
                'tags': getattr(chat_session, 'tags', []),
            },
            'created_at': chat_session.created_at.isoformat() if chat_session.created_at else None,
            'updated_at': chat_session.updated_at.isoformat() if chat_session.updated_at else None,
        }

        return doc

    def _index_file(self, file_obj: File, content: str = "") -> Dict[str, Any]:
        """Index a file for search"""
        tokens = self._tokenize(content)

        doc = {
            'id': f"file_{file_obj.id}",
            'type': 'file',
            'title': file_obj.filename,
            'content': content[:1000],  # Limit content for storage
            'tokens': tokens,
            'metadata': {
                'file_id': str(file_obj.id),
                'filename': file_obj.filename,
                'file_path': file_obj.file_path,
                'file_size': file_obj.metadata.size_bytes,
                'mime_type': file_obj.metadata.mime_type,
                'file_type': file_obj.metadata.file_type.value,
                'tags': file_obj.tags,
            },
            'created_at': file_obj.created_at.isoformat() if file_obj.created_at else None,
            'updated_at': file_obj.updated_at.isoformat() if file_obj.updated_at else None,
        }

        return doc

    def _index_note(self, note_id: str, title: str, content: str) -> Dict[str, Any]:
        """Index a note for search"""
        tokens = self._tokenize(content)

        doc = {
            'id': f"note_{note_id}",
            'type': 'note',
            'title': title,
            'content': content[:1000],  # Limit content for storage
            'tokens': tokens,
            'metadata': {
                'note_id': note_id,
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }

        return doc

    def build_index(self, scope: SearchScope = SearchScope.ALL) -> SearchIndex:
        """Build search index for specified scope"""
        start_time = time.time()

        index_id = f"{scope.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        documents = []

        try:
            if scope in [SearchScope.ALL, SearchScope.CONVERSATIONS]:
                # Index chat sessions
                chat_sessions = self.chat_session_service.list_sessions()
                for session in chat_sessions:
                    try:
                        # Get messages for this session
                        messages = self.chat_session_service.get_session_messages(session.id)
                        doc = self._index_chat_session(session, messages)
                        documents.append(doc)
                    except Exception as e:
                        print(f"Error indexing chat session {session.id}: {e}")

            if scope in [SearchScope.ALL, SearchScope.FILES]:
                # Index files
                search_request = FileSearchRequest(limit=1000)  # Get all files
                file_summaries = self.file_service.search_files(search_request)
                for file_summary in file_summaries:
                    try:
                        # Get full file object for content
                        file_obj = self.file_service.get_file(file_summary.id)
                        if not file_obj:
                            continue

                        # Try to read file content for indexing
                        content = ""
                        if file_obj.file_path and Path(file_obj.file_path).exists():
                            try:
                                with open(file_obj.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                            except:
                                pass  # Skip files that can't be read

                        doc = self._index_file(file_obj, content)
                        documents.append(doc)
                    except Exception as e:
                        print(f"Error indexing file {file_summary.id}: {e}")

            if scope in [SearchScope.ALL, SearchScope.NOTES]:
                # Index notes (from notes directory)
                notes_dir = Path("notes")
                if notes_dir.exists():
                    for note_file in notes_dir.glob("*.txt"):
                        try:
                            with open(note_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            doc = self._index_note(
                                note_id=str(note_file.stem),
                                title=note_file.stem.replace('_', ' ').title(),
                                content=content
                            )
                            documents.append(doc)
                        except Exception as e:
                            print(f"Error indexing note {note_file}: {e}")

            # Update in-memory index
            for doc in documents:
                self.document_store[doc['id']] = doc
                for token in doc['tokens']:
                    self.term_index[token].add(doc['id'])

            # Create index metadata
            index = SearchIndex(
                id=index_id,
                name=f"{scope.value.title()} Index",
                scope=scope,
                total_documents=len(documents),
                last_updated=datetime.now(),
                status="active",
                metadata={
                    'build_time': time.time() - start_time,
                    'document_types': list(set(doc['type'] for doc in documents))
                }
            )

            self.indices[index_id] = index
            return index

        except Exception as e:
            raise Exception(f"Failed to build search index: {str(e)}")

    def search(self, search_query: SearchQuery) -> SearchResults:
        """Perform search across indexed content"""
        start_time = time.time()

        try:
            # Tokenize query
            query_terms = self._tokenize(search_query.query)

            if not query_terms and search_query.search_type != SearchType.REGEX:
                return SearchResults(
                    query=search_query.query,
                    total_results=0,
                    results=[],
                    search_time=time.time() - start_time
                )

            # Find candidate documents
            candidate_docs = set()

            if search_query.search_type == SearchType.EXACT:
                # Exact term matching
                for term in query_terms:
                    candidate_docs.update(self.term_index.get(term, set()))

            elif search_query.search_type == SearchType.FUZZY:
                # Fuzzy matching (simple implementation)
                for term in query_terms:
                    # Check exact matches
                    candidate_docs.update(self.term_index.get(term, set()))
                    # Check similar terms (simple edit distance approximation)
                    for indexed_term in self.term_index.keys():
                        if len(indexed_term) == len(term) and sum(1 for a, b in zip(indexed_term, term) if a != b) <= 1:
                            candidate_docs.update(self.term_index[indexed_term])

            elif search_query.search_type == SearchType.REGEX:
                # Regex matching
                try:
                    pattern = re.compile(search_query.query, re.IGNORECASE)
                    for doc_id, doc in self.document_store.items():
                        if pattern.search(doc.get('content', '')) or pattern.search(doc.get('title', '')):
                            candidate_docs.add(doc_id)
                except:
                    return SearchResults(
                        query=search_query.query,
                        total_results=0,
                        results=[],
                        search_time=time.time() - start_time
                    )

            else:  # SEMANTIC (default)
                # For semantic search, use term overlap as approximation
                for term in query_terms:
                    candidate_docs.update(self.term_index.get(term, set()))

            # Filter and score results
            scored_results = []

            for doc_id in candidate_docs:
                doc = self.document_store.get(doc_id)
                if not doc:
                    continue

                # Apply filters
                if not self._matches_filters(doc, search_query.filters):
                    continue

                # Calculate relevance score
                score = self._calculate_relevance_score(query_terms, doc.get('tokens', []), doc)

                if search_query.filters and search_query.filters.min_score and score < search_query.filters.min_score:
                    continue

                # Create result
                result = SearchResult(
                    id=doc_id,
                    type=SearchResultType(doc['type']),
                    title=doc['title'],
                    content=doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'],
                    relevance_score=score,
                    metadata=doc['metadata'],
                    created_at=doc.get('created_at'),
                    updated_at=doc.get('updated_at'),
                    source_id=doc['metadata'].get(f"{doc['type']}_id", doc_id),
                    source_type=doc['type'],
                    highlights=self._extract_highlights(doc['content'], query_terms)
                )

                scored_results.append((score, result))

            # Sort results
            if search_query.sort_by == "relevance":
                scored_results.sort(key=lambda x: x[0], reverse=search_query.sort_order == "desc")
            elif search_query.sort_by == "date":
                scored_results.sort(
                    key=lambda x: x[1].created_at or datetime.min,
                    reverse=search_query.sort_order == "desc"
                )

            # Apply pagination
            total_results = len(scored_results)
            start_idx = search_query.offset
            end_idx = start_idx + search_query.limit
            paginated_results = [result for _, result in scored_results[start_idx:end_idx]]

            # Calculate facets
            facets = self._calculate_facets([doc_id for doc_id in candidate_docs if doc_id in self.document_store])

            search_time = time.time() - start_time

            # Update analytics
            self._update_analytics(
                search_query.query,
                search_query.search_type.value,
                total_results,
                search_time
            )

            return SearchResults(
                query=search_query.query,
                total_results=total_results,
                results=paginated_results,
                search_time=search_time,
                facets=facets
            )

        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")

    def _matches_filters(self, doc: Dict[str, Any], filters: Optional[SearchFilter]) -> bool:
        """Check if document matches search filters"""
        if not filters:
            return True

        try:
            # Date filters
            if filters.date_from or filters.date_to:
                doc_date = None
                if doc.get('created_at'):
                    try:
                        doc_date = datetime.fromisoformat(doc['created_at'])
                    except:
                        pass

                if doc_date:
                    if filters.date_from and doc_date < filters.date_from:
                        return False
                    if filters.date_to and doc_date > filters.date_to:
                        return False

            # User filter
            if filters.user_id and doc['metadata'].get('user_id') != filters.user_id:
                return False

            # Project filter
            if filters.project_id and doc['metadata'].get('project_id') != filters.project_id:
                return False

            # AI provider filter
            if filters.ai_provider and doc['metadata'].get('ai_provider') != filters.ai_provider:
                return False

            # File type filter
            if filters.file_types and doc['type'] == 'file':
                file_ext = doc['metadata'].get('filename', '').split('.')[-1].lower()
                if file_ext not in [ft.lower() for ft in filters.file_types]:
                    return False

            # Tags filter
            if filters.tags:
                doc_tags = set(doc['metadata'].get('tags', []))
                filter_tags = set(filters.tags)
                if not filter_tags.issubset(doc_tags):
                    return False

            return True

        except Exception:
            return False

    def _calculate_facets(self, doc_ids: List[str]) -> Dict[str, Any]:
        """Calculate search facets from result set"""
        facets = {
            'types': defaultdict(int),
            'users': defaultdict(int),
            'projects': defaultdict(int),
            'ai_providers': defaultdict(int),
            'file_types': defaultdict(int),
            'date_ranges': defaultdict(int)
        }

        for doc_id in doc_ids:
            doc = self.document_store.get(doc_id)
            if not doc:
                continue

            # Type facet
            facets['types'][doc['type']] += 1

            # User facet
            user_id = doc['metadata'].get('user_id')
            if user_id:
                facets['users'][user_id] += 1

            # Project facet
            project_id = doc['metadata'].get('project_id')
            if project_id:
                facets['projects'][project_id] += 1

            # AI provider facet
            ai_provider = doc['metadata'].get('ai_provider')
            if ai_provider:
                facets['ai_providers'][ai_provider] += 1

            # File type facet
            if doc['type'] == 'file':
                filename = doc['metadata'].get('filename', '')
                if '.' in filename:
                    ext = filename.split('.')[-1].lower()
                    facets['file_types'][ext] += 1

            # Date range facet
            if doc.get('created_at'):
                try:
                    created_date = datetime.fromisoformat(doc['created_at'])
                    if created_date > datetime.now() - timedelta(days=1):
                        facets['date_ranges']['today'] += 1
                    elif created_date > datetime.now() - timedelta(days=7):
                        facets['date_ranges']['this_week'] += 1
                    elif created_date > datetime.now() - timedelta(days=30):
                        facets['date_ranges']['this_month'] += 1
                    else:
                        facets['date_ranges']['older'] += 1
                except:
                    pass

        # Convert defaultdicts to regular dicts
        return {k: dict(v) for k, v in facets.items()}

    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[SearchSuggestion]:
        """Get search suggestions based on partial query"""
        suggestions = []

        if not partial_query:
            return suggestions

        partial_lower = partial_query.lower()

        # Get popular queries that start with partial query
        for query_data in self.analytics.popular_queries:
            query = query_data['query']
            if query.lower().startswith(partial_lower) and query != partial_query:
                suggestions.append(SearchSuggestion(
                    text=query,
                    type="popular",
                    confidence=min(1.0, query_data['count'] / max(1, self.analytics.total_searches))
                ))

        # Get terms from index that start with partial query
        matching_terms = [term for term in self.term_index.keys() if term.startswith(partial_lower)]
        for term in matching_terms[:limit]:
            if term != partial_query:
                # Calculate confidence based on document frequency
                confidence = len(self.term_index[term]) / max(1, len(self.document_store))
                suggestions.append(SearchSuggestion(
                    text=term,
                    type="term",
                    confidence=min(1.0, confidence)
                ))

        # Sort by confidence and limit
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:limit]

    def advanced_search(self, advanced_query: AdvancedSearchQuery) -> SearchResults:
        """Perform advanced search with multiple criteria"""
        # Convert to basic search query
        basic_query = SearchQuery(
            query=" ".join(advanced_query.queries),
            filters=advanced_query.filters,
            limit=advanced_query.limit,
            offset=advanced_query.offset
        )

        results = self.search(basic_query)

        # Apply additional filtering for advanced criteria
        if advanced_query.exclude_terms:
            exclude_set = set(term.lower() for term in advanced_query.exclude_terms)
            filtered_results = []
            for result in results.results:
                content_lower = result.content.lower()
                title_lower = result.title.lower()
                if not any(term in content_lower or term in title_lower for term in exclude_set):
                    filtered_results.append(result)
            results.results = filtered_results
            results.total_results = len(filtered_results)

        if advanced_query.exact_phrases:
            filtered_results = []
            for result in results.results:
                content_lower = result.content.lower()
                title_lower = result.title.lower()
                full_text = f"{title_lower} {content_lower}"
                if all(phrase.lower() in full_text for phrase in advanced_query.exact_phrases):
                    filtered_results.append(result)
            results.results = filtered_results
            results.total_results = len(filtered_results)

        return results

    def get_analytics(self) -> SearchAnalytics:
        """Get search analytics"""
        return self.analytics

    def clear_index(self, index_id: Optional[str] = None):
        """Clear search index"""
        if index_id:
            if index_id in self.indices:
                del self.indices[index_id]
        else:
            self.indices.clear()
            self.document_store.clear()
            self.term_index.clear()

    def list_indices(self) -> List[SearchIndex]:
        """List all search indices"""
        return list(self.indices.values())