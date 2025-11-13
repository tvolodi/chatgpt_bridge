import axios from 'axios'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api'
const BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Separate client for user-state API (doesn't use /api prefix)
export const userStateClient = axios.create({
  baseURL: BASE_URL,
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
  getSettings: (userId?: string) =>
    userId
      ? apiClient.get(`/settings/user/${userId}/effective`)
      : apiClient.get('/settings/default'),

  updateSettings: (settings: any, userId?: string) => {
    // For now, we'll update default settings if no userId provided
    // In a real app, you'd want to update user-specific settings
    const settingsId = userId || 'default';
    return apiClient.put(`/settings/${settingsId}`, settings);
  },

  getSettingsByCategory: (category: string, userId?: string) =>
    apiClient.get(`/settings/categories/${category}`, {
      params: userId ? { user_id: userId } : {}
    }),

  updateSettingsByCategory: (category: string, settings: any, userId?: string) =>
    apiClient.put(`/settings/categories/${category}`, settings, {
      params: userId ? { user_id: userId } : {}
    }),

  exportSettings: (settingsId?: string) =>
    apiClient.get(`/settings/${settingsId || 'default'}/export`),

  importSettings: (settings: any) =>
    apiClient.post('/settings/import', settings),

  validateSettings: (settings: any) =>
    apiClient.post('/settings/validate', settings),
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
    userStateClient.get('/user-state/preferences', { params: { user_id: userId } }),

  updatePreferences: (userId: string, preferences: any) =>
    userStateClient.put('/user-state/preferences', preferences, { params: { user_id: userId } }),

  // UI State
  getUIState: (userId: string) =>
    userStateClient.get('/user-state/ui-state', { params: { user_id: userId } }),

  updateUIState: (userId: string, uiState: any) =>
    userStateClient.put('/user-state/ui-state', uiState, { params: { user_id: userId } }),

  // Session State
  getSessionState: (userId: string, sessionId: string) =>
    userStateClient.get(`/user-state/session/${sessionId}`, { params: { user_id: userId } }),

  updateSessionState: (userId: string, sessionState: any) =>
    userStateClient.put('/user-state/session', sessionState, { params: { user_id: userId } }),

  // Recent Activity
  addRecentActivity: (userId: string, activity: any) =>
    userStateClient.post('/user-state/activity', activity, { params: { user_id: userId } }),

  getRecentActivities: (userId: string, limit?: number) =>
    userStateClient.get('/user-state/activity', { params: { user_id: userId, limit } }),

  // Bookmarks
  addBookmark: (userId: string, bookmark: any) =>
    userStateClient.post('/user-state/bookmarks', bookmark, { params: { user_id: userId } }),

  getBookmarks: (userId: string) =>
    userStateClient.get('/user-state/bookmarks', { params: { user_id: userId } }),

  deleteBookmark: (userId: string, bookmarkId: string) =>
    userStateClient.delete(`/user-state/bookmarks/${bookmarkId}`, { params: { user_id: userId } }),

  // Backup and Analytics
  createBackup: (userId: string) =>
    userStateClient.post('/user-state/backup', null, { params: { user_id: userId } }),

  getAnalytics: (userId: string) =>
    userStateClient.get('/user-state/analytics', { params: { user_id: userId } }),
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

// Providers API
export const providersAPI = {
  // List providers
  listProviders: () =>
    apiClient.get('/ai-providers'),

  // Get single provider
  getProvider: (providerId: string) =>
    apiClient.get(`/ai-providers/${providerId}`),

  // Create provider
  createProvider: (providerData: any) =>
    apiClient.post('/ai-providers', providerData),

  // Update provider
  updateProvider: (providerId: string, updateData: any) =>
    apiClient.put(`/ai-providers/${providerId}`, updateData),

  // Delete provider
  deleteProvider: (providerId: string) =>
    apiClient.delete(`/ai-providers/${providerId}`),

  // Get provider config - NOTE: This should use settings API, not providers API
  getProviderConfig: (providerId: string) =>
    apiClient.get(`/settings/api-providers/${providerId}`),

  // Update provider config - NOTE: This should use settings API, not providers API
  updateProviderConfig: (providerId: string, configData: any) =>
    apiClient.put(`/settings/api-providers/${providerId}`, configData),

  // Delete provider config - NOTE: This should use settings API, not providers API
  deleteProviderConfig: (providerId: string) =>
    apiClient.delete(`/settings/api-providers/${providerId}`),

  // Validate provider config - NOTE: Backend doesn't have this endpoint, removing
  // validateProviderConfig: (providerId: string) =>
  //   apiClient.post(`/providers/${providerId}/validate`),

  // Get available models for provider - NOTE: Backend serves this as global endpoint
  getProviderModels: () =>
    apiClient.get('/ai-providers/models/available'),
}

// Templates API
export const templatesAPI = {
  // List templates
  listTemplates: (projectId?: string, category?: string) =>
    apiClient.get('/templates/', { params: { project_id: projectId, category } }),

  // Create template
  createTemplate: (templateData: any) =>
    apiClient.post('/templates/', templateData),

  // Get template
  getTemplate: (templateId: string) =>
    apiClient.get(`/templates/${templateId}`),

  // Update template
  updateTemplate: (templateId: string, updateData: any) =>
    apiClient.put(`/templates/${templateId}`, updateData),

  // Delete template
  deleteTemplate: (templateId: string) =>
    apiClient.delete(`/templates/${templateId}`),

  // Get categories
  getCategories: () =>
    apiClient.get('/templates/categories/'),

  // Substitute template parameters
  substituteTemplate: (templateId: string, parameters: Record<string, string>) =>
    apiClient.post(`/templates/${templateId}/substitute`, { parameters }),

  // Get template placeholders
  getTemplatePlaceholders: (templateId: string) =>
    apiClient.get(`/templates/${templateId}/placeholders`),
}
