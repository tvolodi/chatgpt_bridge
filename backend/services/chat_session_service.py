"""
Chat Session Service

This module provides the business logic for managing chat sessions and messages
within the AI Chat Assistant backend.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..models.chat_session import (
    ChatSession, ChatSessionCreate, ChatSessionUpdate, Message, MessageCreate,
    ChatSessionSummary, ChatSessionStats, ChatSessionWithMessages
)


class ChatSessionService:
    """
    Service for managing chat sessions and their message history.

    Provides CRUD operations for chat sessions, message management,
    and file-based persistence within project directories.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the chat session service.

        Args:
            data_dir: Base directory for storing chat session data
        """
        self.data_dir = Path(data_dir)
        self.sessions_dir = self.data_dir / "chat_sessions"
        self.projects_dir = self.data_dir / "projects"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def _get_session_dir(self, session_id: UUID, project_id: Optional[str] = None) -> Path:
        """
        Get the directory path for a specific chat session.
        
        If project_id is provided, returns nested path: data/projects/{project_id}/chat_sessions/{session_id}
        Otherwise returns legacy flat path: data/chat_sessions/{session_id}
        """
        if project_id:
            return self.projects_dir / str(project_id) / "chat_sessions" / str(session_id)
        return self.sessions_dir / str(session_id)

    def _get_session_metadata_file(self, session_id: UUID, project_id: Optional[str] = None) -> Path:
        """Get the metadata file path for a specific chat session."""
        return self._get_session_dir(session_id, project_id) / "metadata.json"

    def _get_messages_file(self, session_id: UUID, project_id: Optional[str] = None) -> Path:
        """Get the messages file path for a specific chat session."""
        return self._get_session_dir(session_id, project_id) / "messages.json"

    def _load_session_metadata(self, session_id: UUID, project_id: Optional[str] = None) -> Optional[ChatSession]:
        """Load session metadata from file."""
        metadata_file = self._get_session_metadata_file(session_id, project_id)
        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert string timestamps back to datetime objects
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                # Convert string UUIDs back to UUID objects
                data['id'] = UUID(data['id'])
                # Only convert project_id to UUID if it's not None
                data['project_id'] = UUID(data['project_id']) if data['project_id'] else None
                return ChatSession(**data)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _save_session_metadata(self, session: ChatSession, project_id: Optional[str] = None) -> None:
        """Save session metadata to file."""
        session_dir = self._get_session_dir(session.id, project_id)
        session_dir.mkdir(parents=True, exist_ok=True)

        metadata_file = self._get_session_metadata_file(session.id, project_id)
        data = session.model_dump()
        # Convert datetime objects to ISO format strings and UUIDs to strings
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        data['id'] = str(data['id'])
        # Only convert project_id to string if it's not None
        data['project_id'] = str(data['project_id']) if data['project_id'] else None

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_messages(self, session_id: UUID, project_id: Optional[str] = None) -> List[Message]:
        """Load messages for a session from file."""
        messages_file = self._get_messages_file(session_id, project_id)
        if not messages_file.exists():
            return []

        try:
            with open(messages_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                messages = []
                for msg_data in data:
                    # Convert string timestamps back to datetime objects
                    msg_data['timestamp'] = datetime.fromisoformat(msg_data['timestamp'])
                    # Convert string UUIDs back to UUID objects
                    msg_data['id'] = UUID(msg_data['id'])
                    messages.append(Message(**msg_data))
                return messages
        except (json.JSONDecodeError, KeyError, ValueError):
            return []

    def _save_messages(self, session_id: UUID, messages: List[Message], project_id: Optional[str] = None) -> None:
        """Save messages for a session to file."""
        session_dir = self._get_session_dir(session_id, project_id)
        session_dir.mkdir(parents=True, exist_ok=True)

        messages_file = self._get_messages_file(session_id, project_id)
        data = []
        for msg in messages:
            msg_data = msg.model_dump()
            # Convert datetime objects to ISO format strings and UUIDs to strings
            msg_data['timestamp'] = msg_data['timestamp'].isoformat()
            msg_data['id'] = str(msg_data['id'])
            data.append(msg_data)

        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_session(self, session_data: ChatSessionCreate) -> ChatSession:
        """
        Create a new chat session.

        Args:
            session_data: Data for the new session

        Returns:
            The created chat session

        Raises:
            ValueError: If validation fails
        """
        # Extract project_id and convert to string if UUID (None stays None for flat structure)
        project_id_str = str(session_data.project_id) if session_data.project_id else None

        session = ChatSession(
            project_id=session_data.project_id,
            title=session_data.title,
            description=session_data.description,
            metadata=session_data.metadata or {}
        )

        self._save_session_metadata(session, project_id_str)
        return session

    def get_session(self, session_id: UUID, project_id: Optional[str] = None) -> Optional[ChatSession]:
        """
        Get a chat session by ID.

        Args:
            session_id: The session ID to retrieve
            project_id: Optional project ID (required for nested structure, auto-discovered if not provided)

        Returns:
            The chat session if found, None otherwise
        """
        # If project_id is provided, load directly
        if project_id:
            return self._load_session_metadata(session_id, project_id)
        
        # Try legacy flat structure first
        session = self._load_session_metadata(session_id, None)
        if session:
            return session
        
        # If not found in flat structure, search through all projects (auto-discover)
        if self.projects_dir.exists():
            for project_dir in self.projects_dir.iterdir():
                if project_dir.is_dir():
                    try:
                        # Try to load session from this project
                        session = self._load_session_metadata(session_id, project_dir.name)
                        if session:
                            return session
                    except (ValueError, OSError):
                        # Skip if project_dir.name is not a valid directory
                        continue
        
        return None

    def list_sessions(self, project_id: Optional[UUID] = None, include_inactive: bool = False) -> List[ChatSessionSummary]:
        """
        List chat sessions, optionally filtered by project.

        Args:
            project_id: Optional project ID to filter by
            include_inactive: Whether to include inactive sessions

        Returns:
            List of chat session summaries
        """
        summaries = []
        project_id_str = str(project_id) if project_id else None

        # First try nested structure: data/projects/{project_id}/chat_sessions/
        if project_id_str:
            project_sessions_dir = self.projects_dir / project_id_str / "chat_sessions"
            if project_sessions_dir.exists():
                for session_dir in project_sessions_dir.iterdir():
                    if session_dir.is_dir():
                        try:
                            session_id = UUID(session_dir.name)
                            session = self._load_session_metadata(session_id, project_id_str)
                            if session:
                                # Apply filters
                                if not include_inactive and not session.is_active:
                                    continue

                                # Get message count and last message preview
                                messages = self._load_messages(session_id, project_id_str)
                                last_message_preview = None
                                if messages:
                                    last_msg = messages[-1]
                                    last_message_preview = last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content

                                summary = ChatSessionSummary(
                                    id=session.id,
                                    project_id=session.project_id,
                                    title=session.title,
                                    created_at=session.created_at,
                                    updated_at=session.updated_at,
                                    is_active=session.is_active,
                                    message_count=len(messages),
                                    last_message_preview=last_message_preview
                                )
                                summaries.append(summary)
                        except (ValueError, OSError):
                            continue
        else:
            # Fallback: search flat structure (legacy support)
            if self.sessions_dir.exists():
                for session_dir in self.sessions_dir.iterdir():
                    if session_dir.is_dir():
                        try:
                            session_id = UUID(session_dir.name)
                            session = self._load_session_metadata(session_id)
                            if session:
                                # Apply filters
                                if project_id and session.project_id != project_id:
                                    continue
                                if not include_inactive and not session.is_active:
                                    continue

                                # Get message count and last message preview
                                messages = self._load_messages(session_id)
                                last_message_preview = None
                                if messages:
                                    last_msg = messages[-1]
                                    last_message_preview = last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content

                                summary = ChatSessionSummary(
                                    id=session.id,
                                    project_id=session.project_id,
                                    title=session.title,
                                    created_at=session.created_at,
                                    updated_at=session.updated_at,
                                    is_active=session.is_active,
                                    message_count=len(messages),
                                    last_message_preview=last_message_preview
                                )
                                summaries.append(summary)
                        except (ValueError, OSError):
                            continue

        # Sort by updated_at descending (most recent first)
        summaries.sort(key=lambda s: s.updated_at, reverse=True)
        return summaries

    def update_session(self, session_id: UUID, update_data: ChatSessionUpdate, project_id: Optional[str] = None) -> Optional[ChatSession]:
        """
        Update an existing chat session.

        Args:
            session_id: The session ID to update
            update_data: The data to update
            project_id: Optional project ID (required for nested structure, auto-discovered if not provided)

        Returns:
            The updated session if found, None otherwise

        Raises:
            ValueError: If validation fails
        """
        # Use get_session to auto-discover project_id if not provided
        session = self.get_session(session_id, project_id)
        if not session:
            return None
        
        # Get the actual project_id (either provided or discovered)
        actual_project_id = project_id or (str(session.project_id) if session.project_id else None)

        # Update fields if provided
        if update_data.title is not None:
            session.title = update_data.title
        if update_data.description is not None:
            session.description = update_data.description
        if update_data.is_active is not None:
            session.is_active = update_data.is_active
        if update_data.metadata is not None:
            session.metadata = update_data.metadata

        session.updated_at = datetime.now()
        self._save_session_metadata(session, actual_project_id)
        return session

    def delete_session(self, session_id: UUID, force: bool = False, project_id: Optional[str] = None) -> bool:
        """
        Delete a chat session and all its messages.

        Args:
            session_id: The session ID to delete
            force: Whether to force deletion even if session has messages
            project_id: Optional project ID (required for nested structure, auto-discovered if not provided)

        Returns:
            True if deleted, False if not found or not allowed

        Raises:
            ValueError: If session has messages and force=False
        """
        # Use get_session to auto-discover project_id if not provided
        session = self.get_session(session_id, project_id)
        if not session:
            return False
        
        # Get the actual project_id (either provided or discovered)
        actual_project_id = project_id or (str(session.project_id) if session.project_id else None)

        # Check if session has messages and force is not set
        messages = self._load_messages(session_id, actual_project_id)
        if messages and not force:
            raise ValueError(f"Cannot delete session {session_id} with {len(messages)} messages. Use force=True to override.")

        # Delete the session directory
        session_dir = self._get_session_dir(session_id, actual_project_id)
        if session_dir.exists():
            import shutil
            shutil.rmtree(session_dir)

        return True

    def add_message(self, session_id: UUID, message_data: MessageCreate, project_id: Optional[str] = None) -> Optional[Message]:
        """
        Add a message to a chat session.

        Args:
            session_id: The session ID to add the message to
            message_data: The message data
            project_id: Optional project ID (required for nested structure, auto-discovered if not provided)

        Returns:
            The created message if session exists, None otherwise

        Raises:
            ValueError: If session doesn't exist or validation fails
        """
        # Use get_session to auto-discover project_id if not provided
        session = self.get_session(session_id, project_id)
        if not session:
            raise ValueError(f"Chat session {session_id} not found")
        
        # Get the actual project_id (either provided or discovered)
        actual_project_id = project_id or (str(session.project_id) if session.project_id else None)

        # Validate role
        valid_roles = ["user", "assistant", "system"]
        if message_data.role not in valid_roles:
            raise ValueError(f"Invalid message role '{message_data.role}'. Must be one of: {valid_roles}")

        # Create the message
        message = Message(
            role=message_data.role,
            content=message_data.content,
            metadata=message_data.metadata or {}
        )

        # Load existing messages, add new one, and save
        messages = self._load_messages(session_id, actual_project_id)
        messages.append(message)
        self._save_messages(session_id, messages, actual_project_id)

        # Update session metadata
        session.message_count = len(messages)
        session.updated_at = datetime.now()
        self._save_session_metadata(session, actual_project_id)

        return message

    def get_messages(self, session_id: UUID, limit: Optional[int] = None, offset: int = 0, project_id: Optional[str] = None) -> List[Message]:
        """
        Get messages for a chat session.

        Args:
            session_id: The session ID to get messages for
            limit: Optional limit on number of messages to return
            offset: Number of messages to skip from the beginning
            project_id: Optional project ID (required for nested structure, auto-discovered if not provided)

        Returns:
            List of messages (empty if session not found)

        Raises:
            ValueError: If session doesn't exist
        """
        # Use get_session to auto-discover project_id if not provided
        session = self.get_session(session_id, project_id)
        if not session:
            raise ValueError(f"Chat session {session_id} not found")
        
        # Get the actual project_id (either provided or discovered)
        actual_project_id = project_id or (str(session.project_id) if session.project_id else None)

        messages = self._load_messages(session_id, actual_project_id)

        # Apply pagination
        if offset > 0:
            messages = messages[offset:]
        if limit is not None:
            messages = messages[:limit]

        return messages

    def get_session_with_messages(self, session_id: UUID, project_id: Optional[str] = None) -> Optional[ChatSessionWithMessages]:
        """
        Get a chat session with its full message history.

        Args:
            session_id: The session ID to retrieve
            project_id: Optional project ID (required for nested structure, auto-discovered if not provided)

        Returns:
            Session with messages if found, None otherwise
        """
        session = self.get_session(session_id, project_id)
        if not session:
            return None
        
        # Get the actual project_id (either provided or discovered)
        actual_project_id = project_id or (str(session.project_id) if session.project_id else None)
        
        messages = self._load_messages(session_id, actual_project_id)
        session = self._load_session_metadata(session_id, project_id)
        if not session:
            return None

        messages = self._load_messages(session_id, project_id)
        return ChatSessionWithMessages(session=session, messages=messages)

    def get_session_stats(self, project_id: Optional[UUID] = None) -> ChatSessionStats:
        """
        Get statistics for chat sessions.

        Args:
            project_id: Optional project ID to filter by

        Returns:
            Statistics about the sessions
        """
        sessions = self.list_sessions(project_id=project_id, include_inactive=True)
        total_sessions = len(sessions)
        active_sessions = sum(1 for s in sessions if s.is_active)
        total_messages = sum(s.message_count for s in sessions)
        average_messages_per_session = total_messages / total_sessions if total_sessions > 0 else 0

        # Count sessions by project
        sessions_by_project = {}
        for session in sessions:
            project_key = str(session.project_id)
            sessions_by_project[project_key] = sessions_by_project.get(project_key, 0) + 1

        return ChatSessionStats(
            total_sessions=total_sessions,
            active_sessions=active_sessions,
            total_messages=total_messages,
            average_messages_per_session=average_messages_per_session,
            sessions_by_project=sessions_by_project
        )