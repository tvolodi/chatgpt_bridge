import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Chat API
export const chatAPI = {
  sendMessage: (sessionId: string, message: string, model?: string) =>
    apiClient.post('/chat/send', {
      session_id: sessionId,
      message,
      model,
      include_workspace_context: true,
    }),
  
  getHistory: (sessionId: string) =>
    apiClient.get(`/chat/history/${sessionId}`),
  
  createSession: () =>
    apiClient.post('/chat/sessions'),
  
  deleteSession: (sessionId: string) =>
    apiClient.delete(`/chat/sessions/${sessionId}`),
}

// Files API
export const filesAPI = {
  listFiles: (directory: string = '/') =>
    apiClient.get('/files/list', { params: { directory } }),
  
  readFile: (path: string) =>
    apiClient.get('/files/read', { params: { path } }),
  
  writeFile: (path: string, content: string) =>
    apiClient.post('/files/write', { path, content }),
  
  searchFiles: (query: string, directory: string = '/') =>
    apiClient.post('/files/search', { query, directory }),
}

// Settings API
export const settingsAPI = {
  getSettings: () =>
    apiClient.get('/settings'),

  updateSettings: (settings: any) =>
    apiClient.put('/settings', settings),

  getSettingsByCategory: (category: string) =>
    apiClient.get(`/settings/${category}`),

  updateSettingsByCategory: (category: string, settings: any) =>
    apiClient.put(`/settings/${category}`, settings),

  exportSettings: () =>
    apiClient.get('/settings/export'),

  importSettings: (settings: any) =>
    apiClient.post('/settings/import', settings),
}

// Search API
export const searchAPI = {
  search: (query: string, filters?: any) =>
    apiClient.post('/search', { query, filters }),

  getSuggestions: (query: string) =>
    apiClient.get('/search/suggest', { params: { q: query } }),

  buildIndex: () =>
    apiClient.post('/search/index/build'),

  getSearchAnalytics: () =>
    apiClient.get('/search/analytics'),
}

// User State API
export const userStateAPI = {
  // Preferences
  getPreferences: (userId: string) =>
    apiClient.get('/user-state/preferences', { params: { user_id: userId } }),

  updatePreferences: (userId: string, preferences: any) =>
    apiClient.put('/user-state/preferences', preferences, { params: { user_id: userId } }),

  // UI State
  getUIState: (userId: string) =>
    apiClient.get('/user-state/ui-state', { params: { user_id: userId } }),

  updateUIState: (userId: string, uiState: any) =>
    apiClient.put('/user-state/ui-state', uiState, { params: { user_id: userId } }),

  // Session State
  getSessionState: (userId: string, sessionId: string) =>
    apiClient.get('/user-state/session/${sessionId}', { params: { user_id: userId } }),

  updateSessionState: (userId: string, sessionState: any) =>
    apiClient.put('/user-state/session', sessionState, { params: { user_id: userId } }),

  // Recent Activity
  addRecentActivity: (userId: string, activity: any) =>
    apiClient.post('/user-state/activity', activity, { params: { user_id: userId } }),

  getRecentActivities: (userId: string, limit?: number) =>
    apiClient.get('/user-state/activity', { params: { user_id: userId, limit } }),

  // Bookmarks
  addBookmark: (userId: string, bookmark: any) =>
    apiClient.post('/user-state/bookmarks', bookmark, { params: { user_id: userId } }),

  getBookmarks: (userId: string) =>
    apiClient.get('/user-state/bookmarks', { params: { user_id: userId } }),

  deleteBookmark: (userId: string, bookmarkId: string) =>
    apiClient.delete('/user-state/bookmarks/${bookmarkId}', { params: { user_id: userId } }),

  // Backup and Analytics
  createBackup: (userId: string) =>
    apiClient.post('/user-state/backup', null, { params: { user_id: userId } }),

  getAnalytics: (userId: string) =>
    apiClient.get('/user-state/analytics', { params: { user_id: userId } }),
}
