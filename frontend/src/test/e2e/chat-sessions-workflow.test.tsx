import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, within, fireEvent, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'

// Mock the API
vi.mock('../../services/api', () => ({
  chatSessionsAPI: {
    listSessions: vi.fn(),
    createSession: vi.fn(),
    updateSession: vi.fn(),
    deleteSession: vi.fn(),
    getSession: vi.fn(),
    getSessionWithMessages: vi.fn(),
    addMessage: vi.fn(),
    getSessionMessages: vi.fn(),
    getSessionStats: vi.fn(),
  },
}))

// Mock the project store
vi.mock('../../stores/projectStore', () => ({
  useProjectStore: vi.fn()
}))

// Mock the chat session store
vi.mock('../../stores/chatSessionStore', () => ({
  useChatSessionStore: vi.fn()
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Import after mocking
import { ChatSessionsPage } from '../../pages/ChatSessionsPage'
import { chatSessionsAPI } from '../../services/api'
import { useProjectStore } from '../../stores/projectStore'
import { useChatSessionStore } from '../../stores/chatSessionStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const mockProject = {
  id: 'test-project',
  name: 'Test Project',
  description: 'A test project',
  parent_id: null,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
  path: '/projects/test-project',
}

const mockSessions = [
  {
    id: 'session-1',
    project_id: 'test-project',
    title: 'First Chat Session',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    is_active: true,
    message_count: 5,
    last_message_preview: 'Hello, how can I help you?',
  },
  {
    id: 'session-2',
    project_id: 'test-project',
    title: 'Second Chat Session',
    created_at: '2025-01-02T00:00:00Z',
    updated_at: '2025-01-02T00:00:00Z',
    is_active: true,
    message_count: 3,
    last_message_preview: 'What is the weather like?',
  },
]

const renderChatSessionsPage = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ChatSessionsPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Chat Sessions End-to-End Tests', () => {
  let user: ReturnType<typeof userEvent.setup>
  let mockStore: any

  beforeEach(() => {
    user = userEvent.setup()
    vi.clearAllMocks()

    // Mock localStorage
    localStorageMock.getItem.mockReturnValue(null)
    localStorageMock.setItem.mockImplementation(() => {})

    // Mock project store
    ;(useProjectStore as any).mockReturnValue({
      currentProject: mockProject,
      loadProjectTree: vi.fn(),
    })

    // Initialize mock chat session store
    mockStore = {
      sessions: mockSessions,
      isLoading: false,
      error: null,
      loadSessions: vi.fn(),
      createSession: vi.fn(),
      updateSession: vi.fn(),
      deleteSession: vi.fn(),
    }

    // Mock chat session store
    ;(useChatSessionStore as any).mockReturnValue(mockStore)

    // Mock API responses
    vi.mocked(chatSessionsAPI.listSessions).mockResolvedValue({
      data: mockSessions,
    })

    vi.mocked(chatSessionsAPI.createSession).mockResolvedValue({
      data: {
        id: 'session-3',
        project_id: 'test-project',
        title: 'New Chat Session',
        description: 'A new session',
        created_at: '2025-01-03T00:00:00Z',
        updated_at: '2025-01-03T00:00:00Z',
        is_active: true,
        message_count: 0,
      },
    })

    vi.mocked(chatSessionsAPI.updateSession).mockResolvedValue({
      data: {
        id: 'session-1',
        project_id: 'test-project',
        title: 'Updated Chat Session',
        description: 'Updated description',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-03T00:00:00Z',
        is_active: true,
        message_count: 5,
      },
    })

    vi.mocked(chatSessionsAPI.deleteSession).mockResolvedValue({
      data: null,
    })
  })

  it('renders the chat sessions page with project context', () => {
    renderChatSessionsPage()
    expect(screen.getByText('Chat Sessions')).toBeInTheDocument()
    expect(screen.getByText('Manage chat sessions in Test Project')).toBeInTheDocument()
  })

  it('displays chat sessions in a grid layout', async () => {
    renderChatSessionsPage()

    await waitFor(() => {
      expect(screen.getByText('First Chat Session')).toBeInTheDocument()
      expect(screen.getByText('Second Chat Session')).toBeInTheDocument()
    })

    // Check session details - check individual parts since text is split across elements
    expect(screen.getAllByText('5 messages')).toHaveLength(2) // One in header, one in footer
    expect(screen.getByText('• Hello, how can I help you?')).toBeInTheDocument()
    expect(screen.getByText('• What is the weather like?')).toBeInTheDocument()
  })

  it('opens create session modal when clicking New Session button', async () => {
    renderChatSessionsPage()

    const newSessionButton = screen.getByText('New Session')
    await user.click(newSessionButton)

    expect(screen.getByText('Create New Chat Session')).toBeInTheDocument()
    expect(screen.getByLabelText('Session Title *')).toBeInTheDocument()
    expect(screen.getByLabelText('Description')).toBeInTheDocument()
  })

  it('creates a new chat session successfully', async () => {
    renderChatSessionsPage()

    // Open create modal
    const newSessionButton = screen.getByText('New Session')
    await user.click(newSessionButton)

    // Fill form
    const titleInput = screen.getByLabelText('Session Title *')
    const descriptionInput = screen.getByLabelText('Description')

    await user.type(titleInput, 'New Test Session')
    await user.type(descriptionInput, 'A test session description')

    // Submit form
    const saveButton = screen.getByText('Save')
    await user.click(saveButton)

    // Verify store method was called
    await waitFor(() => {
      expect(mockStore.createSession).toHaveBeenCalledWith({
        project_id: 'test-project',
        title: 'New Test Session',
        description: 'A test session description',
      })
    })

    // Modal should close
    await waitFor(() => {
      expect(screen.queryByText('Create New Chat Session')).not.toBeInTheDocument()
    })
  })

  it('shows validation error for empty title', async () => {
    renderChatSessionsPage()

    // Open create modal
    const newSessionButton = screen.getByText('New Session')
    await user.click(newSessionButton)

    // Try to submit without title
    const saveButton = screen.getByText('Save')
    await user.click(saveButton)

    // Should show error
    expect(screen.getByText('Session title is required')).toBeInTheDocument()
  })

  it('opens edit modal when clicking edit button on session card', async () => {
    renderChatSessionsPage()

    await waitFor(() => {
      expect(screen.getByText('First Chat Session')).toBeInTheDocument()
    })

    // Find the edit button for the first session
    const sessionCards = screen.getAllByText('First Chat Session')
    const sessionCard = sessionCards[0].closest('.bg-slate-800')
    const editButton = within(sessionCard!).getByLabelText('Edit First Chat Session')

    await user.click(editButton)

    expect(screen.getByText('Edit Chat Session')).toBeInTheDocument()
    expect(screen.getByDisplayValue('First Chat Session')).toBeInTheDocument()
  })

  it('updates a chat session successfully', async () => {
    renderChatSessionsPage()

    await waitFor(() => {
      expect(screen.getByText('First Chat Session')).toBeInTheDocument()
    })

    // Open edit modal
    const sessionCards = screen.getAllByText('First Chat Session')
    const sessionCard = sessionCards[0].closest('.bg-slate-800')
    const editButton = within(sessionCard!).getByLabelText('Edit First Chat Session')
    await user.click(editButton)

    // Update title
    const titleInput = screen.getByDisplayValue('First Chat Session')
    await user.clear(titleInput)
    await user.type(titleInput, 'Updated Session Title')

    // Save
    const saveButton = screen.getByText('Save')
    await user.click(saveButton)

    // Verify store method was called
    await waitFor(() => {
      expect(mockStore.updateSession).toHaveBeenCalledWith('session-1', {
        title: 'Updated Session Title',
        description: undefined,
      })
    })
  })

  it('opens delete confirmation modal', async () => {
    renderChatSessionsPage()

    await waitFor(() => {
      expect(screen.getByText('First Chat Session')).toBeInTheDocument()
    })

    // Click delete button
    const sessionCards = screen.getAllByText('First Chat Session')
    const sessionCard = sessionCards[0].closest('.bg-slate-800')
    const deleteButton = within(sessionCard!).getByLabelText('Delete First Chat Session')

    await act(async () => {
      await user.click(deleteButton)
    })

    await waitFor(() => {
      expect(screen.getByText('Delete Chat Session')).toBeInTheDocument()
      expect(screen.getByText('First Chat Session')).toBeInTheDocument()
    })
  })

  it('deletes a chat session successfully', async () => {
    renderChatSessionsPage()

    await waitFor(() => {
      expect(screen.getByText('First Chat Session')).toBeInTheDocument()
    })

    // Open delete modal
    const sessionCards = screen.getAllByText('First Chat Session')
    const sessionCard = sessionCards[0].closest('.bg-slate-800')
    const deleteButton = within(sessionCard!).getByLabelText('Delete First Chat Session')
    await act(async () => {
      fireEvent.click(deleteButton)
    })

    // Confirm deletion
    const deleteConfirmButton = screen.getByText('Delete')
    await user.click(deleteConfirmButton)

    // Verify store method was called
    await waitFor(() => {
      expect(mockStore.deleteSession).toHaveBeenCalledWith('session-1')
    })
  })

  it('shows empty state when no sessions exist', async () => {
    // Mock empty sessions list
    mockStore.sessions = []

    renderChatSessionsPage()

    await waitFor(() => {
      expect(screen.getByText('No chat sessions yet')).toBeInTheDocument()
      expect(screen.getByText('Create your first chat session to start a conversation.')).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    // Mock API error
    mockStore.error = 'API Error'

    renderChatSessionsPage()

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument()
    })
  })

  it('shows loading state while fetching sessions', () => {
    // Mock loading state
    mockStore.isLoading = true
    mockStore.sessions = []

    renderChatSessionsPage()

    expect(screen.getByText('Loading chat sessions...')).toBeInTheDocument()
  })

  it('displays session creation date and message count', async () => {
    renderChatSessionsPage()

    await waitFor(() => {
      expect(screen.getByText('01.01.2025')).toBeInTheDocument()
      // Check that message counts appear (they appear in multiple places)
      const messageElements = screen.getAllByText(/messages/)
      expect(messageElements.length).toBeGreaterThan(0)
    })
  })

  it('shows inactive status for inactive sessions', async () => {
    const sessionsWithInactive = [
      ...mockSessions,
      {
        id: 'session-3',
        project_id: 'test-project',
        title: 'Inactive Session',
        created_at: '2025-01-03T00:00:00Z',
        updated_at: '2025-01-03T00:00:00Z',
        is_active: false,
        message_count: 0,
        last_message_preview: null,
      },
    ]

    mockStore.sessions = sessionsWithInactive

    renderChatSessionsPage()

    await waitFor(() => {
      expect(screen.getByText('Inactive')).toBeInTheDocument()
    })
  })
})