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
    apiClient.get('/settings/user/default/effective'),

  updateSettings: (settings: any) =>
    apiClient.put('/settings/user/default', settings),

  getSettingsByCategory: (category: string) =>
    apiClient.get(`/settings/categories/${category}`),

  updateSettingsByCategory: (category: string, settings: any) =>
    apiClient.put(`/settings/categories/${category}`, settings),

  exportSettings: () =>
    apiClient.get('/settings/default/export'),

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

// Projects API
export const projectsAPI = {
  // List projects
  listProjects: (parentId?: string) =>
    apiClient.get('/projects', { params: parentId ? { parent_id: parentId } : {} }),

  // Get single project
  getProject: (projectId: string) =>
    apiClient.get(`/projects/${projectId}`),

  // Create project
  createProject: (projectData: any) =>
    apiClient.post('/projects', projectData),

  // Update project
  updateProject: (projectId: string, updateData: any) =>
    apiClient.put(`/projects/${projectId}`, updateData),

  // Delete project
  deleteProject: (projectId: string, force: boolean = false) =>
    apiClient.delete(`/projects/${projectId}`, { params: { force } }),

  // Project tree
  getProjectTree: (projectId?: string) =>
    projectId
      ? apiClient.get(`/projects/${projectId}/tree`)
      : apiClient.get('/projects/tree/all'),

  // Project stats
  getProjectStats: () =>
    apiClient.get('/projects/stats/overview'),
}

// Chat Sessions API
export const chatSessionsAPI = {
  // List chat sessions
  listSessions: (projectId?: string, includeInactive: boolean = false) =>
    apiClient.get('/chat-sessions', {
      params: {
        ...(projectId && { project_id: projectId }),
        ...(includeInactive && { include_inactive: includeInactive })
      }
    }),

  // Get single chat session
  getSession: (sessionId: string) =>
    apiClient.get(`/chat-sessions/${sessionId}`),

  // Create chat session
  createSession: (sessionData: any) =>
    apiClient.post('/chat-sessions', sessionData),

  // Update chat session
  updateSession: (sessionId: string, updateData: any) =>
    apiClient.put(`/chat-sessions/${sessionId}`, updateData),

  // Delete chat session
  deleteSession: (sessionId: string, force: boolean = false) =>
    apiClient.delete(`/chat-sessions/${sessionId}`, { params: { force } }),

  // Get session with messages
  getSessionWithMessages: (sessionId: string) =>
    apiClient.get(`/chat-sessions/${sessionId}/full`),

  // Add message to session
  addMessage: (sessionId: string, messageData: any) =>
    apiClient.post(`/chat-sessions/${sessionId}/messages`, messageData),

  // Get session messages
  getSessionMessages: (sessionId: string, limit?: number, offset: number = 0) =>
    apiClient.get(`/chat-sessions/${sessionId}/messages`, {
      params: {
        ...(limit && { limit }),
        offset
      }
    }),

  // Get session stats
  getSessionStats: (projectId?: string) =>
    apiClient.get('/chat-sessions/stats/summary', {
      params: projectId ? { project_id: projectId } : {}
    }),
}
