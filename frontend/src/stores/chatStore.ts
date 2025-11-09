import { create } from 'zustand'

interface Message {
  role: 'user' | 'assistant'
  content: string
  id: string
  timestamp: string
}

interface ChatState {
  sessionId: string
  messages: Message[]
  isLoading: boolean
  error: string | null
  
  // Actions
  setSessionId: (id: string) => void
  addMessage: (message: Message) => void
  setMessages: (messages: Message[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearChat: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  sessionId: '',
  messages: [],
  isLoading: false,
  error: null,
  
  setSessionId: (id) => set({ sessionId: id }),
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),
  setMessages: (messages) => set({ messages }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  clearChat: () => set({ messages: [], error: null }),
}))
