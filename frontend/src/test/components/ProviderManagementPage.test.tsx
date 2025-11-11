import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { ProviderManagementPage } from '../../pages/ProviderManagementPage'
import { useProvidersStore } from '../../stores/providersStore'

// Mock the providers store
vi.mock('../../stores/providersStore', () => ({
  useProvidersStore: vi.fn()
}))

// Mock child components
vi.mock('../../components/ProviderForm', () => ({
  ProviderForm: ({ onSubmit, onCancel }: any) => (
    <div data-testid="provider-form">
      <button onClick={() => onSubmit({
        name: 'test-provider',
        displayName: 'Test Provider',
        description: 'Test description',
        models: []
      })}>
        Submit Form
      </button>
      <button onClick={onCancel}>Cancel Form</button>
    </div>
  )
}))

vi.mock('../../components/ProviderList', () => ({
  ProviderList: ({ providers, onEdit, onDelete, onConfigure }: any) => (
    <div data-testid="provider-list">
      {providers.map((provider: any) => (
        <div key={provider.id} data-testid={`provider-${provider.id}`}>
          <span>{provider.displayName}</span>
          <button onClick={() => onEdit(provider)}>Edit</button>
          <button onClick={() => onDelete(provider.id)}>Delete</button>
          <button onClick={() => onConfigure(provider.id)}>Configure</button>
        </div>
      ))}
    </div>
  )
}))

vi.mock('../../components/ProviderConfigDialog', () => ({
  ProviderConfigDialog: ({ open, onClose, providerId }: any) =>
    open ? (
      <div data-testid="provider-config-dialog">
        <span>Config for {providerId}</span>
        <button onClick={onClose}>Close Config</button>
      </div>
    ) : null
}))

const mockStore = {
  providers: [
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
          capabilities: ['text', 'code', 'reasoning']
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
      models: [],
      isActive: true,
      createdAt: '2025-01-10T00:00:00Z',
      updatedAt: '2025-01-10T00:00:00Z'
    }
  ],
  currentProvider: null,
  providerConfigs: {},
  isLoading: false,
  error: null,
  loadProviders: vi.fn(),
  createProvider: vi.fn(),
  updateProvider: vi.fn(),
  deleteProvider: vi.fn(),
  getProvider: vi.fn(),
  saveProviderConfig: vi.fn(),
  getProviderConfig: vi.fn(),
  deleteProviderConfig: vi.fn(),
  validateProviderConfig: vi.fn(),
  getActiveProviders: vi.fn(),
  getProviderByName: vi.fn(),
  setProviders: vi.fn(),
  setCurrentProvider: vi.fn(),
  setProviderConfigs: vi.fn(),
  setLoading: vi.fn(),
  setError: vi.fn()
}

const renderProviderManagementPage = () => {
  return render(
    <MemoryRouter>
      <ProviderManagementPage />
    </MemoryRouter>
  )
}

describe('ProviderManagementPage Component Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useProvidersStore).mockReturnValue(mockStore)
  })

  describe('Initial render', () => {
    it('should render the page title', () => {
      renderProviderManagementPage()

      expect(screen.getByText('Provider Management')).toBeInTheDocument()
    })

    it('should render the add provider button', () => {
      renderProviderManagementPage()

      expect(screen.getByText('Add Provider')).toBeInTheDocument()
    })

    it('should render the provider list', () => {
      renderProviderManagementPage()

      expect(screen.getByTestId('provider-list')).toBeInTheDocument()
      expect(screen.getByTestId('provider-openai-1')).toBeInTheDocument()
      expect(screen.getByTestId('provider-anthropic-1')).toBeInTheDocument()
    })

    it('should load providers on mount', () => {
      renderProviderManagementPage()

      expect(mockStore.loadProviders).toHaveBeenCalledTimes(1)
    })
  })

  describe('Add Provider functionality', () => {
    it('should show provider form when add button is clicked', async () => {
      const user = userEvent.setup()
      renderProviderManagementPage()

      const addButton = screen.getByText('Add Provider')
      await user.click(addButton)

      expect(screen.getByTestId('provider-form')).toBeInTheDocument()
    })

    it('should hide form when cancel is clicked', async () => {
      const user = userEvent.setup()
      renderProviderManagementPage()

      // Show form
      const addButton = screen.getByText('Add Provider')
      await user.click(addButton)

      // Cancel form
      const cancelButton = screen.getByText('Cancel Form')
      await user.click(cancelButton)

      expect(screen.queryByTestId('provider-form')).not.toBeInTheDocument()
    })

    it('should create provider when form is submitted', async () => {
      const user = userEvent.setup()
      renderProviderManagementPage()

      // Show form
      const addButton = screen.getByText('Add Provider')
      await user.click(addButton)

      // Submit form
      const submitButton = screen.getByText('Submit Form')
      await user.click(submitButton)

      expect(mockStore.createProvider).toHaveBeenCalledWith({
        name: 'test-provider',
        displayName: 'Test Provider',
        description: 'Test description',
        models: []
      })
    })

    it('should hide form after successful creation', async () => {
      const user = userEvent.setup()
      mockStore.createProvider.mockResolvedValue({
        id: 'new-provider',
        name: 'test-provider',
        displayName: 'Test Provider',
        description: 'Test description',
        models: [],
        isActive: true,
        createdAt: '2025-01-10T00:00:00Z',
        updatedAt: '2025-01-10T00:00:00Z'
      })

      renderProviderManagementPage()

      // Show and submit form
      const addButton = screen.getByText('Add Provider')
      await user.click(addButton)

      const submitButton = screen.getByText('Submit Form')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.queryByTestId('provider-form')).not.toBeInTheDocument()
      })
    })
  })

  describe('Edit Provider functionality', () => {
    it('should show provider form in edit mode when edit button is clicked', async () => {
      const user = userEvent.setup()
      renderProviderManagementPage()

      const editButton = screen.getAllByText('Edit')[0]
      await user.click(editButton)

      expect(screen.getByTestId('provider-form')).toBeInTheDocument()
    })

    it('should update provider when form is submitted in edit mode', async () => {
      const user = userEvent.setup()
      renderProviderManagementPage()

      // Click edit on first provider
      const editButtons = screen.getAllByText('Edit')
      await user.click(editButtons[0])

      // Submit form
      const submitButton = screen.getByText('Submit Form')
      await user.click(submitButton)

      expect(mockStore.updateProvider).toHaveBeenCalledWith('openai-1', {
        name: 'test-provider',
        displayName: 'Test Provider',
        description: 'Test description',
        models: []
      })
    })
  })

  describe('Delete Provider functionality', () => {
    it('should show confirmation dialog when delete button is clicked', async () => {
      const user = userEvent.setup()
      renderProviderManagementPage()

      const deleteButton = screen.getAllByText('Delete')[0]
      await user.click(deleteButton)

      // Check if browser confirm was called (mocked globally)
      expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this provider?')
    })

    it('should delete provider when confirmed', async () => {
      const user = userEvent.setup()
      // Mock window.confirm to return true
      vi.spyOn(window, 'confirm').mockReturnValue(true)

      renderProviderManagementPage()

      const deleteButton = screen.getAllByText('Delete')[0]
      await user.click(deleteButton)

      expect(mockStore.deleteProvider).toHaveBeenCalledWith('openai-1')
    })

    it('should not delete provider when cancelled', async () => {
      const user = userEvent.setup()
      // Mock window.confirm to return false
      vi.spyOn(window, 'confirm').mockReturnValue(false)

      renderProviderManagementPage()

      const deleteButton = screen.getAllByText('Delete')[0]
      await user.click(deleteButton)

      expect(mockStore.deleteProvider).not.toHaveBeenCalled()
    })
  })

  describe('Configure Provider functionality', () => {
    it('should show config dialog when configure button is clicked', async () => {
      const user = userEvent.setup()
      renderProviderManagementPage()

      const configureButton = screen.getAllByText('Configure')[0]
      await user.click(configureButton)

      expect(screen.getByTestId('provider-config-dialog')).toBeInTheDocument()
      expect(screen.getByText('Config for openai-1')).toBeInTheDocument()
    })

    it('should hide config dialog when close button is clicked', async () => {
      const user = userEvent.setup()
      renderProviderManagementPage()

      // Open config dialog
      const configureButton = screen.getAllByText('Configure')[0]
      await user.click(configureButton)

      // Close dialog
      const closeButton = screen.getByText('Close Config')
      await user.click(closeButton)

      expect(screen.queryByTestId('provider-config-dialog')).not.toBeInTheDocument()
    })
  })

  describe('Loading states', () => {
    it('should show loading indicator when loading', () => {
      const loadingStore = { ...mockStore, isLoading: true }
      vi.mocked(useProvidersStore).mockReturnValue(loadingStore)

      renderProviderManagementPage()

      expect(screen.getByText('Loading providers...')).toBeInTheDocument()
    })

    it('should disable add button when loading', () => {
      const loadingStore = { ...mockStore, isLoading: true }
      vi.mocked(useProvidersStore).mockReturnValue(loadingStore)

      renderProviderManagementPage()

      const addButton = screen.getByText('Add Provider')
      expect(addButton).toBeDisabled()
    })
  })

  describe('Error handling', () => {
    it('should display error message when there is an error', () => {
      const errorStore = { ...mockStore, error: 'Failed to load providers' }
      vi.mocked(useProvidersStore).mockReturnValue(errorStore)

      renderProviderManagementPage()

      expect(screen.getByText('Error: Failed to load providers')).toBeInTheDocument()
    })

    it('should show retry button when there is an error', () => {
      const errorStore = { ...mockStore, error: 'Failed to load providers' }
      vi.mocked(useProvidersStore).mockReturnValue(errorStore)

      renderProviderManagementPage()

      expect(screen.getByText('Retry')).toBeInTheDocument()
    })

    it('should retry loading providers when retry button is clicked', async () => {
      const user = userEvent.setup()
      const errorStore = { ...mockStore, error: 'Failed to load providers' }
      vi.mocked(useProvidersStore).mockReturnValue(errorStore)

      renderProviderManagementPage()

      const retryButton = screen.getByText('Retry')
      await user.click(retryButton)

      expect(mockStore.loadProviders).toHaveBeenCalledTimes(1)
    })
  })

  describe('Empty state', () => {
    it('should show empty state message when no providers', () => {
      const emptyStore = { ...mockStore, providers: [] }
      vi.mocked(useProvidersStore).mockReturnValue(emptyStore)

      renderProviderManagementPage()

      expect(screen.getByText('No providers configured yet.')).toBeInTheDocument()
      expect(screen.getByText('Add your first AI provider to get started.')).toBeInTheDocument()
    })
  })

  describe('Form state management', () => {
    it('should reset editing state when form is cancelled', async () => {
      const user = userEvent.setup()
      renderProviderManagementPage()

      // Start editing
      const editButton = screen.getAllByText('Edit')[0]
      await user.click(editButton)

      // Cancel editing
      const cancelButton = screen.getByText('Cancel Form')
      await user.click(cancelButton)

      // Form should be hidden
      expect(screen.queryByTestId('provider-form')).not.toBeInTheDocument()
    })

    it('should reset editing state when form is submitted', async () => {
      const user = userEvent.setup()
      mockStore.updateProvider.mockResolvedValue({
        id: 'openai-1',
        name: 'openai',
        displayName: 'Updated OpenAI',
        description: 'Updated description',
        models: [],
        isActive: true,
        createdAt: '2025-01-10T00:00:00Z',
        updatedAt: '2025-01-11T00:00:00Z'
      })

      renderProviderManagementPage()

      // Start editing
      const editButton = screen.getAllByText('Edit')[0]
      await user.click(editButton)

      // Submit form
      const submitButton = screen.getByText('Submit Form')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.queryByTestId('provider-form')).not.toBeInTheDocument()
      })
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      renderProviderManagementPage()

      const addButton = screen.getByText('Add Provider')
      expect(addButton).toHaveAttribute('aria-label', 'Add new AI provider')
    })

    it('should have proper heading structure', () => {
      renderProviderManagementPage()

      const heading = screen.getByRole('heading', { level: 1 })
      expect(heading).toHaveTextContent('Provider Management')
    })
  })

  describe('Integration with store', () => {
    it('should refresh provider list after creation', async () => {
      const user = userEvent.setup()
      const newProvider = {
        id: 'new-provider',
        name: 'new-provider',
        displayName: 'New Provider',
        description: 'New provider description',
        models: [],
        isActive: true,
        createdAt: '2025-01-10T00:00:00Z',
        updatedAt: '2025-01-10T00:00:00Z'
      }

      mockStore.createProvider.mockResolvedValue(newProvider)

      renderProviderManagementPage()

      // Add provider
      const addButton = screen.getByText('Add Provider')
      await user.click(addButton)

      const submitButton = screen.getByText('Submit Form')
      await user.click(submitButton)

      // Verify provider was added to store
      expect(mockStore.createProvider).toHaveBeenCalledTimes(1)
    })

    it('should update provider list after deletion', async () => {
      const user = userEvent.setup()
      vi.spyOn(window, 'confirm').mockReturnValue(true)

      renderProviderManagementPage()

      // Delete provider
      const deleteButton = screen.getAllByText('Delete')[0]
      await user.click(deleteButton)

      expect(mockStore.deleteProvider).toHaveBeenCalledWith('openai-1')
    })
  })
})