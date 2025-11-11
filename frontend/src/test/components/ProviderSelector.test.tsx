import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ProviderSelector } from '../../components/ProviderSelector'
import { useProvidersStore } from '../../stores/providersStore'

// Mock the providers store
vi.mock('../../stores/providersStore', () => ({
  useProvidersStore: vi.fn()
}))

const mockStore = {
  providers: [
    {
      id: 'openai-1',
      name: 'openai',
      displayName: 'OpenAI',
      description: 'OpenAI GPT models',
      baseUrl: 'https://api.openai.com/v1',
      models: [],
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
  getActiveProviders: vi.fn().mockReturnValue([
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
  ]),
  getProviderConfig: vi.fn().mockImplementation((providerId: string) => {
    if (providerId === 'openai-1') {
      return { providerId: 'openai-1', apiKey: 'sk-test-key' }
    }
    return null // anthropic-1 has no config
  })
}

const renderProviderSelector = (props = {}) => {
  return render(
    <ProviderSelector
      selectedProviderId={undefined}
      onProviderChange={() => {}}
      {...props}
    />
  )
}

describe('ProviderSelector Component Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useProvidersStore).mockReturnValue(mockStore)
  })

  describe('Initial render', () => {
    it('should render provider selector button', () => {
      renderProviderSelector()

      expect(screen.getByRole('button')).toBeInTheDocument()
      expect(screen.getByText('OpenAI')).toBeInTheDocument()
    })

    it('should show selected provider when selectedProviderId is provided', () => {
      renderProviderSelector({
        selectedProviderId: 'anthropic-1'
      })

      expect(screen.getByText('Anthropic')).toBeInTheDocument()
    })

    it('should show "Select Provider" when no providers available', () => {
      const emptyStore = {
        ...mockStore,
        getActiveProviders: vi.fn().mockReturnValue([])
      }
      vi.mocked(useProvidersStore).mockReturnValue(emptyStore)

      renderProviderSelector()

      expect(screen.getByText('Select Provider')).toBeInTheDocument()
    })
  })

  describe('Dropdown functionality', () => {
    it('should open dropdown when button is clicked', async () => {
      const user = userEvent.setup()
      renderProviderSelector()

      const button = screen.getByRole('button')
      await user.click(button)

      expect(screen.getByText('OpenAI GPT models')).toBeInTheDocument()
      expect(screen.getByText('Anthropic Claude models')).toBeInTheDocument()
    })

    it('should show model count for each provider', async () => {
      const user = userEvent.setup()
      renderProviderSelector()

      const button = screen.getByRole('button')
      await user.click(button)

      expect(screen.getByText('2 models')).toBeInTheDocument()
      expect(screen.getByText('1 models')).toBeInTheDocument()
    })

    it('should call onProviderChange when provider is selected', async () => {
      const user = userEvent.setup()
      const mockOnProviderChange = vi.fn()

      renderProviderSelector({
        onProviderChange: mockOnProviderChange
      })

      const button = screen.getByRole('button')
      await user.click(button)

      const anthropicOption = screen.getByText('Anthropic')
      await user.click(anthropicOption)

      expect(mockOnProviderChange).toHaveBeenCalledWith('anthropic-1')
    })

    it('should close dropdown after selection', async () => {
      const user = userEvent.setup()
      const mockOnProviderChange = vi.fn()

      renderProviderSelector({
        onProviderChange: mockOnProviderChange
      })

      const button = screen.getByRole('button')
      await user.click(button)

      const anthropicOption = screen.getByText('Anthropic')
      await user.click(anthropicOption)

      expect(screen.queryByText('OpenAI GPT models')).not.toBeInTheDocument()
    })
  })

  describe('Empty state', () => {
    it('should show empty state message when no active providers', async () => {
      const user = userEvent.setup()
      const emptyStore = {
        ...mockStore,
        getActiveProviders: vi.fn().mockReturnValue([])
      }
      vi.mocked(useProvidersStore).mockReturnValue(emptyStore)

      renderProviderSelector()

      const button = screen.getByRole('button')
      await user.click(button)

      expect(screen.getByText('No active providers')).toBeInTheDocument()
      expect(screen.getByText('Configure providers in Settings')).toBeInTheDocument()
    })
  })

  describe('Styling', () => {
    it('should apply custom className', () => {
      renderProviderSelector({
        className: 'custom-class'
      })

      const container = screen.getByRole('button').parentElement
      expect(container).toHaveClass('custom-class')
    })

    it('should highlight selected provider', async () => {
      const user = userEvent.setup()

      renderProviderSelector({
        selectedProviderId: 'openai-1'
      })

      const button = screen.getByRole('button')
      await user.click(button)

      // The selected provider should have different styling - find the button in the dropdown
      const dropdownButtons = screen.getAllByRole('button')
      const selectedButton = dropdownButtons.find(button =>
        button.textContent?.includes('OpenAI') &&
        button.classList.contains('bg-slate-700')
      )
      expect(selectedButton).toBeInTheDocument()
    })
  })

  describe('Integration with store', () => {
    it('should call getActiveProviders on render', () => {
      renderProviderSelector()

      expect(mockStore.getActiveProviders).toHaveBeenCalled()
    })

    it('should use providers from store', async () => {
      const user = userEvent.setup()

      renderProviderSelector()

      const button = screen.getByRole('button')
      await user.click(button)

      // Check that both providers are shown in the dropdown
      expect(screen.getAllByText('OpenAI')).toHaveLength(2) // One in button, one in dropdown
      expect(screen.getByText('Anthropic')).toBeInTheDocument()
    })
  })

  describe('Visual Indicators', () => {
    it('should show checkmark next to selected provider in dropdown', async () => {
      const user = userEvent.setup()

      renderProviderSelector({
        selectedProviderId: 'openai-1'
      })

      const button = screen.getByRole('button')
      await user.click(button)

      // Find the OpenAI button in dropdown and check for checkmark
      const openaiButton = screen.getAllByText('OpenAI')[1].closest('button')
      const checkIcon = openaiButton?.querySelector('svg.lucide-check')
      expect(checkIcon).toBeInTheDocument()
    })

    it('should show warning icon and disabled styling for providers without API key', async () => {
      const user = userEvent.setup()

      renderProviderSelector()

      const button = screen.getByRole('button')
      await user.click(button)

      // Anthropic should be disabled and show warning
      const anthropicButton = screen.getByText('Anthropic').closest('button')
      expect(anthropicButton).toHaveAttribute('disabled')
      expect(anthropicButton).toHaveClass('opacity-60')
      expect(anthropicButton).toHaveClass('cursor-not-allowed')

      // Should show warning icon and message
      const warningIcon = anthropicButton?.querySelector('svg.lucide-alert-triangle')
      expect(warningIcon).toBeInTheDocument()
      expect(screen.getByText('API key not configured')).toBeInTheDocument()
    })

    it('should not call onProviderChange when clicking disabled provider', async () => {
      const user = userEvent.setup()
      const mockOnProviderChange = vi.fn()

      renderProviderSelector({
        onProviderChange: mockOnProviderChange
      })

      const button = screen.getByRole('button')
      await user.click(button)

      // Try to click disabled Anthropic provider
      const anthropicButton = screen.getByText('Anthropic').closest('button')
      await user.click(anthropicButton!)

      // Should not call onProviderChange
      expect(mockOnProviderChange).not.toHaveBeenCalled()
    })

    it('should allow clicking configured providers', async () => {
      const user = userEvent.setup()
      const mockOnProviderChange = vi.fn()

      renderProviderSelector({
        onProviderChange: mockOnProviderChange
      })

      const button = screen.getByRole('button')
      await user.click(button)

      // Click configured OpenAI provider
      const openaiButton = screen.getAllByText('OpenAI')[1].closest('button')
      await user.click(openaiButton!)

      // Should call onProviderChange
      expect(mockOnProviderChange).toHaveBeenCalledWith('openai-1')
    })
  })

  describe('Provider Configuration Integration', () => {
    it('should call getProviderConfig for each provider', async () => {
      const user = userEvent.setup()

      renderProviderSelector()

      const button = screen.getByRole('button')
      await user.click(button)

      // Should call getProviderConfig for both providers
      expect(mockStore.getProviderConfig).toHaveBeenCalledWith('openai-1')
      expect(mockStore.getProviderConfig).toHaveBeenCalledWith('anthropic-1')
    })

    it('should update visual state when provider configuration changes', async () => {
      const user = userEvent.setup()

      renderProviderSelector()

      const button = screen.getByRole('button')
      await user.click(button)

      // Initially Anthropic should be disabled
      let anthropicButton = screen.getByText('Anthropic').closest('button')
      expect(anthropicButton).toHaveAttribute('disabled')

      // Simulate configuring Anthropic
      mockStore.getProviderConfig.mockImplementation((providerId: string) => {
        if (providerId === 'openai-1' || providerId === 'anthropic-1') {
          return { providerId, apiKey: 'sk-test-key' }
        }
        return null
      })

      // Re-render component
      renderProviderSelector()

      const newButton = screen.getByRole('button')
      await user.click(newButton)

      // Now Anthropic should be enabled
      anthropicButton = screen.getByText('Anthropic').closest('button')
      expect(anthropicButton).not.toHaveAttribute('disabled')
      expect(anthropicButton).not.toHaveClass('opacity-60')
    })
  })
) 
 
 