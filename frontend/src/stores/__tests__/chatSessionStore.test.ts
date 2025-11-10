import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { chatSessionsAPI } from '../../services/api'
import { useChatSessionStore } from '../../stores/chatSessionStore'

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

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

describe('Chat Session Store', () => {
  const mockSession = {
    id: 'session-1',
    project_id: 'project-1',
    title: 'Test Session',
    description: 'A test session',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    is_active: true,
    message_count: 0,
  }

  const mockMessage = {
    id: 'msg-1',
    role: 'user',
    content: 'Hello',
    timestamp: '2025-01-01T00:00:00Z',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
    localStorageMock.setItem.mockImplementation(() => {})
  })

  afterEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
    localStorageMock.setItem.mockImplementation(() => {})
    localStorageMock.removeItem.mockImplementation(() => {})
    localStorageMock.clear.mockImplementation(() => {})
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useChatSessionStore())

      expect(result.current.sessions).toEqual([])
      expect(result.current.currentSession).toBeNull()
      expect(result.current.sessionMessages).toEqual([])
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })
  })

  describe('loadSessions', () => {
    it('loads sessions successfully', async () => {
      const mockSessions = [mockSession]
      vi.mocked(chatSessionsAPI.listSessions).mockResolvedValue({
        data: mockSessions,
      })

      const { result } = renderHook(() => useChatSessionStore())

      await act(async () => {
        await result.current.loadSessions('project-1')
      })

      expect(chatSessionsAPI.listSessions).toHaveBeenCalledWith('project-1', false)
      expect(result.current.sessions).toEqual(mockSessions)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBe(null)
    })

    it('handles API errors', async () => {
      const error = new Error('API Error')
      vi.mocked(chatSessionsAPI.listSessions).mockRejectedValue(error)

      const { result } = renderHook(() => useChatSessionStore())

      await expect(result.current.loadSessions('project-1')).rejects.toThrow('API Error')
      expect(result.current.error).toBe('API Error')
      expect(result.current.isLoading).toBe(false)
    })

    it('should set loading state correctly', async () => {
      const mockSessions = [mockSession]
      vi.mocked(chatSessionsAPI.listSessions).mockResolvedValue({
        data: mockSessions,
      })

      const { result } = renderHook(() => useChatSessionStore())

      let loadingStates: boolean[] = []

      act(() => {
        result.current.loadSessions('project-1').then(() => {
          loadingStates.push(result.current.isLoading)
        })
        loadingStates.push(result.current.isLoading) // Should be true immediately
      })

      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 0))
      })

      expect(loadingStates).toContain(true) // Was loading
      expect(result.current.isLoading).toBe(false) // Finished loading
    })
  })

  describe('createSession', () => {
    it('creates a session successfully', async () => {
      const createData = {
        project_id: 'project-1',
        title: 'New Session',
        description: 'A new session',
      }

      vi.mocked(chatSessionsAPI.createSession).mockResolvedValue({
        data: mockSession,
      })

      vi.mocked(chatSessionsAPI.listSessions).mockResolvedValue({
        data: [mockSession],
      })

      const { result } = renderHook(() => useChatSessionStore())

      let createdSession
      await act(async () => {
        createdSession = await result.current.createSession(createData)
      })

      expect(chatSessionsAPI.createSession).toHaveBeenCalledWith(createData)
      expect(createdSession).toEqual(mockSession)
      expect(result.current.isLoading).toBe(false)
    })

    it('reloads sessions after creation', async () => {
      const createData = {
        project_id: 'project-1',
        title: 'New Session',
      }

      vi.mocked(chatSessionsAPI.createSession).mockResolvedValue({
        data: mockSession,
      })

      vi.mocked(chatSessionsAPI.listSessions).mockResolvedValue({
        data: [mockSession],
      })

      const { result } = renderHook(() => useChatSessionStore())

      await act(async () => {
        await result.current.createSession(createData)
      })

      expect(chatSessionsAPI.listSessions).toHaveBeenCalledWith('project-1', false)
    })

    it('should handle create errors', async () => {
      const error = new Error('Create failed')
      vi.mocked(chatSessionsAPI.createSession).mockRejectedValue(error)

      const { result } = renderHook(() => useChatSessionStore())

      await expect(result.current.createSession({
        project_id: 'project-1',
        title: 'New Session'
      })).rejects.toThrow('Create failed')
      expect(result.current.error).toBe('Create failed')
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('updateSession', () => {
    it('updates a session successfully', async () => {
      const updateData = {
        title: 'Updated Title',
        description: 'Updated description',
      }

      const updatedSession = { ...mockSession, ...updateData }

      vi.mocked(chatSessionsAPI.updateSession).mockResolvedValue({
        data: updatedSession,
      })

      vi.mocked(chatSessionsAPI.listSessions).mockResolvedValue({
        data: [updatedSession],
      })

      const { result } = renderHook(() => useChatSessionStore())

      await act(async () => {
        result.current.setCurrentSession(mockSession)
        await result.current.updateSession('session-1', updateData)
      })

      expect(chatSessionsAPI.updateSession).toHaveBeenCalledWith('session-1', updateData)
      expect(result.current.currentSession).toEqual(updatedSession)
    })

    it('should handle update errors', async () => {
      const error = new Error('Update failed')
      vi.mocked(chatSessionsAPI.updateSession).mockRejectedValue(error)

      const { result } = renderHook(() => useChatSessionStore())

      await expect(result.current.updateSession('session-1', {
        title: 'Updated Title'
      })).rejects.toThrow('Update failed')
      expect(result.current.error).toBe('Update failed')
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('deleteSession', () => {
    it('deletes a session successfully', async () => {
      vi.mocked(chatSessionsAPI.deleteSession).mockResolvedValue({
        data: null,
      })

      vi.mocked(chatSessionsAPI.listSessions).mockResolvedValue({
        data: [],
      })

      const { result } = renderHook(() => useChatSessionStore())

      await act(async () => {
        result.current.setCurrentSession(mockSession)
        await result.current.deleteSession('session-1')
      })

      expect(chatSessionsAPI.deleteSession).toHaveBeenCalledWith('session-1', false)
      expect(result.current.currentSession).toBe(null)
    })

    it('clears current session if deleted', async () => {
      vi.mocked(chatSessionsAPI.deleteSession).mockResolvedValue({
        data: null,
      })

      const { result } = renderHook(() => useChatSessionStore())

      await act(async () => {
        result.current.setCurrentSession(mockSession)
        await result.current.deleteSession('session-1')
      })

      expect(result.current.currentSession).toBe(null)
    })

    it('should handle delete errors', async () => {
      const error = new Error('Delete failed')
      vi.mocked(chatSessionsAPI.deleteSession).mockRejectedValue(error)

      const { result } = renderHook(() => useChatSessionStore())

      await expect(result.current.deleteSession('session-1', false)).rejects.toThrow('Delete failed')
      expect(result.current.error).toBe('Delete failed')
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('getSessionWithMessages', () => {
    it('loads session with messages', async () => {
      const sessionWithMessages = {
        session: mockSession,
        messages: [mockMessage],
      }

      vi.mocked(chatSessionsAPI.getSessionWithMessages).mockResolvedValue({
        data: sessionWithMessages,
      })

      const { result } = renderHook(() => useChatSessionStore())

      let resultData
      await act(async () => {
        resultData = await result.current.getSessionWithMessages('session-1')
      })

      expect(chatSessionsAPI.getSessionWithMessages).toHaveBeenCalledWith('session-1')
      expect(resultData).toEqual(sessionWithMessages)
      expect(result.current.currentSession).toEqual(mockSession)
      expect(result.current.sessionMessages).toEqual([mockMessage])
    })
  })

  describe('addMessage', () => {
    it('adds a message to session', async () => {
      const messageData = {
        role: 'user' as const,
        content: 'Hello world',
      }

      vi.mocked(chatSessionsAPI.addMessage).mockResolvedValue({
        data: mockMessage,
      })

      vi.mocked(chatSessionsAPI.getSessionMessages).mockResolvedValue({
        data: [mockMessage],
      })

      const { result } = renderHook(() => useChatSessionStore())

      let addedMessage
      await act(async () => {
        addedMessage = await result.current.addMessage('session-1', messageData)
      })

      expect(chatSessionsAPI.addMessage).toHaveBeenCalledWith('session-1', messageData)
      expect(addedMessage).toEqual(mockMessage)
      expect(result.current.sessionMessages).toEqual([mockMessage])
    })
  })

  describe('getSessionMessages', () => {
    it('loads session messages', async () => {
      const messages = [mockMessage]

      vi.mocked(chatSessionsAPI.getSessionMessages).mockResolvedValue({
        data: messages,
      })

      const { result } = renderHook(() => useChatSessionStore())

      let loadedMessages
      await act(async () => {
        loadedMessages = await result.current.getSessionMessages('session-1')
      })

      expect(chatSessionsAPI.getSessionMessages).toHaveBeenCalledWith('session-1', undefined, 0)
      expect(loadedMessages).toEqual(messages)
      expect(result.current.sessionMessages).toEqual(messages)
    })

    it('supports pagination', async () => {
      vi.mocked(chatSessionsAPI.getSessionMessages).mockResolvedValue({
        data: [mockMessage],
      })

      const { result } = renderHook(() => useChatSessionStore())

      await act(async () => {
        await result.current.getSessionMessages('session-1', 10, 5)
      })

      expect(chatSessionsAPI.getSessionMessages).toHaveBeenCalledWith('session-1', 10, 5)
    })
  })

  describe('getSessionStats', () => {
    it('loads session statistics', async () => {
      const stats = {
        total_sessions: 5,
        active_sessions: 3,
        total_messages: 25,
        average_messages_per_session: 5,
        sessions_by_project: { 'project-1': 5 },
      }

      vi.mocked(chatSessionsAPI.getSessionStats).mockResolvedValue({
        data: stats,
      })

      const { result } = renderHook(() => useChatSessionStore())

      let loadedStats
      await act(async () => {
        loadedStats = await result.current.getSessionStats('project-1')
      })

      expect(chatSessionsAPI.getSessionStats).toHaveBeenCalledWith('project-1')
      expect(loadedStats).toEqual(stats)
    })
  })

  describe('State setters', () => {
    it('sets current session', () => {
      const { result } = renderHook(() => useChatSessionStore())

      act(() => {
        result.current.setCurrentSession(mockSession)
      })

      expect(result.current.currentSession).toEqual(mockSession)
    })

    it('sets sessions list', () => {
      const sessions = [mockSession]
      const { result } = renderHook(() => useChatSessionStore())

      act(() => {
        result.current.setSessions(sessions)
      })

      expect(result.current.sessions).toEqual(sessions)
    })

    it('sets session messages', () => {
      const messages = [mockMessage]
      const { result } = renderHook(() => useChatSessionStore())

      act(() => {
        result.current.setSessionMessages(messages)
      })

      expect(result.current.sessionMessages).toEqual(messages)
    })

    it('sets loading state', () => {
      const { result } = renderHook(() => useChatSessionStore())

      act(() => {
        result.current.setLoading(true)
      })

      expect(result.current.isLoading).toBe(true)
    })

    it('sets error state', () => {
      const { result } = renderHook(() => useChatSessionStore())

      act(() => {
        result.current.setError('Test error')
      })

      expect(result.current.error).toBe('Test error')
    })
  })
})