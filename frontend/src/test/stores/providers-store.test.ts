import { describe, it, expect, beforeEach, vi } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useProvidersStore } from '../../stores/providersStore'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('Providers Store Tests', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks()

    // Reset localStorage mocks
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()

    // Reset store state by creating a fresh instance
    // This is a workaround since Zustand doesn't have a built-in reset
    const { result } = renderHook(() => useProvidersStore())
    act(() => {
      // Clear the persisted state
      result.current.setProviders([])
      result.current.setCurrentProvider(null)
      result.current.setProviderConfigs({})
      result.current.setError(null)
      result.current.setLoading(false)
    })
  })

  describe('Initial state', () => {
    it('should have correct initial state', () => {
      const { result } = renderHook(() => useProvidersStore())

      expect(result.current.providers).toEqual([])
      expect(result.current.currentProvider).toBeNull()
      expect(result.current.providerConfigs).toEqual({})
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })
  })

  describe('loadProviders', () => {
    it('should load default providers successfully', async () => {
      const { result } = renderHook(() => useProvidersStore())

      await act(async () => {
        await result.current.loadProviders()
      })

      expect(result.current.providers).toHaveLength(2)
      expect(result.current.providers[0].name).toBe('openai')
      expect(result.current.providers[1].name).toBe('anthropic')
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
      expect(result.current.currentProvider?.name).toBe('openai') // First active provider is set as current
    })

    it('should set loading state during load', async () => {
      const { result } = renderHook(() => useProvidersStore())

      act(() => {
        result.current.loadProviders()
      })

      expect(result.current.isLoading).toBe(true)

      await act(async () => {
        // Wait for the async operation to complete
        await new Promise(resolve => setTimeout(resolve, 0))
      })

      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('setCurrentProvider', () => {
    it('should set current provider', () => {
      const { result } = renderHook(() => useProvidersStore())

      const provider = {
        id: 'openai',
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
            capabilities: ['text', 'code', 'reasoning']
          }
        ],
        isActive: true,
        createdAt: '2025-01-10T00:00:00Z',
        updatedAt: '2025-01-10T00:00:00Z'
      }

      act(() => {
        result.current.setCurrentProvider(provider)
      })

      expect(result.current.currentProvider).toEqual(provider)
    })

    it('should allow setting current provider to null', () => {
      const { result } = renderHook(() => useProvidersStore())

      act(() => {
        result.current.setCurrentProvider(null)
      })

      expect(result.current.currentProvider).toBeNull()
    })
  })

  describe('createProvider', () => {
    it('should create provider successfully', async () => {
      const newProviderData = {
        name: 'custom-provider',
        displayName: 'Custom Provider',
        description: 'Custom AI provider',
        baseUrl: 'https://api.custom.com/v1',
        models: [
          {
            name: 'custom-model',
            displayName: 'Custom Model',
            description: 'A custom model',
            contextWindow: 4096,
            maxTokens: 2048,
            capabilities: ['text']
          }
        ]
      }

      const { result } = renderHook(() => useProvidersStore())

      let createdProvider: any = null
      await act(async () => {
        createdProvider = await result.current.createProvider(newProviderData)
      })

      expect(createdProvider).toBeDefined()
      expect(createdProvider.name).toBe('custom-provider')
      expect(createdProvider.displayName).toBe('Custom Provider')
      expect(createdProvider.isActive).toBe(true)
      expect(createdProvider.models).toHaveLength(1)
      expect(result.current.providers).toContain(createdProvider)
      expect(result.current.error).toBeNull()
    })
  })

  describe('updateProvider', () => {
    it('should update provider successfully', async () => {
      const { result } = renderHook(() => useProvidersStore())

      // First create a provider
      let createdProvider: any = null
      await act(async () => {
        createdProvider = await result.current.createProvider({
          name: 'test-provider',
          displayName: 'Test Provider',
          description: 'Test provider',
          models: []
        })
      })

      const updateData = {
        displayName: 'Updated Test Provider',
        description: 'Updated description'
      }

      let updatedProvider: any = null
      await act(async () => {
        updatedProvider = await result.current.updateProvider(createdProvider.id, updateData)
      })

      expect(updatedProvider.displayName).toBe('Updated Test Provider')
      expect(updatedProvider.description).toBe('Updated description')
      expect(result.current.providers.find(p => p.id === createdProvider.id)).toEqual(updatedProvider)
      expect(result.current.error).toBeNull()
    })

    it('should update current provider if it was modified', async () => {
      const { result } = renderHook(() => useProvidersStore())

      // First create and set as current provider
      let createdProvider: any = null
      await act(async () => {
        createdProvider = await result.current.createProvider({
          name: 'test-provider',
          displayName: 'Test Provider',
          description: 'Test provider',
          models: []
        })
        result.current.setCurrentProvider(createdProvider)
      })

      const updateData = {
        displayName: 'Updated Current Provider'
      }

      await act(async () => {
        await result.current.updateProvider(createdProvider.id, updateData)
      })

      expect(result.current.currentProvider?.displayName).toBe('Updated Current Provider')
    })
  })

  describe('deleteProvider', () => {
    it('should delete provider successfully', async () => {
      const { result } = renderHook(() => useProvidersStore())

      // First create a provider
      let createdProvider: any = null
      await act(async () => {
        createdProvider = await result.current.createProvider({
          name: 'test-provider',
          displayName: 'Test Provider',
          description: 'Test provider',
          models: []
        })
      })

      await act(async () => {
        await result.current.deleteProvider(createdProvider.id)
      })

      expect(result.current.providers).not.toContain(createdProvider)
      expect(result.current.error).toBeNull()
    })

    it('should clear current provider if it was deleted', async () => {
      const { result } = renderHook(() => useProvidersStore())

      // First create and set as current provider
      let createdProvider: any = null
      await act(async () => {
        createdProvider = await result.current.createProvider({
          name: 'test-provider',
          displayName: 'Test Provider',
          description: 'Test provider',
          models: []
        })
        result.current.setCurrentProvider(createdProvider)
      })

      await act(async () => {
        await result.current.deleteProvider(createdProvider.id)
      })

      expect(result.current.currentProvider).toBeNull()
    })

    it('should remove provider config when deleting provider', async () => {
      const { result } = renderHook(() => useProvidersStore())

      // First create a provider and config
      let createdProvider: any = null
      await act(async () => {
        createdProvider = await result.current.createProvider({
          name: 'test-provider',
          displayName: 'Test Provider',
          description: 'Test provider',
          models: []
        })
        await result.current.saveProviderConfig({
          providerId: createdProvider.id,
          apiKey: 'test-key'
        })
      })

      expect(result.current.getProviderConfig(createdProvider.id)).not.toBeNull()

      await act(async () => {
        await result.current.deleteProvider(createdProvider.id)
      })

      expect(result.current.getProviderConfig(createdProvider.id)).toBeNull()
    })
  })

  describe('getProvider', () => {
    it('should get provider by id', async () => {
      const { result } = renderHook(() => useProvidersStore())

      // First create a provider
      let createdProvider: any = null
      await act(async () => {
        createdProvider = await result.current.createProvider({
          name: 'test-provider',
          displayName: 'Test Provider',
          description: 'Test provider',
          models: []
        })
      })

      let retrievedProvider: any = null
      await act(async () => {
        retrievedProvider = await result.current.getProvider(createdProvider.id)
      })

      expect(retrievedProvider).toEqual(createdProvider)
    })

    it('should throw error for non-existent provider', async () => {
      const { result } = renderHook(() => useProvidersStore())

      await expect(async () => {
        await act(async () => {
          await result.current.getProvider('non-existent')
        })
      }).rejects.toThrow('Provider with id non-existent not found')
    })
  })

  describe('Provider Config Management', () => {
    it('should save and retrieve provider config', async () => {
      const { result } = renderHook(() => useProvidersStore())

      const config = {
        providerId: 'openai',
        apiKey: 'sk-test123456789',
        baseUrl: 'https://api.openai.com/v1',
        organizationId: 'org-test123',
        timeout: 30000,
        retryAttempts: 3
      }

      await act(async () => {
        await result.current.saveProviderConfig(config)
      })

      const retrievedConfig = result.current.getProviderConfig('openai')
      expect(retrievedConfig).toEqual(config)
    })

    it('should return null for non-existent config', () => {
      const { result } = renderHook(() => useProvidersStore())

      const config = result.current.getProviderConfig('non-existent')
      expect(config).toBeNull()
    })

    it('should delete provider config', async () => {
      const { result } = renderHook(() => useProvidersStore())

      const config = {
        providerId: 'openai',
        apiKey: 'sk-test123456789'
      }

      await act(async () => {
        await result.current.saveProviderConfig(config)
      })

      expect(result.current.getProviderConfig('openai')).not.toBeNull()

      await act(async () => {
        await result.current.deleteProviderConfig('openai')
      })

      expect(result.current.getProviderConfig('openai')).toBeNull()
    })
  })

  describe('validateProviderConfig', () => {
    it('should validate config with api key', async () => {
      const { result } = renderHook(() => useProvidersStore())

      const config = {
        providerId: 'openai',
        apiKey: 'sk-test123456789'
      }

      await act(async () => {
        await result.current.saveProviderConfig(config)
      })

      let isValid: boolean = false
      await act(async () => {
        isValid = await result.current.validateProviderConfig('openai')
      })

      expect(isValid).toBe(true)
    })

    it('should return false for config without api key', async () => {
      const { result } = renderHook(() => useProvidersStore())

      const config = {
        providerId: 'openai',
        apiKey: ''
      }

      await act(async () => {
        await result.current.saveProviderConfig(config)
      })

      let isValid: boolean = true
      await act(async () => {
        isValid = await result.current.validateProviderConfig('openai')
      })

      expect(isValid).toBe(false)
    })

    it('should return false for non-existent config', async () => {
      const { result } = renderHook(() => useProvidersStore())

      let isValid: boolean = true
      await act(async () => {
        isValid = await result.current.validateProviderConfig('non-existent')
      })

      expect(isValid).toBe(false)
    })
  })

  describe('Utility methods', () => {
    it('should get active providers', async () => {
      const { result } = renderHook(() => useProvidersStore())

      await act(async () => {
        await result.current.loadProviders()
      })

      const activeProviders = result.current.getActiveProviders()
      expect(activeProviders).toHaveLength(2)
      expect(activeProviders.every(p => p.isActive)).toBe(true)
    })

    it('should get provider by name', async () => {
      const { result } = renderHook(() => useProvidersStore())

      await act(async () => {
        await result.current.loadProviders()
      })

      const openaiProvider = result.current.getProviderByName('openai')
      expect(openaiProvider).not.toBeNull()
      expect(openaiProvider?.name).toBe('openai')

      const nonExistentProvider = result.current.getProviderByName('non-existent')
      expect(nonExistentProvider).toBeNull()
    })
  })

  describe('Error handling', () => {
    it('should handle errors in createProvider', async () => {
      const { result } = renderHook(() => useProvidersStore())

      // Mock a failure scenario by overriding the method temporarily
      const originalCreateProvider = result.current.createProvider
      result.current.createProvider = vi.fn().mockRejectedValue(new Error('Creation failed'))

      await expect(async () => {
        await act(async () => {
          await result.current.createProvider({
            name: 'test',
            displayName: 'Test',
            description: 'Test provider',
            models: []
          })
        })
      }).rejects.toThrow('Creation failed')

      expect(result.current.error).toBe('Creation failed')
      expect(result.current.isLoading).toBe(false)

      // Restore original method
      result.current.createProvider = originalCreateProvider
    })

    it('should clear error state', () => {
      const { result } = renderHook(() => useProvidersStore())

      act(() => {
        result.current.setError('Test error')
      })

      expect(result.current.error).toBe('Test error')

      act(() => {
        result.current.setError(null)
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe('Persistence', () => {
    it('should persist currentProvider and providerConfigs', async () => {
      const { result } = renderHook(() => useProvidersStore())

      const provider = {
        id: 'openai',
        name: 'openai',
        displayName: 'OpenAI',
        description: 'OpenAI GPT models',
        baseUrl: 'https://api.openai.com/v1',
        models: [],
        isActive: true,
        createdAt: '2025-01-10T00:00:00Z',
        updatedAt: '2025-01-10T00:00:00Z'
      }

      const config = {
        providerId: 'openai',
        apiKey: 'sk-test123'
      }

      await act(async () => {
        result.current.setCurrentProvider(provider)
        await result.current.saveProviderConfig(config)
      })

      // Create a new hook instance to test persistence
      const { result: newResult } = renderHook(() => useProvidersStore())

      expect(newResult.current.currentProvider).toEqual(provider)
      expect(newResult.current.getProviderConfig('openai')).toEqual(config)
    })
  })

  describe('Concurrent operations', () => {
    it('should handle multiple async operations', async () => {
      const { result } = renderHook(() => useProvidersStore())

      const operations = [
        result.current.createProvider({
          name: 'provider1',
          displayName: 'Provider 1',
          description: 'First provider',
          models: []
        }),
        result.current.createProvider({
          name: 'provider2',
          displayName: 'Provider 2',
          description: 'Second provider',
          models: []
        })
      ]

      const results = await Promise.all(operations)

      expect(results).toHaveLength(2)
      expect(result.current.providers).toHaveLength(2)
      expect(result.current.providers.map(p => p.name)).toEqual(
        expect.arrayContaining(['provider1', 'provider2'])
      )
    })
  })
})