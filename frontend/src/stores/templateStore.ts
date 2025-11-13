import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { templatesAPI } from '../services/api'

export interface MessageTemplate {
  id: string
  name: string
  content: string
  category: string
  project_id?: string
  description?: string
  created_at: string
  updated_at: string
}

export interface MessageTemplateSummary {
  id: string
  name: string
  category: string
  description?: string
  project_id?: string
  created_at: string
  updated_at: string
}

export interface TemplateCategory {
  name: string
  count: number
  description?: string
}

export interface CreateTemplateData {
  name: string
  content: string
  category?: string
  project_id?: string
  description?: string
}

export interface UpdateTemplateData {
  name?: string
  content?: string
  category?: string
  project_id?: string
  description?: string
}

export interface TemplateSubstitutionResult {
  template_id: string
  original_content: string
  substituted_content: string
  placeholders_found: string[]
}

interface TemplateState {
  // State
  templates: MessageTemplateSummary[]
  categories: TemplateCategory[]
  selectedTemplate: MessageTemplate | null
  isLoading: boolean
  error: string | null

  // Actions
  setTemplates: (templates: MessageTemplateSummary[]) => void
  setCategories: (categories: TemplateCategory[]) => void
  setSelectedTemplate: (template: MessageTemplate | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // API Actions
  loadTemplates: (projectId?: string, category?: string) => Promise<void>
  loadCategories: () => Promise<void>
  createTemplate: (data: CreateTemplateData) => Promise<MessageTemplate>
  updateTemplate: (id: string, data: UpdateTemplateData) => Promise<MessageTemplate>
  deleteTemplate: (id: string) => Promise<void>
  getTemplate: (id: string) => Promise<MessageTemplate>
  substituteTemplate: (id: string, parameters: Record<string, string>) => Promise<TemplateSubstitutionResult>
  getTemplatePlaceholders: (id: string) => Promise<string[]>
}

export const useTemplateStore = create<TemplateState>()(
  persist(
    (set, get) => ({
      // Initial state
      templates: [],
      categories: [],
      selectedTemplate: null,
      isLoading: false,
      error: null,

      // Basic setters
      setTemplates: (templates) => set({ templates }),
      setCategories: (categories) => set({ categories }),
      setSelectedTemplate: (template) => set({ selectedTemplate: template }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),

      // API Actions
      loadTemplates: async (projectId, category) => {
        set({ isLoading: true, error: null })
        try {
          const response = await templatesAPI.listTemplates(projectId, category)
          set({ templates: response.data, isLoading: false })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      loadCategories: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await templatesAPI.getCategories()
          set({ categories: response.data, isLoading: false })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      createTemplate: async (data) => {
        set({ isLoading: true, error: null })
        try {
          const response = await templatesAPI.createTemplate(data)
          set({ isLoading: false })
          // Reload templates to reflect the new template
          await get().loadTemplates()
          await get().loadCategories()
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      updateTemplate: async (id, data) => {
        set({ isLoading: true, error: null })
        try {
          const response = await templatesAPI.updateTemplate(id, data)
          set({ isLoading: false })
          // Reload templates to reflect the update
          await get().loadTemplates()
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      deleteTemplate: async (id) => {
        set({ isLoading: true, error: null })
        try {
          await templatesAPI.deleteTemplate(id)
          set({ isLoading: false })
          // Reload templates to reflect the deletion
          await get().loadTemplates()
          await get().loadCategories()
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      getTemplate: async (id) => {
        set({ isLoading: true, error: null })
        try {
          const response = await templatesAPI.getTemplate(id)
          const template = response.data
          set({ selectedTemplate: template, isLoading: false })
          return template
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      substituteTemplate: async (id, parameters) => {
        set({ isLoading: true, error: null })
        try {
          const response = await templatesAPI.substituteTemplate(id, parameters)
          set({ isLoading: false })
          return response.data
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      getTemplatePlaceholders: async (id) => {
        set({ isLoading: true, error: null })
        try {
          const response = await templatesAPI.getTemplatePlaceholders(id)
          set({ isLoading: false })
          return response.data.placeholders
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      }
    }),
    {
      name: 'ai-chat-templates',
      partialize: (state) => ({
        selectedTemplate: state.selectedTemplate
      })
    }
  )
)