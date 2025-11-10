import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { chatSessionsAPI } from '../services/api'

export interface Message {
  id: string
  role: string
  content: string
  timestamp: string
  metadata?: Record<string, any>
}

export interface ChatSession {
  id: string
  project_id: string
  title: string
  description?: string
  created_at: string
  updated_at: string
  is_active: boolean
  metadata?: Record<string, any>
  message_count: number
}

export interface ChatSessionSummary {
  id: string
  project_id: string
  title: string
  created_at: string
  updated_at: string
  is_active: boolean
  message_count: number
  last_message_preview?: string
}

export interface ChatSessionWithMessages {
  session: ChatSession
  messages: Message[]
}

export interface ChatSessionStats {
  total_sessions: number
  active_sessions: number
  total_messages: number
  average_messages_per_session: number
  sessions_by_project: Record<string, number>
}

export interface CreateChatSessionData {
  project_id: string
  title: string
  description?: string
  metadata?: Record<string, any>
}

export interface UpdateChatSessionData {
  title?: string
  description?: string
  is_active?: boolean
  metadata?: Record<string, any>
}

export interface CreateMessageData {
  role: string
  content: string
  metadata?: Record<string, any>
}

interface ChatSessionState {
  // State
  currentSession: ChatSession | null
  sessions: ChatSessionSummary[]
  sessionMessages: Message[]
  isLoading: boolean
  error: string | null

  // Actions
  setCurrentSession: (session: ChatSession | null) => void
  setSessions: (sessions: ChatSessionSummary[]) => void
  setSessionMessages: (messages: Message[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // API Actions
  loadSessions: (projectId?: string, includeInactive?: boolean) => Promise<void>
  createSession: (data: CreateChatSessionData) => Promise<ChatSession>
  updateSession: (id: string, data: UpdateChatSessionData) => Promise<ChatSession>
  deleteSession: (id: string, force?: boolean) => Promise<void>
  getSession: (id: string) => Promise<ChatSession>
  getSessionWithMessages: (id: string) => Promise<ChatSessionWithMessages>
  addMessage: (sessionId: string, messageData: CreateMessageData) => Promise<Message>
  getSessionMessages: (sessionId: string, limit?: number, offset?: number) => Promise<Message[]>
  getSessionStats: (projectId?: string) => Promise<ChatSessionStats>
}

export const useChatSessionStore = create<ChatSessionState>()(
  persist(
    (set: any, get: any) => ({
      // Initial state
      currentSession: null,
      sessions: [],
      sessionMessages: [],
      isLoading: false,
      error: null,

      // Basic setters
      setCurrentSession: (session: ChatSession | null) => set({ currentSession: session }),
      setSessions: (sessions: ChatSessionSummary[]) => set({ sessions }),
      setSessionMessages: (messages: Message[]) => set({ sessionMessages: messages }),
      setLoading: (loading: boolean) => set({ isLoading: loading }),
      setError: (error: string | null) => set({ error }),

      // API Actions
      loadSessions: async (projectId?: string, includeInactive: boolean = false) => {
        set({ isLoading: true, error: null })
        try {
          const response = await chatSessionsAPI.listSessions(projectId, includeInactive)
          set({ sessions: response.data, isLoading: false })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      createSession: async (data: CreateChatSessionData) => {
        set({ isLoading: true, error: null })
        try {
          const response = await chatSessionsAPI.createSession(data)
          set({ isLoading: false })
          // Reload sessions to reflect the new session
          await get().loadSessions(data.project_id)
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      updateSession: async (id: string, data: UpdateChatSessionData) => {
        set({ isLoading: true, error: null })
        try {
          const response = await chatSessionsAPI.updateSession(id, data)
          set({ isLoading: false })
          // Update current session if it's the one being updated
          const currentSession = get().currentSession
          if (currentSession && currentSession.id === id) {
            set({ currentSession: response.data })
          }
          // Reload sessions to reflect the update
          if (currentSession) {
            await get().loadSessions(currentSession.project_id)
          }
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      deleteSession: async (id: string, force: boolean = false) => {
        set({ isLoading: true, error: null })
        try {
          await chatSessionsAPI.deleteSession(id, force)
          set({ isLoading: false })
          // Clear current session if it was deleted
          const currentSession = get().currentSession
          if (currentSession && currentSession.id === id) {
            set({ currentSession: null, sessionMessages: [] })
          }
          // Reload sessions
          if (currentSession) {
            await get().loadSessions(currentSession.project_id)
          }
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      getSession: async (id: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await chatSessionsAPI.getSession(id)
          set({ isLoading: false })
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      getSessionWithMessages: async (id: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await chatSessionsAPI.getSessionWithMessages(id)
          const sessionWithMessages = response.data
          set({
            currentSession: sessionWithMessages.session,
            sessionMessages: sessionWithMessages.messages,
            isLoading: false
          })
          return sessionWithMessages
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      addMessage: async (sessionId: string, messageData: CreateMessageData) => {
        set({ isLoading: true, error: null })
        try {
          const response = await chatSessionsAPI.addMessage(sessionId, messageData)
          set({ isLoading: false })
          // Reload messages to reflect the new message
          await get().getSessionMessages(sessionId)
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      getSessionMessages: async (sessionId: string, limit?: number, offset: number = 0) => {
        set({ isLoading: true, error: null })
        try {
          const response = await chatSessionsAPI.getSessionMessages(sessionId, limit, offset)
          set({ sessionMessages: response.data, isLoading: false })
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      getSessionStats: async (projectId) => {
        set({ isLoading: true, error: null })
        try {
          const response = await chatSessionsAPI.getSessionStats(projectId)
          set({ isLoading: false })
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      }
    }),
    {
      name: 'ai-chat-sessions',
      partialize: (state) => ({
        currentSession: state.currentSession
      })
    }
  )
)