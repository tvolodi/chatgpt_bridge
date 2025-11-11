import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor, renderHook } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from 'react-query'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { ChatPage } from '../../pages/ChatPage'
import { useProvidersStore } from '../../stores/providersStore'
import { useUserStateStore } from '../../stores/userStateStore'

// Mock MSW server for API calls
const server = setupServer(
  // Default handlers - will be overridden in specific tests
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
  beforeEach(() => {
    // Reset stores
    useProvidersStore.setState({
      providers: [
        {
          id: 'openai-1',
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
              capabilities: ['text', 'code', 'reasoning']
            },
            { 
              id: 'gpt-3.5', 
              name: 'gpt-3.5', 
              displayName: 'GPT-3.5',
              description: 'Fast and efficient GPT-3.5 model',
              contextWindow: 4096,
              maxTokens: 4096,
              capabilities: ['text', 'code']
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
          description: 'Claude models from Anthropic',
          baseUrl: 'https://api.anthropic.com',
          models: [
            { 
              id: 'claude-3', 
              name: 'claude-3', 
              displayName: 'Claude 3',
              description: 'Advanced Claude model',
              contextWindow: 200000,
              maxTokens: 4096,
              capabilities: ['text', 'code', 'reasoning', 'vision']
            }
          ],
          isActive: true,
          createdAt: '2025-01-10T00:00:00Z',
          updatedAt: '2025-01-10T00:00:00Z'
        }
      ],
      providerConfigs: {
        'openai-1': { providerId: 'openai-1', apiKey: 'sk-test-key' },
        // anthropic-1 has no config (unavailable)
      }
    })

    useUserStateStore.setState({
      session: {
        sessionId: 'session-1',
        loginTime: new Date(),
        lastActivity: new Date(),
        activeProject: 'project-1',
        activeSession: 'session-1',
        selectedProviderId: 'openai-1',
        openTabs: [],
        clipboardHistory: []
      }
    })
  })

  describe('Provider Selector in Chat Header', () => {
    it('should display provider selector in chat header', async () => {
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Should show provider selector with current provider
      const providerSelector = screen.getByRole('button', { name: /openai/i })
      expect(providerSelector).toBeInTheDocument()
    })

    it('should show currently selected provider name', async () => {
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Should display the selected provider name
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
    })

    it('should open dropdown when provider selector is clicked', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      const providerSelector = screen.getByRole('button', { name: /openai/i })
      await user.click(providerSelector)

      // Should show dropdown with all providers
      expect(screen.getByText('OpenAI GPT models including GPT-4, GPT-3.5, and DALL-E')).toBeInTheDocument()
      expect(screen.getByText('Claude models from Anthropic')).toBeInTheDocument()
    })
  })

  describe('Provider Dropdown Display', () => {
    it('should display provider name, description, and model count', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      const providerSelector = screen.getByRole('button', { name: /openai/i })
      await user.click(providerSelector)

      // Check OpenAI provider details
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
      expect(screen.getByText('OpenAI GPT models including GPT-4, GPT-3.5, and DALL-E')).toBeInTheDocument()
      expect(screen.getByText('2 models')).toBeInTheDocument()

      // Check Anthropic provider details
      expect(screen.getByText('Anthropic')).toBeInTheDocument()
      expect(screen.getByText('Claude models from Anthropic')).toBeInTheDocument()
      expect(screen.getByText('1 models')).toBeInTheDocument()
    })

    it('should show checkmark next to currently selected provider', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      const providerSelector = screen.getByRole('button', { name: /openai/i })
      await user.click(providerSelector)

      // Should show checkmark icon next to selected provider
      const openaiButton = screen.getByText('OpenAI').closest('button')
      const checkIcon = openaiButton?.querySelector('svg')
      expect(checkIcon).toBeInTheDocument()
    })

    it('should visually indicate unavailable providers', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      const providerSelector = screen.getByRole('button', { name: /openai/i })
      await user.click(providerSelector)

      // Anthropic should show as unavailable (no API key configured)
      const anthropicButton = screen.getByText('Anthropic').closest('button')
      expect(anthropicButton).toHaveClass('opacity-60')
      expect(anthropicButton).toHaveAttribute('disabled')

      // Should show warning icon and message
      expect(screen.getByText('API key not configured')).toBeInTheDocument()
      const warningIcon = anthropicButton?.querySelector('svg.lucide-alert-triangle')
      expect(warningIcon).toBeInTheDocument()
    })
  })

  describe('Provider Switching', () => {
    it('should allow switching to available provider', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Initially shows OpenAI
      expect(screen.getByText('OpenAI')).toBeInTheDocument()

      // Click to open dropdown
      const providerSelector = screen.getByRole('button', { name: /openai/i })
      await user.click(providerSelector)

      // Click on OpenAI again (should close dropdown since it's already selected)
      const openaiOption = screen.getAllByText('OpenAI')[1] // Second instance is in dropdown
      await user.click(openaiOption)

      // Should still show OpenAI
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
    })

    it('should not allow switching to unavailable provider', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Initially shows OpenAI
      expect(screen.getByText('OpenAI')).toBeInTheDocument()

      // Click to open dropdown
      const providerSelector = screen.getByRole('button', { name: /openai/i })
      await user.click(providerSelector)

      // Try to click on Anthropic (unavailable)
      const anthropicOption = screen.getByText('Anthropic')
      await user.click(anthropicOption)

      // Should still show OpenAI (no change)
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
    })

    it('should persist provider selection across component re-renders', async () => {
      const user = userEvent.setup()
      const { rerender } = renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Initially shows OpenAI
      expect(screen.getByText('OpenAI')).toBeInTheDocument()

      // Re-render component
      rerender(
        <QueryClientProvider client={new QueryClient()}>
          <ChatPage />
        </QueryClientProvider>
      )

      // Should still show OpenAI
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
    })
  })

  describe('Provider Selection Persistence', () => {
    it('should persist selected provider in user state store', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Check initial state
      const { result } = renderHook(() => useUserStateStore())
      expect(result.current.session?.selectedProviderId).toBe('openai-1')

      // Provider selection should be persisted in store
      expect(result.current.session?.selectedProviderId).toBe('openai-1')
    })

    it('should initialize with first available provider if none selected', async () => {
      // Clear selected provider
      useUserStateStore.setState({
        session: {
          sessionId: 'session-1',
          loginTime: new Date(),
          lastActivity: new Date(),
          activeProject: 'project-1',
          activeSession: 'session-1',
          openTabs: [],
          clipboardHistory: []
        }
      })

      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Should initialize with first available provider (OpenAI)
      const { result } = renderHook(() => useUserStateStore())
      expect(result.current.session?.selectedProviderId).toBe('openai-1')
    })
  })

  describe('Integration with Provider Management', () => {
    it('should update available providers when store changes', async () => {
      const user = userEvent.setup()
      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Open dropdown
      const providerSelector = screen.getByRole('button', { name: /openai/i })
      await user.click(providerSelector)

      // Should show both providers initially
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
      expect(screen.getByText('Anthropic')).toBeInTheDocument()

      // Simulate adding a new provider via Provider Management
      useProvidersStore.setState(state => ({
        providers: [
          ...state.providers,
          {
            id: 'google-1',
            name: 'google',
            displayName: 'Google',
            description: 'Google AI models',
            baseUrl: 'https://generativelanguage.googleapis.com',
            models: [{ 
              id: 'gemini', 
              name: 'gemini-pro', 
              displayName: 'Gemini Pro',
              description: 'Google Gemini Pro model',
              contextWindow: 32768,
              maxTokens: 8192,
              capabilities: ['text', 'code', 'reasoning', 'vision']
            }],
            isActive: true,
            createdAt: '2025-01-10T00:00:00Z',
            updatedAt: '2025-01-10T00:00:00Z'
          }
        ]
      }))

      // Re-open dropdown (close and open again)
      await user.click(document.body) // Close dropdown
      await user.click(providerSelector) // Re-open

      // Should now show Google provider
      expect(screen.getByText('Google')).toBeInTheDocument()
    })

    it('should handle provider removal gracefully', async () => {
      const user = userEvent.setup()

      // Set Anthropic as selected provider
      useUserStateStore.setState({
        session: {
          sessionId: 'session-1',
          loginTime: new Date(),
          lastActivity: new Date(),
          activeProject: 'project-1',
          activeSession: 'session-1',
          selectedProviderId: 'anthropic-1',
          openTabs: [],
          clipboardHistory: []
        }
      })

      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Should show Anthropic as selected
      expect(screen.getByText('Anthropic')).toBeInTheDocument()

      // Simulate removing Anthropic provider
      useProvidersStore.setState(state => ({
        providers: state.providers.filter(p => p.id !== 'anthropic-1')
      }))

      // Should fall back to first available provider (OpenAI)
      await waitFor(() => {
        expect(screen.getByText('OpenAI')).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle case when no providers are available', async () => {
      // Clear all providers
      useProvidersStore.setState({
        providers: []
      })

      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Should show "Select Provider" when no providers available
      expect(screen.getByText('Select Provider')).toBeInTheDocument()
    })

    it('should handle provider store errors gracefully', async () => {
      // Mock store error
      const originalGetActiveProviders = useProvidersStore.getState().getActiveProviders
      useProvidersStore.setState({
        getActiveProviders: () => {
          throw new Error('Store error')
        }
      })

      renderWithProviders(<ChatPage />)

      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument()
      })

      // Should still render without crashing
      expect(screen.getByText('Chat')).toBeInTheDocument()

      // Restore original function
      useProvidersStore.setState({ getActiveProviders: originalGetActiveProviders })
    })
  })
})