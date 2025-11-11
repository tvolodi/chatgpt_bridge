import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface RecentActivity {
  action: string
  resourceType: string
  resourceId: string
  title: string
  timestamp: Date
  metadata?: Record<string, any>
}

export interface Bookmark {
  id: string
  title: string
  resourceType: string
  resourceId: string
  url?: string
  description?: string
  tags: string[]
  createdAt: Date
  lastAccessed: Date
}

export interface SessionState {
  sessionId: string
  userId?: string
  loginTime: Date
  lastActivity: Date
  activeProject?: string
  activeSession?: string
  selectedProviderId?: string
  openTabs: string[]
  draftContent?: string
  clipboardHistory: string[]
}

interface UserState {
  session: SessionState | null
  recentActivities: RecentActivity[]
  bookmarks: Bookmark[]
  preferences: any // Will be defined in settings store

  // Actions
  setSession: (session: SessionState) => void
  updateSession: (updates: Partial<SessionState>) => void
  clearSession: () => void
  addRecentActivity: (activity: RecentActivity) => void
  addBookmark: (bookmark: Omit<Bookmark, 'id' | 'createdAt' | 'lastAccessed'>) => void
  removeBookmark: (bookmarkId: string) => void
  updateBookmark: (bookmarkId: string, updates: Partial<Bookmark>) => void
}

export const useUserStateStore = create<UserState>()(
  persist(
    (set, get) => ({
      session: null,
      recentActivities: [],
      bookmarks: [],
      preferences: {},

      setSession: (session) => set({ session }),

      updateSession: (updates) =>
        set((state) => ({
          session: state.session ? { ...state.session, ...updates } : null
        })),

      clearSession: () => set({ session: null }),

      addRecentActivity: (activity) =>
        set((state) => ({
          recentActivities: [activity, ...state.recentActivities.slice(0, 49)] // Keep last 50
        })),

      addBookmark: (bookmarkData) => {
        const bookmark: Bookmark = {
          ...bookmarkData,
          id: `bookmark_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          createdAt: new Date(),
          lastAccessed: new Date(),
        }
        set((state) => ({
          bookmarks: [...state.bookmarks, bookmark]
        }))
      },

      removeBookmark: (bookmarkId) =>
        set((state) => ({
          bookmarks: state.bookmarks.filter(b => b.id !== bookmarkId)
        })),

      updateBookmark: (bookmarkId, updates) =>
        set((state) => ({
          bookmarks: state.bookmarks.map(bookmark =>
            bookmark.id === bookmarkId
              ? { ...bookmark, ...updates, lastAccessed: new Date() }
              : bookmark
          )
        })),
    }),
    {
      name: 'ai-chat-user-state',
      partialize: (state) => ({
        recentActivities: state.recentActivities,
        bookmarks: state.bookmarks,
      })
    }
  )
)