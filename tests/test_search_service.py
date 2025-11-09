"""
Tests for Search Service

Comprehensive tests for the search functionality across conversations, files, and notes.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from backend.services.search_service import SearchService
from backend.models.search import (
    SearchQuery, SearchResults, SearchResult, SearchResultType,
    SearchFilter, SearchType, SearchScope, SearchIndex,
    SearchSuggestion, AdvancedSearchQuery
)
from backend.models.conversation import ConversationContext, ConversationMessage
from backend.models.chat_session import ChatSession, Message
from backend.models.file_management import File, FileMetadata, FileType, FileSummary, FileStatus


class TestSearchService:
    """Test cases for SearchService"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def search_service(self, temp_dir):
        """Create search service instance with temp directory"""
        service = SearchService(base_path=str(temp_dir))
        return service

    def test_initialization(self, search_service):
        """Test search service initialization"""
        assert search_service.base_path.exists()
        assert search_service.index_path.exists()
        assert search_service.analytics_path.exists()
        assert isinstance(search_service.indices, dict)
        assert isinstance(search_service.document_store, dict)
        assert isinstance(search_service.term_index, dict)

    def test_tokenize(self, search_service):
        """Test text tokenization"""
        text = "Hello, this is a test message with some words!"
        tokens = search_service._tokenize(text)

        # Should not contain stop words
        assert "is" not in tokens
        assert "a" not in tokens
        assert "with" not in tokens
        assert "some" not in tokens

        # Should contain meaningful words
        assert "hello" in tokens
        assert "this" in tokens
        assert "test" in tokens
        assert "message" in tokens
        assert "words" in tokens

    def test_calculate_relevance_score(self, search_service):
        """Test relevance score calculation"""
        query_terms = ["test", "message"]
        document_terms = ["hello", "test", "message", "content"]
        document = {"created_at": datetime.now().isoformat()}

        score = search_service._calculate_relevance_score(query_terms, document_terms, document)
        assert 0.0 <= score <= 1.0

        # Score should be higher when query terms are present
        assert score > 0.0

    def test_extract_highlights(self, search_service):
        """Test highlight extraction"""
        text = "This is a long message containing test content for highlighting purposes."
        query_terms = ["test", "content"]

        highlights = search_service._extract_highlights(text, query_terms)
        assert isinstance(highlights, list)
        assert len(highlights) > 0

        # Should contain the query terms
        highlight_text = " ".join(highlights).lower()
        assert "test" in highlight_text or "content" in highlight_text

    @patch('backend.services.search_service.ChatSessionService')
    def test_index_chat_session(self, mock_session_service, search_service):
        """Test chat session indexing"""
        # Mock chat session
        message = Message(
            id=uuid4(),
            role="user",
            content="Hello, this is a test message",
            timestamp=datetime.now()
        )

        chat_session = ChatSession(
            id=uuid4(),
            project_id=uuid4(),
            title="Test Session",
            description="A test session",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            message_count=1
        )

        doc = search_service._index_chat_session(chat_session, [message])

        assert doc['id'] == f"session_{chat_session.id}"
        assert doc['type'] == "conversation"
        assert doc['title'] == "Test Session"
        assert "test" in doc['tokens']
        assert "message" in doc['tokens']
        assert doc['metadata']['session_id'] == str(chat_session.id)
        assert doc['metadata']['project_id'] == str(chat_session.project_id)

    @patch('backend.services.file_management_service.FileManagementService')
    def test_index_file(self, mock_file_service, search_service):
        """Test file indexing"""
        # Create file metadata
        metadata = FileMetadata(
            filename="test.txt",
            file_type=FileType.TEXT,
            mime_type="text/plain",
            size_bytes=100,
            checksum="test_checksum"
        )

        # Create file object
        file_obj = File(
            id=uuid4(),
            filename="test.txt",
            file_path="/path/to/test.txt",
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        content = "This is test file content with some important information."

        doc = search_service._index_file(file_obj, content)

        assert doc['id'] == f"file_{file_obj.id}"
        assert doc['type'] == "file"
        assert doc['title'] == "test.txt"
        assert "test" in doc['tokens']
        assert "content" in doc['tokens']
        assert doc['metadata']['file_id'] == str(file_obj.id)
        assert doc['metadata']['filename'] == "test.txt"

    def test_index_note(self, search_service):
        """Test note indexing"""
        doc = search_service._index_note("note1", "Test Note", "This is test note content.")

        assert doc['id'] == "note_note1"
        assert doc['type'] == "note"
        assert doc['title'] == "Test Note"
        assert "test" in doc['tokens']
        assert "note" in doc['tokens']
        assert "content" in doc['tokens']
        assert doc['metadata']['note_id'] == "note1"

    @patch('backend.services.search_service.ChatSessionService')
    @patch('backend.services.file_management_service.FileManagementService')
    def test_build_index(self, mock_file_service, mock_session_service, search_service):
        """Test index building"""
        mock_session_service.return_value.list_sessions.return_value = [
            ChatSession(
                id=uuid4(),
                project_id=uuid4(),
                title="Test Session",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                message_count=1
            )
        ]
        mock_session_service.return_value.get_session_messages.return_value = [
            Message(id=uuid4(), role="user", content="test content", timestamp=datetime.now())
        ]

        # Mock files
        metadata = FileMetadata(
            filename="test.txt",
            file_type=FileType.TEXT,
            mime_type="text/plain",
            size_bytes=100,
            checksum="test_checksum"
        )
        file_obj = File(
            id=uuid4(),
            filename="test.txt",
            file_path="/tmp/test.txt",
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_file_service.return_value.search_files.return_value = [
            FileSummary(
                id=file_obj.id,
                filename="test.txt",
                file_type=FileType.TEXT,
                size_bytes=100,
                status=FileStatus.PROCESSED,
                tags=[],
                created_at=datetime.now()
            )
        ]
        mock_file_service.return_value.get_file.return_value = file_obj

        index = search_service.build_index(SearchScope.ALL)

        assert isinstance(index, SearchIndex)
        assert index.scope == SearchScope.ALL
        assert index.total_documents > 0
        assert index.status == "active"

        # Check that documents were indexed
        assert len(search_service.document_store) > 0
        assert len(search_service.term_index) > 0

    def test_search_basic(self, search_service):
        """Test basic search functionality"""
        # Add some test documents
        search_service.document_store["doc1"] = {
            'id': 'doc1',
            'type': 'conversation',
            'title': 'Test Document',
            'content': 'This is a test document with some content',
            'tokens': ['this', 'test', 'document', 'with', 'some', 'content'],
            'metadata': {'user_id': 'user1'},
            'created_at': datetime.now().isoformat()
        }
        search_service.term_index['test'].add('doc1')
        search_service.term_index['content'].add('doc1')

        search_query = SearchQuery(query="test content")
        results = search_service.search(search_query)

        assert isinstance(results, SearchResults)
        assert results.query == "test content"
        assert len(results.results) > 0
        assert results.total_results > 0
        assert results.search_time > 0

        # Check first result
        result = results.results[0]
        assert isinstance(result, SearchResult)
        assert result.relevance_score > 0
        assert result.type == SearchResultType.CONVERSATION

    def test_search_with_filters(self, search_service):
        """Test search with filters"""
        # Add test documents
        search_service.document_store["doc1"] = {
            'id': 'doc1',
            'type': 'conversation',
            'title': 'Test Document',
            'content': 'This is a test document',
            'tokens': ['this', 'test', 'document'],
            'metadata': {'user_id': 'user1', 'project_id': 'proj1'},
            'created_at': datetime.now().isoformat()
        }
        search_service.document_store["doc2"] = {
            'id': 'doc2',
            'type': 'conversation',
            'title': 'Another Document',
            'content': 'This is another test document',
            'tokens': ['this', 'another', 'test', 'document'],
            'metadata': {'user_id': 'user2', 'project_id': 'proj1'},
            'created_at': datetime.now().isoformat()
        }

        for term in ['test', 'document', 'this', 'another']:
            search_service.term_index[term].update(['doc1', 'doc2'])

        # Search with user filter
        search_filter = SearchFilter(user_id="user1")
        search_query = SearchQuery(query="test", filters=search_filter)
        results = search_service.search(search_query)

        assert len(results.results) == 1
        assert results.results[0].source_id == "doc1"

    def test_search_exact_type(self, search_service):
        """Test exact search type"""
        # Add test document
        search_service.document_store["doc1"] = {
            'id': 'doc1',
            'type': 'conversation',
            'title': 'Test Document',
            'content': 'This is a test document with exact content',
            'tokens': ['this', 'test', 'document', 'with', 'exact', 'content'],
            'metadata': {},
            'created_at': datetime.now().isoformat()
        }
        search_service.term_index['test'].add('doc1')
        search_service.term_index['exact'].add('doc1')

        search_query = SearchQuery(query="test", search_type=SearchType.EXACT)
        results = search_service.search(search_query)

        assert len(results.results) > 0

    def test_search_fuzzy_type(self, search_service):
        """Test fuzzy search type"""
        # Add test document
        search_service.document_store["doc1"] = {
            'id': 'doc1',
            'type': 'conversation',
            'title': 'Test Document',
            'content': 'This is a test document',
            'tokens': ['this', 'test', 'document'],
            'metadata': {},
            'created_at': datetime.now().isoformat()
        }
        search_service.term_index['test'].add('doc1')
        search_service.term_index['document'].add('doc1')

        search_query = SearchQuery(query="tst", search_type=SearchType.FUZZY)  # Misspelled
        results = search_service.search(search_query)

        # Fuzzy search should still find results (basic implementation)
        assert isinstance(results, SearchResults)

    def test_search_regex_type(self, search_service):
        """Test regex search type"""
        # Add test document
        search_service.document_store["doc1"] = {
            'id': 'doc1',
            'type': 'conversation',
            'title': 'Test Document',
            'content': 'This is a test123 document',
            'tokens': ['this', 'test123', 'document'],
            'metadata': {},
            'created_at': datetime.now().isoformat()
        }

        search_query = SearchQuery(query=r"test\d+", search_type=SearchType.REGEX)
        results = search_service.search(search_query)

        assert len(results.results) > 0

    def test_search_pagination(self, search_service):
        """Test search pagination"""
        # Add multiple test documents
        for i in range(5):
            doc_id = f"doc{i}"
            search_service.document_store[doc_id] = {
                'id': doc_id,
                'type': 'conversation',
                'title': f'Test Document {i}',
                'content': f'This is test content {i}',
                'tokens': ['this', 'test', 'content'],
                'metadata': {},
                'created_at': datetime.now().isoformat()
            }
            search_service.term_index['test'].add(doc_id)

        # Search with pagination
        search_query = SearchQuery(query="test", limit=2, offset=1)
        results = search_service.search(search_query)

        assert len(results.results) == 2
        assert results.total_results == 5

    def test_get_search_suggestions(self, search_service):
        """Test search suggestions"""
        # Add some terms to index
        search_service.term_index['test'].update(['doc1', 'doc2'])
        search_service.term_index['testing'].update(['doc3'])
        search_service.term_index['content'].update(['doc1'])

        # Add some popular queries to analytics
        search_service.analytics.popular_queries = [
            {'query': 'test query', 'count': 10},
            {'query': 'content search', 'count': 5}
        ]

        suggestions = search_service.get_search_suggestions("te", 3)

        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3

        # Should include popular queries and terms
        suggestion_texts = [s.text for s in suggestions]
        assert any('test' in text for text in suggestion_texts)

    def test_advanced_search(self, search_service):
        """Test advanced search"""
        # Add test documents
        search_service.document_store["doc1"] = {
            'id': 'doc1',
            'type': 'conversation',
            'title': 'Test Document',
            'content': 'This is a test document with important content',
            'tokens': ['this', 'test', 'document', 'with', 'important', 'content'],
            'metadata': {},
            'created_at': datetime.now().isoformat()
        }
        search_service.document_store["doc2"] = {
            'id': 'doc2',
            'type': 'conversation',
            'title': 'Another Document',
            'content': 'This is another document without the important content',
            'tokens': ['this', 'another', 'document', 'without', 'important', 'content'],
            'metadata': {},
            'created_at': datetime.now().isoformat()
        }

        for term in ['test', 'document', 'content', 'important', 'another', 'this', 'with', 'without']:
            search_service.term_index[term].update(['doc1', 'doc2'])

        advanced_query = AdvancedSearchQuery(
            queries=["test", "content"],
            exclude_terms=["another"],
            exact_phrases=["important content"]
        )

        results = search_service.advanced_search(advanced_query)

        assert isinstance(results, SearchResults)
        # Should find doc1 but not doc2 (excluded "another")
        assert len(results.results) >= 1

    def test_calculate_facets(self, search_service):
        """Test facet calculation"""
        # Add test documents
        search_service.document_store["doc1"] = {
            'id': 'doc1',
            'type': 'conversation',
            'title': 'Test Conversation',
            'content': 'Test content',
            'tokens': ['test', 'content'],
            'metadata': {
                'user_id': 'user1',
                'project_id': 'proj1',
                'ai_provider': 'openai'
            },
            'created_at': datetime.now().isoformat()
        }
        search_service.document_store["doc2"] = {
            'id': 'doc2',
            'type': 'file',
            'title': 'test.txt',
            'content': 'File content',
            'tokens': ['file', 'content'],
            'metadata': {
                'filename': 'test.txt',
                'user_id': 'user2'
            },
            'created_at': datetime.now().isoformat()
        }

        facets = search_service._calculate_facets(['doc1', 'doc2'])

        assert 'types' in facets
        assert 'users' in facets
        assert facets['types']['conversation'] == 1
        assert facets['types']['file'] == 1
        assert facets['users']['user1'] == 1
        assert facets['users']['user2'] == 1

    def test_get_analytics(self, search_service):
        """Test analytics retrieval"""
        analytics = search_service.get_analytics()

        assert hasattr(analytics, 'total_searches')
        assert hasattr(analytics, 'average_results')
        assert hasattr(analytics, 'popular_queries')
        assert hasattr(analytics, 'search_types_usage')

    def test_clear_index(self, search_service):
        """Test index clearing"""
        # Add some data
        search_service.indices['test_index'] = SearchIndex(
            id='test_index',
            name='Test Index',
            scope=SearchScope.ALL,
            total_documents=10
        )
        search_service.document_store['doc1'] = {'id': 'doc1', 'type': 'test'}
        search_service.term_index['test'].add('doc1')

        # Clear specific index
        search_service.clear_index('test_index')
        assert 'test_index' not in search_service.indices

        # Clear all indices
        search_service.clear_index()
        assert len(search_service.indices) == 0
        assert len(search_service.document_store) == 0
        assert len(search_service.term_index) == 0

    def test_list_indices(self, search_service):
        """Test listing indices"""
        # Add test indices
        index1 = SearchIndex(
            id='index1',
            name='Index 1',
            scope=SearchScope.CONVERSATIONS,
            total_documents=5
        )
        index2 = SearchIndex(
            id='index2',
            name='Index 2',
            scope=SearchScope.FILES,
            total_documents=3
        )

        search_service.indices['index1'] = index1
        search_service.indices['index2'] = index2

        indices = search_service.list_indices()

        assert len(indices) == 2
        assert all(isinstance(idx, SearchIndex) for idx in indices)

    def test_search_empty_query(self, search_service):
        """Test search with empty query"""
        search_query = SearchQuery(query="")
        results = search_service.search(search_query)

        assert isinstance(results, SearchResults)
        assert results.total_results == 0
        assert len(results.results) == 0

    def test_search_no_results(self, search_service):
        """Test search with no matching results"""
        search_query = SearchQuery(query="nonexistentterm")
        results = search_service.search(search_query)

        assert isinstance(results, SearchResults)
        assert results.total_results == 0
        assert len(results.results) == 0

    def test_matches_filters_date_range(self, search_service):
        """Test date range filtering"""
        past_date = datetime.now() - timedelta(days=10)
        future_date = datetime.now() + timedelta(days=1)

        doc = {
            'type': 'conversation',
            'metadata': {},
            'created_at': past_date.isoformat()
        }

        # Should match date range
        filters = SearchFilter(date_from=past_date - timedelta(days=1), date_to=future_date)
        assert search_service._matches_filters(doc, filters)

        # Should not match date range
        filters = SearchFilter(date_from=future_date)
        assert not search_service._matches_filters(doc, filters)

    def test_matches_filters_tags(self, search_service):
        """Test tag filtering"""
        doc = {
            'type': 'conversation',
            'metadata': {'tags': ['important', 'test']},
        }

        # Should match tags
        filters = SearchFilter(tags=['important'])
        assert search_service._matches_filters(doc, filters)

        # Should not match tags
        filters = SearchFilter(tags=['missing'])
        assert not search_service._matches_filters(doc, filters)