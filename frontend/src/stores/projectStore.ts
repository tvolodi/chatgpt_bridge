import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { projectsAPI } from '../services/api'

export interface Project {
  id: string
  name: string
  description?: string
  parent_id?: string
  created_at: string
  updated_at: string
  path: string
}

export interface ProjectSummary {
  id: string
  name: string
  description?: string
  parent_id?: string
  created_at: string
  updated_at: string
  has_children: boolean
  children_count: number
}

export interface ProjectTree {
  project: Project
  children: ProjectTree[]
}

export interface ProjectStats {
  total_projects: number
  total_sessions: number
  total_messages: number
  total_files: number
  storage_size: number
}

export interface CreateProjectData {
  name: string
  description?: string
  parent_id?: string
}

export interface UpdateProjectData {
  name?: string
  description?: string
  parent_id?: string
}

interface ProjectState {
  // State
  currentProject: Project | null
  projects: ProjectSummary[]
  projectTree: ProjectTree[]
  isLoading: boolean
  error: string | null

  // Actions
  setCurrentProject: (project: Project | null) => void
  setProjects: (projects: ProjectSummary[]) => void
  setProjectTree: (tree: ProjectTree[]) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // API Actions
  loadProjects: (parentId?: string) => Promise<void>
  loadProjectTree: () => Promise<void>
  createProject: (data: CreateProjectData) => Promise<Project>
  updateProject: (id: string, data: UpdateProjectData) => Promise<Project>
  deleteProject: (id: string, force?: boolean) => Promise<void>
  getProject: (id: string) => Promise<Project>
  getProjectStats: () => Promise<ProjectStats>
}

export const useProjectStore = create<ProjectState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentProject: null,
      projects: [],
      projectTree: [],
      isLoading: false,
      error: null,

      // Basic setters
      setCurrentProject: (project) => set({ currentProject: project }),
      setProjects: (projects) => set({ projects }),
      setProjectTree: (tree) => set({ projectTree: tree }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),

      // API Actions
      loadProjects: async (parentId) => {
        set({ isLoading: true, error: null })
        try {
          const response = await projectsAPI.listProjects(parentId)
          set({ projects: response.data, isLoading: false })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      loadProjectTree: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await projectsAPI.getProjectTree()
          set({ projectTree: response.data, isLoading: false })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      createProject: async (data) => {
        set({ isLoading: true, error: null })
        try {
          const response = await projectsAPI.createProject(data)
          set({ isLoading: false })
          // Reload projects to reflect the new project
          await get().loadProjects()
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      updateProject: async (id, data) => {
        set({ isLoading: true, error: null })
        try {
          const response = await projectsAPI.updateProject(id, data)
          set({ isLoading: false })
          // Reload projects to reflect the update
          await get().loadProjects()
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      deleteProject: async (id, force = false) => {
        set({ isLoading: true, error: null })
        try {
          await projectsAPI.deleteProject(id, force)
          set({ isLoading: false })
          // Reload projects to reflect the deletion
          await get().loadProjects()
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      getProject: async (id) => {
        set({ isLoading: true, error: null })
        try {
          const response = await projectsAPI.getProject(id)
          set({ isLoading: false })
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      getProjectStats: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await projectsAPI.getProjectStats()
          set({ isLoading: false })
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      }
    }),
    {
      name: 'ai-chat-projects',
      partialize: (state) => ({
        currentProject: state.currentProject
      })
    }
  )
)