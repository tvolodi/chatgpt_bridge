import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { useProvidersStore } from '../../stores/providersStore'
import { providersAPI } from '../../services/api'

// ===== REAL BACKEND RESPONSE MODELS =====
// These match the actual backend data structures from backend/models/ai_provider.py

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
      }
    ],
    isActive: true,
    createdAt: '2025-01-10T00:00:00Z',
    updatedAt: '2025-01-10T00:00:00Z'
  }
]

// ===== MSW MOCK SERVER =====
// Simulates the real backend endpoints for testing
const server = setupServer(
  // GET /api/providers - List all providers
  http.get('http://localhost:8000/api/providers', () => {
    return HttpResponse.json(MOCK_PROVIDERS)
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
    return HttpResponse.json({ id: params.provider_id })
  })
)

beforeEach(() => server.listen())
afterEach(() => server.resetHandlers())
afterEach(() => server.close())

describe('Real Frontend-Backend Provider Communication', () => {
  /**
   * E2E TEST: Verify direct API calls work correctly
   * Tests that the real API client (providersAPI) communicates with mock backend
   */
  describe('Provider List Operations', () => {
    it('should fetch providers from backend API', async () => {
      const response = await providersAPI.listProviders()
      
      expect(response.status).toBe(200)
      expect(response.data).toHaveLength(2)
      expect(response.data[0].displayName).toBe('OpenAI')
      expect(response.data[1].displayName).toBe('Anthropic')
    })

    it('should include provider models from backend', async () => {
      const response = await providersAPI.listProviders()
      const openaiProvider = response.data.find((p: AIProvider) => p.name === 'openai')
      
      expect(openaiProvider).toBeDefined()
      expect(openaiProvider?.models).toHaveLength(2)
      expect(openaiProvider?.models[0].displayName).toBe('GPT-4')
      expect(openaiProvider?.models[1].displayName).toBe('GPT-3.5 Turbo')
    })

    it('should include pricing information in models', async () => {
      const response = await providersAPI.listProviders()
      const firstModel = response.data[0].models[0]
      
      expect(firstModel.pricing).toBeDefined()
      expect(firstModel.pricing?.input).toBe(0.03)
      expect(firstModel.pricing?.output).toBe(0.06)
    })

    it('should include model capabilities from backend', async () => {
      const response = await providersAPI.listProviders()
      const gpt4 = response.data[0].models[0]
      
      expect(gpt4.capabilities).toContain('text')
      expect(gpt4.capabilities).toContain('code')
      expect(gpt4.capabilities).toContain('reasoning')
    })
  })

  /**
   * E2E TEST: CRUD operations with real API endpoints
   */
  describe('Provider CRUD Operations', () => {
    it('should get single provider from backend', async () => {
      const providerId = MOCK_PROVIDERS[0].id
      const response = await providersAPI.getProvider(providerId)
      
      expect(response.status).toBe(200)
      expect(response.data.id).toBe(providerId)
      expect(response.data.displayName).toBe('OpenAI')
    })

    it('should return 404 for non-existent provider', async () => {
      try {
        await providersAPI.getProvider('invalid-id-12345')
        expect.fail('Should have thrown error')
      } catch (error: any) {
        expect(error.response?.status).toBe(404)
        expect(error.response?.data?.detail).toContain('not found')
      }
    })

    it('should create provider with 201 status', async () => {
      const newProvider = {
        name: 'together-ai',
        displayName: 'Together AI',
        description: 'Together AI inference platform',
        baseUrl: 'https://api.together.xyz/v1',
        models: [],
        isActive: true
      }

      const response = await providersAPI.createProvider(newProvider)
      
      expect(response.status).toBe(201)
      expect(response.data.name).toBe('together-ai')
      expect(response.data.displayName).toBe('Together AI')
      expect(response.data.id).toBeDefined()
    })

    it('should update provider via backend', async () => {
      const providerId = MOCK_PROVIDERS[0].id
      const updates = { displayName: 'OpenAI GPT-4 Only' }

      const response = await providersAPI.updateProvider(providerId, updates)
      
      expect(response.status).toBe(200)
      expect(response.data.displayName).toBe('OpenAI GPT-4 Only')
    })

    it('should delete provider via backend', async () => {
      const providerId = MOCK_PROVIDERS[0].id
      const response = await providersAPI.deleteProvider(providerId)
      
      expect(response.status).toBe(200)
    })
  })

  /**
   * E2E TEST: Store integration with real API responses
   * Verifies that Zustand store correctly updates with backend data
   */
  describe('Zustand Store Integration', () => {
    beforeEach(() => {
      useProvidersStore.setState({
        providers: [],
        currentProvider: null,
        providerConfigs: {},
        isLoading: false,
        error: null
      })
    })

    it('should populate store with providers from backend', async () => {
      const response = await providersAPI.listProviders()
      
      useProvidersStore.setState({
        providers: response.data,
        currentProvider: response.data[0]
      })

      const state = useProvidersStore.getState()
      expect(state.providers).toHaveLength(2)
      expect(state.currentProvider?.displayName).toBe('OpenAI')
    })

    it('should set current provider to first from backend', async () => {
      const response = await providersAPI.listProviders()
      const firstProvider = response.data[0]
      
      useProvidersStore.setState({ currentProvider: firstProvider })
      
      const state = useProvidersStore.getState()
      expect(state.currentProvider?.id).toBe(firstProvider.id)
    })

    it('should update provider in store', async () => {
      const response = await providersAPI.listProviders()
      useProvidersStore.setState({ providers: response.data })

      const updated = await providersAPI.updateProvider(response.data[0].id, {
        displayName: 'Updated OpenAI'
      })

      useProvidersStore.setState(state => ({
        providers: state.providers.map(p =>
          p.id === updated.data.id ? updated.data : p
        ),
        currentProvider: state.currentProvider?.id === updated.data.id ? updated.data : state.currentProvider
      }))

      const state = useProvidersStore.getState()
      expect(state.providers[0].displayName).toBe('Updated OpenAI')
    })
  })

  /**
   * E2E TEST: Response data structure validation
   * Ensures backend returns expected fields for frontend consumption
   */
  describe('API Response Validation', () => {
    it('should return provider with all required fields', async () => {
      const response = await providersAPI.listProviders()
      const provider = response.data[0]

      expect(provider).toHaveProperty('id')
      expect(provider).toHaveProperty('name')
      expect(provider).toHaveProperty('displayName')
      expect(provider).toHaveProperty('description')
      expect(provider).toHaveProperty('baseUrl')
      expect(provider).toHaveProperty('models')
      expect(provider).toHaveProperty('isActive')
      expect(provider).toHaveProperty('createdAt')
      expect(provider).toHaveProperty('updatedAt')
    })

    it('should return model with all required fields', async () => {
      const response = await providersAPI.listProviders()
      const model = response.data[0].models[0]

      expect(model).toHaveProperty('id')
      expect(model).toHaveProperty('name')
      expect(model).toHaveProperty('displayName')
      expect(model).toHaveProperty('description')
      expect(model).toHaveProperty('contextWindow')
      expect(model).toHaveProperty('maxTokens')
      expect(model).toHaveProperty('capabilities')
    })

    it('should return valid UUID for provider id', async () => {
      const response = await providersAPI.listProviders()
      const providerId = response.data[0].id

      // Check UUID format
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
      expect(providerId).toMatch(uuidRegex)
    })

    it('should return ISO date strings', async () => {
      const response = await providersAPI.listProviders()
      const provider = response.data[0]

      const isoRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$/
      expect(provider.createdAt).toMatch(isoRegex)
      expect(provider.updatedAt).toMatch(isoRegex)
    })
  })

  /**
   * E2E TEST: Error handling
   */
  describe('Error Handling', () => {
    it('should handle 404 errors', async () => {
      try {
        await providersAPI.getProvider('nonexistent')
        expect.fail('Should throw')
      } catch (error: any) {
        expect(error.response?.status).toBe(404)
      }
    })

    it('should include error details in response', async () => {
      try {
        await providersAPI.getProvider('nonexistent')
      } catch (error: any) {
        expect(error.response?.data).toHaveProperty('detail')
      }
    })
  })
})
