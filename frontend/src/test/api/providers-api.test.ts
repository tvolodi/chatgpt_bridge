import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { providersAPI } from '../../services/api'

// Mock server setup
const server = setupServer(
  // Mock providers endpoints
  http.get('http://localhost:8000/api/ai-providers', () => {
    return HttpResponse.json([
      {
        id: 'openai-1',
        name: 'openai',
        displayName: 'OpenAI',
        description: 'OpenAI GPT models',
        baseUrl: 'https://api.openai.com/v1',
        models: [
          {
            id: 'gpt-4',
            name: 'gpt-4',
            displayName: 'GPT-4',
            description: 'Most capable GPT-4 model',
            contextWindow: 8192,
            maxTokens: 4096,
            capabilities: ['chat', 'completion']
          },
          {
            id: 'gpt-3.5-turbo',
            name: 'gpt-3.5-turbo',
            displayName: 'GPT-3.5 Turbo',
            description: 'Fast and efficient GPT-3.5 model',
            contextWindow: 4096,
            maxTokens: 2048,
            capabilities: ['chat', 'completion']
          }
        ],
        isActive: true,
        createdAt: '2025-01-10T00:00:00Z',
        updatedAt: '2025-01-10T00:00:00Z'
      },
      {
        id: 'anthropic-1',
        name: 'anthropic',
        displayName: 'Anthropic',
        description: 'Anthropic Claude models',
        baseUrl: 'https://api.anthropic.com',
        models: [
          {
            id: 'claude-3-opus',
            name: 'claude-3-opus',
            displayName: 'Claude 3 Opus',
            description: 'Most capable Claude model',
            contextWindow: 200000,
            maxTokens: 4096,
            capabilities: ['chat', 'completion']
          }
        ],
        isActive: true,
        createdAt: '2025-01-10T00:00:00Z',
        updatedAt: '2025-01-10T00:00:00Z'
      }
    ])
  }),

  http.get('http://localhost:8000/api/ai-providers/openai-1', () => {
    return HttpResponse.json({
      id: 'openai-1',
      name: 'openai',
      displayName: 'OpenAI',
      description: 'OpenAI GPT models',
      baseUrl: 'https://api.openai.com/v1',
      models: [
        {
          id: 'gpt-4',
          name: 'gpt-4',
          displayName: 'GPT-4',
          description: 'Most capable GPT-4 model',
          contextWindow: 8192,
          maxTokens: 4096,
          capabilities: ['chat', 'completion']
        }
      ],
      isActive: true,
      createdAt: '2025-01-10T00:00:00Z',
      updatedAt: '2025-01-10T00:00:00Z'
    })
  }),

  http.post('http://localhost:8000/api/ai-providers', () => {
    return HttpResponse.json({
      id: 'new-provider-1',
      name: 'custom-provider',
      displayName: 'Custom Provider',
      description: 'Custom AI provider',
      baseUrl: 'https://api.custom.com/v1',
      models: [],
      isActive: true,
      createdAt: '2025-01-10T00:00:00Z',
      updatedAt: '2025-01-10T00:00:00Z'
    })
  }),

  http.put('http://localhost:8000/api/ai-providers/openai-1', () => {
    return HttpResponse.json({
      id: 'openai-1',
      name: 'openai',
      displayName: 'Updated OpenAI',
      description: 'Updated OpenAI GPT models',
      baseUrl: 'https://api.openai.com/v1',
      models: [],
      isActive: true,
      createdAt: '2025-01-10T00:00:00Z',
      updatedAt: '2025-01-11T00:00:00Z'
    })
  }),

  http.delete('http://localhost:8000/api/ai-providers/openai-1', () => {
    return HttpResponse.json({ message: 'Provider deleted successfully' })
  }),

  http.get('http://localhost:8000/api/settings/api-providers/openai-1', () => {
    return HttpResponse.json({
      providerId: 'openai-1',
      apiKey: 'sk-test123456789',
      baseUrl: 'https://api.openai.com/v1',
      organizationId: 'org-test123',
      projectId: 'proj_test123',
      timeout: 30000,
      retryAttempts: 3
    })
  }),

  http.put('http://localhost:8000/api/settings/api-providers/openai-1', () => {
    return HttpResponse.json({ message: 'Provider config updated successfully' })
  }),

  http.delete('http://localhost:8000/api/settings/api-providers/openai-1', () => {
    return HttpResponse.json({ message: 'Provider config deleted successfully' })
  }),

  // Validate provider config - NOTE: Backend doesn't have this endpoint, removing
  // http.post('http://localhost:8000/api/providers/openai-1/validate', () => {
  //   return HttpResponse.json({ valid: true, message: 'Configuration is valid' })
  // }),

  // Get available models for provider - NOTE: Backend serves this as global endpoint
  http.get('http://localhost:8000/api/ai-providers/models/available', () => {
    return HttpResponse.json([
      {
        id: 'gpt-4',
        name: 'gpt-4',
        displayName: 'GPT-4',
        description: 'Most capable GPT-4 model',
        contextWindow: 8192,
        maxTokens: 4096,
        capabilities: ['chat', 'completion']
      },
      {
        id: 'gpt-4-turbo',
        name: 'gpt-4-turbo',
        displayName: 'GPT-4 Turbo',
        description: 'Latest GPT-4 Turbo model',
        contextWindow: 128000,
        maxTokens: 4096,
        capabilities: ['chat', 'completion']
      }
    ])
  })
)

// Start server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))

// Reset handlers after each test
afterEach(() => server.resetHandlers())

// Close server after all tests
afterAll(() => server.close())

describe('Providers API Integration Tests', () => {
  describe('listProviders', () => {
    it('should fetch all providers successfully', async () => {
      const response = await providersAPI.listProviders()

      expect(response.data).toBeDefined()
      expect(Array.isArray(response.data)).toBe(true)
      expect(response.data).toHaveLength(2)

      const openaiProvider = response.data.find((p: any) => p.name === 'openai')
      expect(openaiProvider).toBeDefined()
      expect(openaiProvider.displayName).toBe('OpenAI')
      expect(openaiProvider.models).toHaveLength(2)
      expect(openaiProvider.isActive).toBe(true)
    })

    it('should handle API errors gracefully', async () => {
      server.use(
        http.get('http://localhost:8000/api/ai-providers', () => {
          return HttpResponse.json({ error: 'Internal server error' }, { status: 500 })
        })
      )

      await expect(providersAPI.listProviders()).rejects.toThrow()
    })
  })

  describe('getProvider', () => {
    it('should fetch single provider successfully', async () => {
      const response = await providersAPI.getProvider('openai-1')

      expect(response.data).toBeDefined()
      expect(response.data.id).toBe('openai-1')
      expect(response.data.name).toBe('openai')
      expect(response.data.displayName).toBe('OpenAI')
      expect(response.data.models).toHaveLength(1)
      expect(response.data.models[0].name).toBe('gpt-4')
    })

    it('should handle provider not found', async () => {
      server.use(
        http.get('http://localhost:8000/api/ai-providers/nonexistent', () => {
          return HttpResponse.json({ error: 'Provider not found' }, { status: 404 })
        })
      )

      await expect(providersAPI.getProvider('nonexistent')).rejects.toThrow()
    })
  })

  describe('createProvider', () => {
    it('should create provider successfully', async () => {
      const providerData = {
        name: 'custom-provider',
        displayName: 'Custom Provider',
        description: 'Custom AI provider',
        baseUrl: 'https://api.custom.com/v1',
        models: []
      }

      const response = await providersAPI.createProvider(providerData)

      expect(response.data).toBeDefined()
      expect(response.data.id).toBe('new-provider-1')
      expect(response.data.name).toBe('custom-provider')
      expect(response.data.displayName).toBe('Custom Provider')
      expect(response.data.isActive).toBe(true)
    })

    it('should handle validation errors', async () => {
      server.use(
        http.post('http://localhost:8000/api/ai-providers', () => {
          return HttpResponse.json({ error: 'Invalid provider data' }, { status: 400 })
        })
      )

      await expect(providersAPI.createProvider({})).rejects.toThrow()
    })
  })

  describe('updateProvider', () => {
    it('should update provider successfully', async () => {
      const updateData = {
        displayName: 'Updated OpenAI',
        description: 'Updated OpenAI GPT models'
      }

      const response = await providersAPI.updateProvider('openai-1', updateData)

      expect(response.data).toBeDefined()
      expect(response.data.id).toBe('openai-1')
      expect(response.data.displayName).toBe('Updated OpenAI')
      expect(response.data.description).toBe('Updated OpenAI GPT models')
      expect(response.data.updatedAt).toBe('2025-01-11T00:00:00Z')
    })

    it('should handle update validation errors', async () => {
      server.use(
        http.put('http://localhost:8000/api/ai-providers/openai-1', () => {
          return HttpResponse.json({ error: 'Invalid update data' }, { status: 400 })
        })
      )

      await expect(providersAPI.updateProvider('openai-1', { invalidField: 'value' })).rejects.toThrow()
    })
  })

  describe('deleteProvider', () => {
    it('should delete provider successfully', async () => {
      const response = await providersAPI.deleteProvider('openai-1')

      expect(response.data).toBeDefined()
      expect(response.data.message).toBe('Provider deleted successfully')
    })

    it('should handle provider not found during deletion', async () => {
      server.use(
        http.delete('http://localhost:8000/api/ai-providers/nonexistent', () => {
          return HttpResponse.json({ error: 'Provider not found' }, { status: 404 })
        })
      )

      await expect(providersAPI.deleteProvider('nonexistent')).rejects.toThrow()
    })
  })

  describe('getProviderConfig', () => {
    it('should fetch provider config successfully', async () => {
      const response = await providersAPI.getProviderConfig('openai-1')

      expect(response.data).toBeDefined()
      expect(response.data.providerId).toBe('openai-1')
      expect(response.data.apiKey).toBe('sk-test123456789')
      expect(response.data.organizationId).toBe('org-test123')
      expect(response.data.timeout).toBe(30000)
      expect(response.data.retryAttempts).toBe(3)
    })

    it('should handle config not found', async () => {
      server.use(
        http.get('http://localhost:8000/api/settings/api-providers/no-config', () => {
          return HttpResponse.json({ error: 'Config not found' }, { status: 404 })
        })
      )

      await expect(providersAPI.getProviderConfig('no-config')).rejects.toThrow()
    })
  })

  describe('updateProviderConfig', () => {
    it('should update provider config successfully', async () => {
      const configData = {
        providerId: 'openai-1',
        apiKey: 'sk-new123456789',
        timeout: 45000,
        retryAttempts: 5
      }

      const response = await providersAPI.updateProviderConfig('openai-1', configData)

      expect(response.data).toBeDefined()
      expect(response.data.message).toBe('Provider config updated successfully')
    })

    it('should handle config validation errors', async () => {
      server.use(
        http.put('http://localhost:8000/api/settings/api-providers/openai-1', () => {
          return HttpResponse.json({ error: 'Invalid config data' }, { status: 400 })
        })
      )

      await expect(providersAPI.updateProviderConfig('openai-1', { invalidField: 'value' })).rejects.toThrow()
    })
  })

  describe('deleteProviderConfig', () => {
    it('should delete provider config successfully', async () => {
      const response = await providersAPI.deleteProviderConfig('openai-1')

      expect(response.data).toBeDefined()
      expect(response.data.message).toBe('Provider config deleted successfully')
    })

    it('should handle config not found during deletion', async () => {
      server.use(
        http.delete('http://localhost:8000/api/settings/api-providers/no-config', () => {
          return HttpResponse.json({ error: 'Config not found' }, { status: 404 })
        })
      )

      await expect(providersAPI.deleteProviderConfig('no-config')).rejects.toThrow()
    })
  })



  describe('getProviderModels', () => {
    it('should fetch provider models successfully', async () => {
      const response = await providersAPI.getProviderModels()

      expect(response.data).toBeDefined()
      expect(Array.isArray(response.data)).toBe(true)
      expect(response.data).toHaveLength(2)

      const gpt4Model = response.data.find((m: any) => m.name === 'gpt-4')
      expect(gpt4Model).toBeDefined()
      expect(gpt4Model.displayName).toBe('GPT-4')
      expect(gpt4Model.contextWindow).toBe(8192)
      expect(gpt4Model.capabilities).toContain('chat')
    })

    it('should handle provider not found when fetching models', async () => {
      server.use(
        http.get('http://localhost:8000/api/ai-providers/models/available', () => {
          return HttpResponse.json({ error: 'Provider not found' }, { status: 404 })
        })
      )

      await expect(providersAPI.getProviderModels()).rejects.toThrow()
    })
  })

  describe('Cross-functional scenarios', () => {
    it('should handle complete provider lifecycle', async () => {
      // 1. List providers
      const listResponse = await providersAPI.listProviders()
      expect(listResponse.data).toHaveLength(2)

      // 2. Get specific provider
      const providerResponse = await providersAPI.getProvider('openai-1')
      expect(providerResponse.data.name).toBe('openai')

      // 3. Get provider config
      const configResponse = await providersAPI.getProviderConfig('openai-1')
      expect(configResponse.data.apiKey).toBe('sk-test123456789')

      // 4. Validate config - NOTE: Backend doesn't have this endpoint, skipping
      // const validateResponse = await providersAPI.validateProviderConfig('openai-1')
      // expect(validateResponse.data.valid).toBe(true)

      // 5. Get provider models
      const modelsResponse = await providersAPI.getProviderModels()
      expect(modelsResponse.data).toHaveLength(2)

      // 6. Update provider
      const updateResponse = await providersAPI.updateProvider('openai-1', {
        displayName: 'Updated OpenAI'
      })
      expect(updateResponse.data.displayName).toBe('Updated OpenAI')

      // 7. Update config
      await providersAPI.updateProviderConfig('openai-1', {
        providerId: 'openai-1',
        apiKey: 'sk-updated123456789'
      })

      // 8. Delete config (optional cleanup)
      await providersAPI.deleteProviderConfig('openai-1')

      // 9. Delete provider
      await providersAPI.deleteProvider('openai-1')
    })

    it('should handle network errors gracefully', async () => {
      server.use(
        http.get('http://localhost:8000/api/ai-providers', () => {
          return HttpResponse.error()
        })
      )

      await expect(providersAPI.listProviders()).rejects.toThrow()
    })

    it('should handle timeout scenarios', async () => {
      server.use(
        http.post('http://localhost:8000/api/ai-providers', async () => {
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json({ id: 'timeout-test' })
        })
      )

      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), 50)
      )

      await expect(Promise.race([
        providersAPI.createProvider({
          name: 'timeout-test',
          displayName: 'Timeout Test',
          description: 'Test timeout handling',
          models: []
        }),
        timeoutPromise
      ])).rejects.toThrow('Timeout')
    })

    it('should handle concurrent operations', async () => {
      const operations = [
        providersAPI.getProvider('openai-1'),
        providersAPI.getProviderConfig('openai-1'),
        providersAPI.getProviderModels()
      ]

      const results = await Promise.all(operations)

      expect(results).toHaveLength(3)
      expect(results[0].data.name).toBe('openai')
      expect(results[1].data.apiKey).toBe('sk-test123456789')
      expect(results[2].data).toHaveLength(2)
    })
  })
})