import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface AIProvider {
  id: string
  name: string
  displayName: string
  description: string
  baseUrl?: string
  models: AIModel[]
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface AIModel {
  id: string
  name: string
  displayName: string
  description: string
  contextWindow: number
  maxTokens: number
  pricing?: {
    input: number // per 1K tokens
    output: number // per 1K tokens
  }
  capabilities: string[]
}

export interface ProviderConfig {
  providerId: string
  apiKey: string
  baseUrl?: string
  organizationId?: string
  projectId?: string
  customHeaders?: Record<string, string>
  timeout?: number
  retryAttempts?: number
}

export interface CreateProviderData {
  name: string
  displayName: string
  description: string
  baseUrl?: string
  models: Omit<AIModel, 'id'>[]
}

export interface UpdateProviderData {
  displayName?: string
  description?: string
  baseUrl?: string
  models?: AIModel[]
  isActive?: boolean
}

interface ProvidersState {
  // State
  providers: AIProvider[]
  currentProvider: AIProvider | null
  providerConfigs: Record<string, ProviderConfig>
  isLoading: boolean
  error: string | null

  // Actions
  setProviders: (providers: AIProvider[]) => void
  setCurrentProvider: (provider: AIProvider | null) => void
  setProviderConfigs: (configs: Record<string, ProviderConfig>) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // API Actions
  loadProviders: () => Promise<void>
  loadProviderConfigs: () => Promise<void>
  createProvider: (data: CreateProviderData) => Promise<AIProvider>
  updateProvider: (id: string, data: UpdateProviderData) => Promise<AIProvider>
  deleteProvider: (id: string) => Promise<void>
  getProvider: (id: string) => Promise<AIProvider>

  // Config Actions
  saveProviderConfig: (config: ProviderConfig) => Promise<void>
  getProviderConfig: (providerId: string) => ProviderConfig | null
  deleteProviderConfig: (providerId: string) => Promise<void>

  // Utility Actions
  getActiveProviders: () => AIProvider[]
  getProviderByName: (name: string) => AIProvider | null
  validateProviderConfig: (providerId: string) => Promise<boolean>
}

export const useProvidersStore = create<ProvidersState>()(
  persist(
    (set: any, get: any) => ({
      // Initial state
      providers: [],
      currentProvider: null,
      providerConfigs: {},
      isLoading: false,
      error: null,

      // Basic setters
      setProviders: (providers: AIProvider[]) => set({ providers }),
      setCurrentProvider: (provider: AIProvider | null) => set({ currentProvider: provider }),
      setProviderConfigs: (configs: Record<string, ProviderConfig>) => set({ providerConfigs: configs }),
      setLoading: (loading: boolean) => set({ isLoading: loading }),
      setError: (error: string | null) => set({ error }),

      // API Actions
      loadProviders: async () => {
        set({ isLoading: true, error: null })
        try {
          // For now, return default providers
          // In a real implementation, this would call the API
          const defaultProviders: AIProvider[] = [
            {
              id: 'openai',
              name: 'openai',
              displayName: 'OpenAI',
              description: 'OpenAI GPT models including GPT-4, GPT-3.5, and DALL-E',
              baseUrl: 'https://api.openai.com/v1',
              isActive: true,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              models: [
                {
                  id: 'gpt-4',
                  name: 'gpt-4',
                  displayName: 'GPT-4',
                  description: 'Most capable GPT-4 model',
                  contextWindow: 8192,
                  maxTokens: 4096,
                  pricing: { input: 0.03, output: 0.06 },
                  capabilities: ['text', 'code', 'reasoning']
                },
                {
                  id: 'gpt-3.5-turbo',
                  name: 'gpt-3.5-turbo',
                  displayName: 'GPT-3.5 Turbo',
                  description: 'Fast and efficient GPT-3.5 model',
                  contextWindow: 4096,
                  maxTokens: 4096,
                  pricing: { input: 0.0015, output: 0.002 },
                  capabilities: ['text', 'code']
                }
              ]
            },
            {
              id: 'anthropic',
              name: 'anthropic',
              displayName: 'Anthropic',
              description: 'Claude models from Anthropic',
              baseUrl: 'https://api.anthropic.com',
              isActive: true,
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              models: [
                {
                  id: 'claude-3-opus',
                  name: 'claude-3-opus-20240229',
                  displayName: 'Claude 3 Opus',
                  description: 'Most capable Claude model',
                  contextWindow: 200000,
                  maxTokens: 4096,
                  pricing: { input: 0.015, output: 0.075 },
                  capabilities: ['text', 'code', 'reasoning', 'vision']
                },
                {
                  id: 'claude-3-sonnet',
                  name: 'claude-3-sonnet-20240229',
                  displayName: 'Claude 3 Sonnet',
                  description: 'Balanced Claude model',
                  contextWindow: 200000,
                  maxTokens: 4096,
                  pricing: { input: 0.003, output: 0.015 },
                  capabilities: ['text', 'code', 'reasoning', 'vision']
                }
              ]
            }
          ]

          set({ providers: defaultProviders, isLoading: false })

          // Load provider configs from backend
          await get().loadProviderConfigs()

          // Set first active provider as current if none selected
          const state = get()
          if (!state.currentProvider && defaultProviders.length > 0) {
            const activeProvider = defaultProviders.find(p => p.isActive) || defaultProviders[0]
            set({ currentProvider: activeProvider })
          }
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      loadProviderConfigs: async () => {
        try {
          console.log('[Frontend] Loading provider configs from backend')
          const state = get()
          const updatedConfigs: Record<string, ProviderConfig> = { ...state.providerConfigs }
          
          // Load config for each provider
          for (const provider of state.providers) {
            try {
              const response = await fetch(`http://localhost:8000/api/settings/api-providers/${provider.id}`)
              if (response.ok) {
                const providerSettings = await response.json()
                console.log(`[Frontend] Loaded config for provider ${provider.id}:`, providerSettings)
                
                // Convert backend response to ProviderConfig
                if (providerSettings && providerSettings.api_key) {
                  updatedConfigs[provider.id] = {
                    providerId: provider.id,
                    apiKey: providerSettings.api_key || '',
                    baseUrl: providerSettings.base_url,
                    organizationId: updatedConfigs[provider.id]?.organizationId, // Keep local value
                    projectId: updatedConfigs[provider.id]?.projectId, // Keep local value
                  }
                }
              }
            } catch (error) {
              console.log(`[Frontend] Could not load config for ${provider.id}:`, error)
            }
          }
          
          // Update store with all loaded configs
          set({ providerConfigs: updatedConfigs })
        } catch (error) {
          console.log('[Frontend] Error loading provider configs:', error)
          // Don't set error state since configs are optional
        }
      },

      createProvider: async (data: CreateProviderData) => {
        set({ isLoading: true, error: null })
        try {
          // In a real implementation, this would call the API
          const newProvider: AIProvider = {
            id: `provider-${Date.now()}`,
            ...data,
            isActive: true,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            models: data.models.map(model => ({
              ...model,
              id: `model-${Date.now()}-${Math.random()}`
            }))
          }

          const state = get()
          const updatedProviders = [...state.providers, newProvider]
          set({ providers: updatedProviders, isLoading: false })

          return newProvider
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      updateProvider: async (id: string, data: UpdateProviderData) => {
        set({ isLoading: true, error: null })
        try {
          // In a real implementation, this would call the API
          const state = get()
          const updatedProviders = state.providers.map(provider =>
            provider.id === id
              ? { ...provider, ...data, updatedAt: new Date().toISOString() }
              : provider
          )

          set({ providers: updatedProviders, isLoading: false })

          // Update current provider if it was modified
          const updatedProvider = updatedProviders.find(p => p.id === id)
          if (updatedProvider && state.currentProvider?.id === id) {
            set({ currentProvider: updatedProvider })
          }

          return updatedProvider!
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      deleteProvider: async (id: string) => {
        set({ isLoading: true, error: null })
        try {
          // In a real implementation, this would call the API
          const state = get()
          const updatedProviders = state.providers.filter(provider => provider.id !== id)
          set({ providers: updatedProviders, isLoading: false })

          // Clear current provider if it was deleted
          if (state.currentProvider?.id === id) {
            const activeProvider = updatedProviders.find(p => p.isActive) || updatedProviders[0] || null
            set({ currentProvider: activeProvider })
          }

          // Remove provider config
          const updatedConfigs = { ...state.providerConfigs }
          delete updatedConfigs[id]
          set({ providerConfigs: updatedConfigs })
        } catch (error) {
          set({ error: error instanceof Error ? error.message : 'Unknown error', isLoading: false })
          throw error
        }
      },

      getProvider: async (id: string) => {
        const state = get()
        const provider = state.providers.find(p => p.id === id)
        if (!provider) {
          throw new Error(`Provider with id ${id} not found`)
        }
        return provider
      },

      // Config Actions
      saveProviderConfig: async (config: ProviderConfig) => {
        set({ isLoading: true, error: null })
        try {
          // Call backend API to save provider settings (including API key to .env)
          console.log('[Frontend] Saving provider config:', { providerId: config.providerId, hasApiKey: !!config.apiKey })
          const url = `http://localhost:8000/api/settings/api-providers/${config.providerId}`
          console.log('[Frontend] Calling PUT', url)
          
          const response = await fetch(
            url,
            {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                provider_name: config.providerId,
                api_key: config.apiKey,
                base_url: config.baseUrl,
                // Note: organization_id and project_id are frontend-only fields
                // The backend APIProviderSettings model doesn't support them
              })
            }
          )

          console.log('[Frontend] Response status:', response.status, response.statusText)
          
          if (!response.ok) {
            const errorText = await response.text()
            console.log('[Frontend] Error response body:', errorText)
            console.error('[Frontend] ❌ HTTP Error:', response.status, response.statusText, errorText)
            // Don't throw - just update error state without re-throwing
            set({ isLoading: false, error: `Failed to save provider config: ${response.statusText}` })
            return // Exit without throwing
          }

          const responseData = await response.json()
          console.log('[Frontend] Success response:', responseData)

          // Update local store with the new config
          const state = get()
          const updatedConfigs = {
            ...state.providerConfigs,
            [config.providerId]: config
          }
          set({ providerConfigs: updatedConfigs, isLoading: false })
          console.log('[Frontend] ✅ Provider config saved successfully')
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Unknown error'
          console.error('[Frontend] ❌ Exception error saving provider config:', errorMsg)
          set({ error: errorMsg, isLoading: false })
          // Don't re-throw - let the caller handle it
        }
      },

      getProviderConfig: (providerId: string) => {
        const state = get()
        return state.providerConfigs[providerId] || null
      },

      deleteProviderConfig: async (providerId: string) => {
        const state = get()
        const updatedConfigs = { ...state.providerConfigs }
        delete updatedConfigs[providerId]
        set({ providerConfigs: updatedConfigs })
      },

      // Utility Actions
      getActiveProviders: () => {
        const state = get()
        return state.providers.filter(provider => provider.isActive)
      },

      getProviderByName: (name: string) => {
        const state = get()
        return state.providers.find(provider => provider.name === name) || null
      },

      validateProviderConfig: async (providerId: string) => {
        // In a real implementation, this would test the API key
        const config = get().getProviderConfig(providerId)
        return !!(config?.apiKey && config.apiKey.length > 0)
      }
    }),
    {
      name: 'ai-providers',
      // SECURITY: Intentionally NOT persisting providerConfigs which contain API keys
      // API keys are stored on backend only (.env file), never in browser localStorage
      // Without explicit partialize, Zustand persist will save the entire state by default,
      // but we rely on the backend to NOT include API keys when sending provider configs
      // Client-side code never reads/writes API keys directly
      partialize: (state: any) => ({
        currentProvider: state.currentProvider
      })
    } as any
  )
)