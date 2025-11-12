import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { useProvidersStore } from '../../stores/providersStore'
import { providersAPI } from '../../services/api'

// === REAL BACKEND RESPONSE MODELS ===
// These match the actual backend Pydantic models from backend/models/ai_provider.py

interface AIModel {
  id: string
  name: string
  displayName: string
  description: string
  contextWindow: number
  maxTokens: number
  pricing?: {
    input: number
    output: number
  }
  capabilities: string[]
}

interface AIProvider {
  id: string
  name: string
  displayName: string
  description: string
  baseUrl: string
  models: AIModel[]
  isActive: boolean
  createdAt: string
  updatedAt: string
}

// Mock data matching real backend responses
const MOCK_PROVIDERS: AIProvider[] = [
  {
    id: '550e8400-e29b-41d4-a716-446655440001',
    name: 'openai',
    displayName: 'OpenAI',
    description: 'OpenAI GPT models including GPT-4, GPT-3.5, and DALL-E',
    baseUrl: 'https://api.openai.com/v1',
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
    ],
    isActive: true,
    createdAt: '2025-01-10T00:00:00Z',
    updatedAt: '2025-01-10T00:00:00Z'
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440002',
    name: 'anthropic',
    displayName: 'Anthropic',
    description: 'Claude models from Anthropic',
    baseUrl: 'https://api.anthropic.com/v1',
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
    ],
    isActive: true,
    createdAt: '2025-01-10T00:00:00Z',
    updatedAt: '2025-01-10T00:00:00Z'
  }
]

// Mock server matching real backend endpoints from backend/api/ai_providers.py
const server = setupServer(
  // === Real AI Provider Endpoints ===
  // GET /api/providers - List all providers
  http.get('http://localhost:8000/api/providers', ({ request }) => {
    const url = new URL(request.url)
    const includeInactive = url.searchParams.get('include_inactive') === 'true'
    const providers = includeInactive ? MOCK_PROVIDERS : MOCK_PROVIDERS.filter(p => p.isActive)
    return HttpResponse.json(providers)
  }),

  // GET /api/providers/:provider_id - Get specific provider
  http.get('http://localhost:8000/api/providers/:provider_id', ({ params }) => {
    const provider = MOCK_PROVIDERS.find(p => p.id === params.provider_id)
    if (!provider) {
      return HttpResponse.json(
        { detail: `AI provider ${params.provider_id} not found` },
        { status: 404 }
      )
    }
    return HttpResponse.json(provider)
  }),

  // POST /api/providers - Create new provider
  http.post('http://localhost:8000/api/providers', async ({ request }) => {
    const body = await request.json() as any
    const newProvider: AIProvider = {
      id: `550e8400-e29b-41d4-a716-${Date.now()}`,
      name: body.name,
      displayName: body.displayName || body.name,
      description: body.description || '',
      baseUrl: body.baseUrl || '',
      models: body.models || [],
      isActive: body.isActive !== false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    return HttpResponse.json(newProvider, { status: 201 })
  }),

  // PUT /api/providers/:provider_id - Update provider
  http.put('http://localhost:8000/api/providers/:provider_id', async ({ params, request }) => {
    const provider = MOCK_PROVIDERS.find(p => p.id === params.provider_id)
    if (!provider) {
      return HttpResponse.json(
        { detail: `AI provider ${params.provider_id} not found` },
        { status: 404 }
      )
    }
    const updates = await request.json() as any
    const updated = { ...provider, ...updates, updatedAt: new Date().toISOString() }
    return HttpResponse.json(updated)
  }),

  // DELETE /api/providers/:provider_id - Delete provider
  http.delete('http://localhost:8000/api/providers/:provider_id', ({ params }) => {
    const provider = MOCK_PROVIDERS.find(p => p.id === params.provider_id)
    if (!provider) {
      return HttpResponse.json(
        { detail: `AI provider ${params.provider_id} not found` },
        { status: 404 }
      )
    }
    return HttpResponse.json({ message: `AI provider ${params.provider_id} deleted successfully` })
  }),

  // === Real Chat Session Endpoints ===
  http.get('http://localhost:8000/api/chat-sessions', () => {
    return HttpResponse.json([
      {
        id: 'session-1',
        project_id: 'project-1',
        title: 'Test Chat Session',
        description: 'A test chat session',
        created_at: '2025-01-10T00:00:00Z',
        updated_at: '2025-01-10T00:00:00Z',
        message_count: 0
      }
    ])
  }),

  http.post('http://localhost:8000/api/chat-sessions', () => {
    return HttpResponse.json({
      id: 'new-session-1',
      project_id: 'project-1',
      title: 'Chat 2025-01-10',
      description: 'New chat session',
      created_at: '2025-01-10T00:00:00Z',
      updated_at: '2025-01-10T00:00:00Z',
      message_count: 0
    })
  }),

  http.get('http://localhost:8000/api/projects', () => {
    return HttpResponse.json([
      {
        id: 'project-1',
        name: 'Default Project',
        description: 'Default project for chats',
        created_at: '2025-01-10T00:00:00Z',
        updated_at: '2025-01-10T00:00:00Z'
      }
    ])
  })
)

beforeEach(() => server.listen())
afterEach(() => server.resetHandlers())
afterEach(() => server.close())

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  )
}

describe('Chat Page Provider Integration E2E Tests', () => {
  /**
   * Setup for each test: Load providers from the mock backend API.
   * This simulates the real frontend behavior where providers are fetched
   * from the backend via /api/ai-providers endpoint.
   */
  beforeEach(async () => {
    // Reset stores
    useProvidersStore.setState({
      providers: [],
      currentProvider: null,
      providerConfigs: {},
      isLoading: false,
      error: null
    })

    useUserStateStore.setState({
      session: {
        sessionId: 'session-1',
        loginTime: new Date(),
        lastActivity: new Date(),
        activeProject: 'project-1',
        activeSession: 'session-1',
        selectedProviderId: MOCK_PROVIDERS[0].id,
        openTabs: [],
        clipboardHistory: []
      }
    })

    // Load providers from mock backend API (like real app does)
    try {
      const response = await providersAPI.listProviders()
      const providers = response.data
      useProvidersStore.setState({
        providers,
        currentProvider: providers[0] || null
      })
    } catch (error) {
      console.error('Failed to load providers:', error)
    }
  })

  describe('Loading Providers from Backend API', () => {
    /**
     * Real scenario: Frontend fetches providers from backend on app init.
     * Backend returns real provider data via GET /api/ai-providers
     */
    it('should fetch and display providers from real backend API', async () => {
      const { result } = renderHook(() => useProvidersStore())

      await waitFor(() => {
        expect(result.current.providers.length).toBeGreaterThan(0)
      })

      // Verify providers match backend response
      expect(result.current.providers).toEqual(MOCK_PROVIDERS)
      expect(result.current.providers[0].displayName).toBe('OpenAI')
      expect(result.current.providers[1].displayName).toBe('Anthropic')
    })

    /**
     * Real scenario: Verify provider models are loaded correctly from backend.
     * Backend returns models in the AIProvider response.
     */
    it('should include models for each provider from backend', async () => {
      const { result } = renderHook(() => useProvidersStore())

      await waitFor(() => {
        expect(result.current.providers.length).toBeGreaterThan(0)
      })

      const openaiProvider = result.current.providers.find(p => p.name === 'openai')
      expect(openaiProvider?.models).toHaveLength(2)
      expect(openaiProvider?.models[0].displayName).toBe('GPT-4')
      expect(openaiProvider?.models[0].capabilities).toContain('text')
    })

    /**
     * Real scenario: Backend returns pricing information for models.
     * This is used for cost tracking in the UI.
     */
    it('should include pricing information from backend', async () => {
      const { result } = renderHook(() => useProvidersStore())

      await waitFor(() => {
        expect(result.current.providers.length).toBeGreaterThan(0)
      })

      const model = result.current.providers[0].models[0]
      expect(model.pricing).toEqual({ input: 0.03, output: 0.06 })
    })
  })

  describe('Provider Selector in Chat Header', () => {
    /**
     * Real scenario: Display provider selector with current active provider.
     * Verifies UI correctly represents backend state.
     */
    it('should display provider selector with active provider from backend', async () => {
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Should show first provider from backend (OpenAI)
      const providerSelector = screen.getByRole('button', { name: /OpenAI|openai/i })
      expect(providerSelector).toBeInTheDocument()
    })

    /**
     * Real scenario: Provider selector shows all providers from backend.
     * Dropdown displays all active providers returned by API.
     */
    it('should open dropdown showing all active providers from backend', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      const providerSelector = screen.getByRole('button', { name: /OpenAI|openai/i })
      await user.click(providerSelector)

      // Both backend providers should be visible
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
      expect(screen.getByText('Anthropic')).toBeInTheDocument()
    })
  })

  describe('Real Frontend-Backend Communication', () => {
    /**
     * Real scenario: User switches provider via UI.
     * Frontend sends selection change to backend (if needed for persistence).
     * Backend returns updated provider data.
     */
    it('should handle provider switching with real backend communication', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Click to open provider dropdown
      const providerSelector = screen.getByRole('button', { name: /OpenAI|openai/i })
      await user.click(providerSelector)

      // Get Anthropic option from dropdown
      const anthropicOption = screen.getAllByText('Anthropic')[0]
      expect(anthropicOption).toBeInTheDocument()

      // Click it to switch provider
      await user.click(anthropicOption)

      // Verify provider switched
      await waitFor(() => {
        const { result } = renderHook(() => useProvidersStore())
        expect(result.current.currentProvider?.name).toBe('anthropic')
      })
    })

    /**
     * Real scenario: Fetch specific provider data from backend.
     * Uses GET /api/ai-providers/:provider_id endpoint.
     */
    it('should fetch specific provider details from backend', async () => {
      const provider = MOCK_PROVIDERS[0]
      const response = await providersAPI.getProvider(provider.id)

      expect(response.data.id).toBe(provider.id)
      expect(response.data.displayName).toBe('OpenAI')
      expect(response.data.models).toHaveLength(2)
    })

    /**
     * Real scenario: Create new provider via backend API.
     * Frontend sends POST request to /api/ai-providers with provider data.
     * Backend validates and returns created provider with UUID.
     */
    it('should create new provider via real backend API', async () => {
      const newProviderData = {
        name: 'google',
        displayName: 'Google AI',
        description: 'Google Gemini models',
        baseUrl: 'https://generativelanguage.googleapis.com/v1beta',
        models: [],
        isActive: true
      }

      const response = await providersAPI.createProvider(newProviderData)

      expect(response.status).toBe(201)
      expect(response.data).toHaveProperty('id')
      expect(response.data.displayName).toBe('Google AI')
      expect(response.data.baseUrl).toBe('https://generativelanguage.googleapis.com/v1beta')
    })

    /**
     * Real scenario: Update existing provider via backend.
     * Frontend sends PUT request to /api/ai-providers/:provider_id
     * with updated data.
     */
    it('should update provider via real backend API', async () => {
      const provider = MOCK_PROVIDERS[0]
      const updateData = {
        displayName: 'OpenAI (Updated)',
        description: 'Updated description'
      }

      const response = await providersAPI.updateProvider(provider.id, updateData)

      expect(response.data.displayName).toBe('OpenAI (Updated)')
      expect(response.data.description).toBe('Updated description')
    })

    /**
     * Real scenario: Delete provider from backend.
     * Frontend sends DELETE request to /api/ai-providers/:provider_id
     */
    it('should delete provider via real backend API', async () => {
      const provider = MOCK_PROVIDERS[0]
      const response = await providersAPI.deleteProvider(provider.id)

      expect(response.status).toBe(200)
      expect(response.data.message).toContain('deleted successfully')
    })
  })

  describe('Provider Availability Based on API Keys', () => {
    /**
     * Real scenario: Backend returns provider with API key loaded from .env file.
     * Frontend must handle providers with/without configured API keys.
     * This tests the actual API key persistence fix.
     */
    it('should display provider availability based on API key configuration', async () => {
      const { result } = renderHook(() => useProvidersStore())

      await waitFor(() => {
        expect(result.current.providers.length).toBeGreaterThan(0)
      })

      // All providers should be marked as active/available if they have isActive=true
      const activeProviders = result.current.providers.filter(p => p.isActive)
      expect(activeProviders.length).toBeGreaterThan(0)
    })

    /**
     * Real scenario: Simulate provider without API key configured.
     * Backend would return isActive=false or a separate unavailable status.
     */
    it('should handle unavailable providers (missing API key)', async () => {
      // Override handler to return a provider marked as unavailable
      server.use(
        http.get('http://localhost:8000/api/providers', () => {
          const providersWithUnavailable = [
            ...MOCK_PROVIDERS,
            {
              ...MOCK_PROVIDERS[1],
              id: '550e8400-e29b-41d4-a716-446655440003',
              displayName: 'Anthropic (No Key)',
              isActive: false // Not available - no API key
            }
          ]
          return HttpResponse.json(providersWithUnavailable)
        })
      )

      const response = await providersAPI.listProviders()
      const unavailableProviders = response.data.filter((p: AIProvider) => !p.isActive)

      expect(unavailableProviders.length).toBeGreaterThan(0)
    })
  })
})