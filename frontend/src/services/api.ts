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

// Workspace API
export const workspaceAPI = {
  getInfo: () =>
    apiClient.get('/workspace/info'),
  
  getContext: () =>
    apiClient.get('/workspace/context'),
  
  getTree: (maxDepth: number = 3) =>
    apiClient.get('/workspace/tree', { params: { max_depth: maxDepth } }),
  
  reindex: () =>
    apiClient.post('/workspace/index'),
}
