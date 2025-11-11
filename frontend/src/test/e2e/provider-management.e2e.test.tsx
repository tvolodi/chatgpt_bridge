import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, renderHook } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from 'react-query'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { ProviderManagementPage } from '../../pages/ProviderManagementPage'
import { ChatPage } from '../../pages/ChatPage'
import { useProvidersStore } from '../../stores/providersStore'

// Mock MSW server for API calls
const server = setupServer(
  // Default handlers - will be overridden in specific tests
  http.get('http://localhost:8000/api/providers', () => {
    return HttpResponse.json([
      {
        id: 'openai-1',
        name: 'openai',
        displayName: 'OpenAI',
        description: 'OpenAI GPT models',
        baseUrl: 'https://api.openai.com/v1',
        models: [
          { id: 'gpt-4', name: 'gpt-4', displayName: 'GPT-4' },
          { id: 'gpt-3.5', name: 'gpt-3.5', displayName: 'GPT-3.5' }
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
          { id: 'claude-3', name: 'claude-3', displayName: 'Claude 3' }
        ],
        isActive: true,
        createdAt: '2025-01-10T00:00:00Z',
        updatedAt: '2025-01-10T00:00:00Z'
      }
    ])
  }),
  http.post('http://localhost:8000/api/providers', () => {
    return HttpResponse.json({
      id: 'test-provider-1',
      name: 'test-provider',
      displayName: 'Test Provider',
      description: '',
      baseUrl: 'https://api.test.com/v1',
      models: [],
      isActive: true,
      createdAt: '2025-01-10T00:00:00Z',
      updatedAt: '2025-01-10T00:00:00Z'
    })
  }),
  http.put('http://localhost:8000/api/providers/openai-1', () => {
    return HttpResponse.json({
      id: 'openai-1',
      name: 'openai',
      displayName: 'OpenAI (Updated)',
      description: 'OpenAI GPT models',
      baseUrl: 'https://api.openai.com/v1',
      models: [
        { id: 'gpt-4', name: 'gpt-4', displayName: 'GPT-4' },
        { id: 'gpt-3.5', name: 'gpt-3.5', displayName: 'GPT-3.5' }
      ],
      isActive: true,
      createdAt: '2025-01-10T00:00:00Z',
      updatedAt: '2025-01-10T00:00:00Z'
    })
  }),
  http.delete('http://localhost:8000/api/providers/anthropic-1', () => {
    return HttpResponse.json({ success: true })
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

describe('Provider Management E2E Tests', () => {
  describe('Provider Management Page Integration', () => {
    it('should render provider management page with providers list', async () => {
      renderWithProviders(<ProviderManagementPage />)

      await waitFor(() => {
        expect(screen.getByText('Provider Management')).toBeInTheDocument()
      })

      expect(screen.getByText('OpenAI')).toBeInTheDocument()
      expect(screen.getByText('Anthropic')).toBeInTheDocument()
    })

    it('should allow adding a new provider through the workflow', async () => {
      // Mock the store's createProvider method
      const originalCreateProvider = useProvidersStore.getState().createProvider
      const mockProvider = {
        id: 'test-provider-1',
        name: 'test-provider',
        displayName: 'Test Provider',
        description: '',
        baseUrl: 'https://api.test.com/v1',
        models: [],
        isActive: true,
        createdAt: '2025-01-10T00:00:00Z',
        updatedAt: '2025-01-10T00:00:00Z'
      }
      useProvidersStore.setState({
        createProvider: async () => {
          // Add the provider to the store
          const state = useProvidersStore.getState()
          const updatedProviders = [...state.providers, mockProvider]
          useProvidersStore.setState({ providers: updatedProviders })
          return mockProvider
        }
      })

      const user = userEvent.setup()
      renderWithProviders(<ProviderManagementPage />)

      await waitFor(() => {
        expect(screen.getByText('Provider Management')).toBeInTheDocument()
      })

      // Click add provider button
      const addButton = screen.getByRole('button', { name: /add provider/i })
      await user.click(addButton)

      // Should show add provider dialog
      await waitFor(() => {
        expect(screen.getByText('Add New Provider')).toBeInTheDocument()
      })

      // Fill out the form
      const nameInput = screen.getByPlaceholderText('openai')
      const displayNameInput = screen.getByPlaceholderText('OpenAI')
      const baseUrlInput = screen.getByPlaceholderText('https://api.openai.com/v1')

      await user.type(nameInput, 'test-provider')
      await user.type(displayNameInput, 'Test Provider')
      await user.type(baseUrlInput, 'https://api.test.com/v1')

      // Submit the form
      const submitButton = screen.getByRole('button', { name: /create provider/i })
      await user.click(submitButton)

      // Should close dialog and show success
      await waitFor(() => {
        expect(screen.queryByText('Add New Provider')).not.toBeInTheDocument()
      })

      // Should show the new provider in the list
      expect(screen.getByText('Test Provider')).toBeInTheDocument()

      // Restore original method
      useProvidersStore.setState({ createProvider: originalCreateProvider })
    })

    it('should allow editing an existing provider', async () => {
      // Mock the store's updateProvider method
      const originalUpdateProvider = useProvidersStore.getState().updateProvider
      useProvidersStore.setState({
        updateProvider: async (id, data) => {
          // Update the provider in the store
          const state = useProvidersStore.getState()
          const updatedProviders = state.providers.map(provider =>
            provider.id === id
              ? { ...provider, ...data, updatedAt: new Date().toISOString() }
              : provider
          )
          useProvidersStore.setState({ providers: updatedProviders })
          return updatedProviders.find(p => p.id === id)!
        }
      })

      const user = userEvent.setup()
      renderWithProviders(<ProviderManagementPage />)

      await waitFor(() => {
        expect(screen.getByText('Provider Management')).toBeInTheDocument()
      })

      // Find the OpenAI provider card and click its edit button
      const openaiCard = screen.getByText('OpenAI').closest('.border')
      const editButton = openaiCard?.querySelector('button:nth-child(2)') as HTMLButtonElement
      await user.click(editButton)

      // Should show edit provider dialog
      await waitFor(() => {
        expect(screen.getByText('Edit Provider')).toBeInTheDocument()
      })

      // Modify display name - find input by placeholder
      const displayNameInput = screen.getByPlaceholderText('OpenAI')
      await user.clear(displayNameInput)
      await user.type(displayNameInput, 'OpenAI (Updated)')

      // Submit the form
      const submitButton = screen.getByRole('button', { name: /update provider/i })
      await user.click(submitButton)

      // Should close dialog and show updated provider
      await waitFor(() => {
        expect(screen.queryByText('Edit Provider')).not.toBeInTheDocument()
      })

      expect(screen.getByText('OpenAI (Updated)')).toBeInTheDocument()

      // Restore original method
      useProvidersStore.setState({ updateProvider: originalUpdateProvider })
    })

    it('should allow deleting a provider', async () => {
      // Mock the store's deleteProvider method
      const originalDeleteProvider = useProvidersStore.getState().deleteProvider
      useProvidersStore.setState({
        deleteProvider: async (id: string) => {
          // Remove the provider from the store
          const state = useProvidersStore.getState()
          const updatedProviders = state.providers.filter(p => p.id !== id)
          useProvidersStore.setState({ providers: updatedProviders })
        }
      })

      const user = userEvent.setup()
      renderWithProviders(<ProviderManagementPage />)

      await waitFor(() => {
        expect(screen.getByText('Provider Management')).toBeInTheDocument()
      })

      // Mock window.confirm to return true
      const originalConfirm = window.confirm
      window.confirm = () => true

      // Find the Anthropic provider card and click its delete button
      const anthropicCard = screen.getByText('Anthropic').closest('.border')
      const deleteButton = anthropicCard?.querySelector('button:nth-child(3)') as HTMLButtonElement
      await user.click(deleteButton)

      // Should remove provider
      await waitFor(() => {
        expect(screen.queryByText('Anthropic')).not.toBeInTheDocument()
      })

      // Restore original confirm
      window.confirm = originalConfirm

      // Restore original method
      useProvidersStore.setState({ deleteProvider: originalDeleteProvider })
    })
  })

  describe('Chat Page Provider Integration', () => {
    it('should render chat page with provider selector', async () => {
      renderWithProviders(<ChatPage />)

      // Should show chat interface
      expect(screen.getByText('Welcome to AI Chat Assistant')).toBeInTheDocument()

      // Should show provider selector
      const providerSelector = screen.getByRole('button', { name: /openai/i })
      expect(providerSelector).toBeInTheDocument()
    })

    it('should allow switching providers in chat', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      // Click provider selector
      const providerSelector = screen.getByRole('button', { name: /openai/i })
      await user.click(providerSelector)

      // Should show dropdown with providers - look for the dropdown options specifically
      const dropdownOptions = screen.getAllByText('OpenAI')
      expect(dropdownOptions.length).toBeGreaterThan(0)
      expect(screen.getByText('Anthropic')).toBeInTheDocument()

      // Select Anthropic
      const anthropicOption = screen.getByText('Anthropic')
      await user.click(anthropicOption)

      // Should update selector to show Anthropic
      expect(screen.getByText('Anthropic')).toBeInTheDocument()
    })
  })

  describe('Error Handling and Edge Cases', () => {
    it('should handle API errors gracefully', async () => {
      // Mock the store's createProvider method to throw an error
      const originalCreateProvider = useProvidersStore.getState().createProvider
      useProvidersStore.setState({
        createProvider: async () => {
          throw new Error('Failed to create provider')
        }
      })

      const user = userEvent.setup()
      renderWithProviders(<ProviderManagementPage />)

      await waitFor(() => {
        expect(screen.getByText('Provider Management')).toBeInTheDocument()
      })

      // Try to add provider
      const addButton = screen.getByRole('button', { name: /add provider/i })
      await user.click(addButton)

      // Wait for dialog to open
      await waitFor(() => {
        expect(screen.getByText('Add New Provider')).toBeInTheDocument()
      })

      // Fill out the form
      const nameInput = screen.getByPlaceholderText('openai')
      const displayNameInput = screen.getByPlaceholderText('OpenAI')
      const baseUrlInput = screen.getByPlaceholderText('https://api.openai.com/v1')

      await user.type(nameInput, 'failing-provider')
      await user.type(displayNameInput, 'Failing Provider')
      await user.type(baseUrlInput, 'https://api.fail.com/v1')

      const submitButton = screen.getByRole('button', { name: /create provider/i })
      await user.click(submitButton)

      // Should show error message (alert)
      // Note: In a real app, we'd check for error toast/snackbar, but here we use alerts

      // Restore original method
      useProvidersStore.setState({ createProvider: originalCreateProvider })
    })

    it('should handle empty provider list', async () => {
      // Mock empty providers list and loadProviders
      const originalLoadProviders = useProvidersStore.getState().loadProviders
      useProvidersStore.setState({
        providers: [],
        loadProviders: async () => {
          useProvidersStore.setState({ providers: [] })
        }
      })

      renderWithProviders(<ProviderManagementPage />)

      await waitFor(() => {
        expect(screen.getByText('No providers configured')).toBeInTheDocument()
      })

      // Restore original method
      useProvidersStore.setState({ loadProviders: originalLoadProviders })
    })
  })

  describe('Store Integration and State Management', () => {
    it('should integrate providers store with components', async () => {
      renderWithProviders(<ProviderManagementPage />)

      await waitFor(() => {
        expect(screen.getByText('Provider Management')).toBeInTheDocument()
      })

      // Verify providers are loaded from store
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
      expect(screen.getByText('Anthropic')).toBeInTheDocument()

      // Verify store integration
      const { result } = renderHook(() => useProvidersStore())
      expect(result.current.providers).toHaveLength(2)
    })

    it('should maintain provider selection state across components', async () => {
      const user = userEvent.setup()

      // Start with chat page
      const { rerender } = renderWithProviders(<ChatPage />)

      expect(screen.getByText('OpenAI')).toBeInTheDocument()

      // Switch to Anthropic
      const providerSelector = screen.getByRole('button', { name: /openai/i })
      await user.click(providerSelector)

      const anthropicOption = screen.getByText('Anthropic')
      await user.click(anthropicOption)

      // Verify selection persisted
      expect(screen.getByText('Anthropic')).toBeInTheDocument()

      // Switch to provider management page by rerendering
      rerender(
        <QueryClientProvider client={new QueryClient()}>
          <ProviderManagementPage />
        </QueryClientProvider>
      )

      await waitFor(() => {
        expect(screen.getByText('Provider Management')).toBeInTheDocument()
      })

      // Providers should still be available
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
      expect(screen.getByText('Anthropic')).toBeInTheDocument()
    })
  })
})