import React, { useState, useEffect } from 'react'
import { useChatSessionStore, ChatSessionSummary, CreateChatSessionData, UpdateChatSessionData } from '../stores/chatSessionStore'
import { useProjectStore } from '../stores/projectStore'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Plus, Edit, Trash2, MessageSquare, Calendar, FileText } from 'lucide-react'

interface ChatSessionCardProps {
  session: ChatSessionSummary
  onEdit: (session: ChatSessionSummary) => void
  onDelete: (session: ChatSessionSummary) => void
  onSelect: (session: ChatSessionSummary) => void
}

const ChatSessionCard: React.FC<ChatSessionCardProps> = ({ session, onEdit, onDelete, onSelect }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors cursor-pointer" onClick={() => onSelect(session)}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-600 rounded-lg">
            <MessageSquare className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-50">{session.title}</h3>
            <p className="text-sm text-slate-400 mt-1">
              {session.message_count} messages
              {session.last_message_preview && (
                <span className="ml-2">• {session.last_message_preview}</span>
              )}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation()
              onEdit(session)
            }}
            className="text-slate-400 hover:text-white"
            aria-label={`Edit ${session.title}`}
            title={`Edit ${session.title}`}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation()
              onDelete(session)
            }}
            className="text-slate-400 hover:text-red-400"
            aria-label={`Delete ${session.title}`}
            title={`Delete ${session.title}`}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm text-slate-400">
        <div className="flex items-center gap-1">
          <Calendar className="h-4 w-4" />
          <span>{new Date(session.created_at).toLocaleDateString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <FileText className="h-4 w-4" />
          <span>{session.message_count} messages</span>
        </div>
        {!session.is_active && (
          <span className="ml-auto text-xs bg-slate-600 text-slate-300 px-2 py-1 rounded">
            Inactive
          </span>
        )}
      </div>
    </div>
  )
}

export { ChatSessionCard }

interface ChatSessionModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: CreateChatSessionData | UpdateChatSessionData) => Promise<void>
  session?: ChatSessionSummary | null
  title: string
}

const ChatSessionModal: React.FC<ChatSessionModalProps> = ({
  isOpen,
  onClose,
  onSave,
  session,
  title
}) => {
  const [titleValue, setTitleValue] = useState('')
  const [description, setDescription] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (session) {
      setTitleValue(session.title)
      // Note: ChatSessionSummary doesn't have description, so we'll set it to empty
      setDescription('')
    } else {
      setTitleValue('')
      setDescription('')
    }
    setError('')
  }, [session, isOpen])

  const handleSave = async () => {
    if (!titleValue.trim()) {
      setError('Session title is required')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      await onSave({
        title: titleValue.trim(),
        description: description.trim() || undefined
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save chat session')
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md border border-slate-700">
        <h2 className="text-xl font-semibold text-slate-50 mb-4">{title}</h2>

        <div className="space-y-4">
          <div>
            <label htmlFor="session-title" className="block text-sm font-medium text-slate-200 mb-2">
              Session Title *
            </label>
            <Input
              id="session-title"
              value={titleValue}
              onChange={(e) => setTitleValue(e.target.value)}
              placeholder="Enter session title"
              className={error ? 'border-red-500' : ''}
            />
          </div>

          <div>
            <label htmlFor="session-description" className="block text-sm font-medium text-slate-200 mb-2">
              Description
            </label>
            <textarea
              id="session-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter session description (optional)"
              rows={3}
              className="flex w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-slate-50 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm">{error}</div>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <Button
            onClick={handleSave}
            disabled={isLoading}
            className="flex-1"
          >
            {isLoading ? 'Saving...' : 'Save'}
          </Button>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  )
}

interface DeleteConfirmModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => Promise<void>
  session: ChatSessionSummary | null
}

const DeleteConfirmModal: React.FC<DeleteConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  session
}) => {
  const [isLoading, setIsLoading] = useState(false)

  const handleConfirm = async () => {
    setIsLoading(true)
    try {
      await onConfirm()
      onClose()
    } catch (err) {
      // Error is handled in the parent component
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen || !session) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md border border-slate-700">
        <h2 className="text-xl font-semibold text-slate-50 mb-4">Delete Chat Session</h2>

        <p className="text-slate-300 mb-4">
          Are you sure you want to delete <strong>"{session.title}"</strong>?
          This action cannot be undone and will remove all {session.message_count} messages.
        </p>

        <div className="flex gap-3">
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={isLoading}
            className="flex-1"
          >
            {isLoading ? 'Deleting...' : 'Delete'}
          </Button>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  )
}

export const ChatSessionsPage: React.FC = () => {
  const { currentProject } = useProjectStore()
  const {
    sessions,
    isLoading,
    error,
    loadSessions,
    createSession,
    updateSession,
    deleteSession
  } = useChatSessionStore()

  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [selectedSession, setSelectedSession] = useState<ChatSessionSummary | null>(null)

  useEffect(() => {
    if (currentProject) {
      loadSessions(currentProject.id)
    }
  }, [currentProject, loadSessions])

  const handleCreateSession = async (data: CreateChatSessionData) => {
    if (!currentProject) return
    await createSession({
      ...data,
      project_id: currentProject.id
    })
  }

  const handleEditSession = (session: ChatSessionSummary) => {
    setSelectedSession(session)
    setEditModalOpen(true)
  }

  const handleUpdateSession = async (data: UpdateChatSessionData) => {
    if (selectedSession) {
      await updateSession(selectedSession.id, data)
      setSelectedSession(null)
    }
  }

  const handleDeleteSession = (session: ChatSessionSummary) => {
    setSelectedSession(session)
    setDeleteModalOpen(true)
  }

  const handleConfirmDelete = async () => {
    if (selectedSession) {
      await deleteSession(selectedSession.id)
      setSelectedSession(null)
    }
  }

  const handleSelectSession = (session: ChatSessionSummary) => {
    // Navigate to chat with this session selected
    // This will be implemented when we update the ChatPage
    console.log('Selected session:', session)
  }

  if (!currentProject) {
    return (
      <div className="p-6">
        <div className="max-w-6xl mx-auto text-center py-12">
          <MessageSquare className="h-16 w-16 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-300 mb-2">No Project Selected</h3>
          <p className="text-slate-400">Please select a project to manage chat sessions.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-50 mb-2">Chat Sessions</h1>
            <p className="text-slate-400">Manage chat sessions in {currentProject.name}</p>
          </div>
          <Button onClick={() => setCreateModalOpen(true)} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            New Session
          </Button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900 border border-red-600 rounded-lg p-4 mb-6">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && sessions.length === 0 && (
          <div className="text-center py-12">
            <div className="text-slate-400">Loading chat sessions...</div>
          </div>
        )}

        {/* Sessions Grid */}
        {!isLoading || sessions.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.map((session) => (
              <ChatSessionCard
                key={session.id}
                session={session}
                onEdit={handleEditSession}
                onDelete={handleDeleteSession}
                onSelect={handleSelectSession}
              />
            ))}
          </div>
        ) : null}

        {/* Empty State */}
        {!isLoading && sessions.length === 0 && (
          <div className="text-center py-12">
            <MessageSquare className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-300 mb-2">No chat sessions yet</h3>
            <p className="text-slate-400 mb-6">Create your first chat session to start a conversation.</p>
            <Button onClick={() => setCreateModalOpen(true)} className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Create Session
            </Button>
          </div>
        )}

        {/* Modals */}
        <ChatSessionModal
          isOpen={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
          onSave={handleCreateSession}
          title="Create New Chat Session"
        />

        <ChatSessionModal
          isOpen={editModalOpen}
          onClose={() => {
            setEditModalOpen(false)
            setSelectedSession(null)
          }}
          onSave={handleUpdateSession}
          session={selectedSession}
          title="Edit Chat Session"
        />

        <DeleteConfirmModal
          isOpen={deleteModalOpen}
          onClose={() => {
            setDeleteModalOpen(false)
            setSelectedSession(null)
          }}
          onConfirm={handleConfirmDelete}
          session={selectedSession}
        />
      </div>
    </div>
  )
}

export default ChatSessionsPage