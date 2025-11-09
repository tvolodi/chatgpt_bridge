import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  layout: 'compact' | 'comfortable' | 'spacious'
  language: string
  timezone: string
  dateFormat: string
  timeFormat: '12h' | '24h'
  notifications: {
    enabled: boolean
    soundEnabled: boolean
    desktopNotifications: boolean
    emailNotifications: boolean
    notificationTypes: Record<string, boolean>
  }
  autoSave: boolean
  autoSaveInterval: number
  keyboardShortcuts: Record<string, string>
}

export interface UIState {
  sidebarCollapsed: boolean
  activePanel?: string
  windowSize?: { width: number; height: number }
  windowPosition?: { x: number; y: number }
  splitPaneSizes?: number[]
  expandedSections: string[]
  lastViewedProject?: string
  lastViewedSession?: string
}

interface SettingsState {
  preferences: UserPreferences
  uiState: UIState

  // Actions
  updatePreferences: (preferences: Partial<UserPreferences>) => void
  updateUIState: (uiState: Partial<UIState>) => void
  resetToDefaults: () => void
}

const defaultPreferences: UserPreferences = {
  theme: 'system',
  layout: 'comfortable',
  language: 'en',
  timezone: 'UTC',
  dateFormat: 'YYYY-MM-DD',
  timeFormat: '24h',
  notifications: {
    enabled: true,
    soundEnabled: true,
    desktopNotifications: true,
    emailNotifications: false,
    notificationTypes: {}
  },
  autoSave: true,
  autoSaveInterval: 30,
  keyboardShortcuts: {}
}

const defaultUIState: UIState = {
  sidebarCollapsed: false,
  expandedSections: [],
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set, get) => ({
      preferences: defaultPreferences,
      uiState: defaultUIState,

      updatePreferences: (newPreferences) =>
        set((state) => ({
          preferences: { ...state.preferences, ...newPreferences }
        })),

      updateUIState: (newUIState) =>
        set((state) => ({
          uiState: { ...state.uiState, ...newUIState }
        })),

      resetToDefaults: () =>
        set({
          preferences: defaultPreferences,
          uiState: defaultUIState
        })
    }),
    {
      name: 'ai-chat-settings',
      partialize: (state) => ({
        preferences: state.preferences,
        uiState: state.uiState
      })
    }
  )
)