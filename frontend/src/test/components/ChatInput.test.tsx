import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatInput } from '../../components/ChatInput'
import { useTemplateStore } from '../../stores/templateStore'

// Mock the template store
vi.mock('../../stores/templateStore', () => ({
  useTemplateStore: vi.fn()
}))

const mockStore = {
  templates: [
    {
      id: 'template-1',
      name: 'Greeting Template',
      category: 'general',
      description: 'A simple greeting',
      project_id: null,
      created_at: '2025-01-10T00:00:00Z',
      updated_at: '2025-01-10T00:00:00Z'
    },
    {
      id: 'template-2',
      name: 'Code Review',
      category: 'coding',
      description: 'Request code review',
      project_id: null,
      created_at: '2025-01-11T00:00:00Z',
      updated_at: '2025-01-11T00:00:00Z'
    }
  ],
  loadTemplates: vi.fn(),
  substituteTemplate: vi.fn(),
  getTemplatePlaceholders: vi.fn()
}

describe('ChatInput with Templates', () => {
  const mockOnSend = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useTemplateStore as any).mockReturnValue(mockStore)
  })

  it('renders chat input with template selector', () => {
    render(<ChatInput onSend={mockOnSend} />)

    expect(screen.getByPlaceholderText('Ask me anything...')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('loads templates on mount', () => {
    render(<ChatInput onSend={mockOnSend} />)

    expect(mockStore.loadTemplates).toHaveBeenCalled()
  })

  it('opens template dropdown when template button is clicked', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSend={mockOnSend} />)

    const templateButton = screen.getByTitle('Insert template')
    await user.click(templateButton)

    expect(screen.getByText('Greeting Template')).toBeInTheDocument()
    expect(screen.getByText('Code Review')).toBeInTheDocument()
  })

  it('inserts template without parameters', async () => {
    const user = userEvent.setup()
    mockStore.substituteTemplate.mockResolvedValue({
      template_id: 'template-1',
      original_content: 'Hello {{name}}!',
      substituted_content: 'Hello {{name}}!',
      placeholders_found: ['name']
    })
    mockStore.getTemplatePlaceholders.mockResolvedValue([])

    render(<ChatInput onSend={mockOnSend} />)

    // Open template dropdown
    const templateButton = screen.getByTitle('Insert template')
    await user.click(templateButton)

    // Select template
    const templateOption = screen.getByText('Greeting Template')
    await user.click(templateOption)

    // Since no placeholders, template should be inserted directly
    await waitFor(() => {
      expect(mockStore.substituteTemplate).toHaveBeenCalledWith('template-1', {})
    })
  })

  it('shows parameter modal for template with placeholders', async () => {
    const user = userEvent.setup()
    mockStore.getTemplatePlaceholders.mockResolvedValue(['name', 'topic'])
    mockStore.substituteTemplate.mockResolvedValue({
      template_id: 'template-1',
      original_content: 'Hello {{name}}! Lets discuss {{topic}}.',
      substituted_content: 'Hello John! Lets discuss AI.',
      placeholders_found: ['name', 'topic']
    })

    render(<ChatInput onSend={mockOnSend} />)

    // Open template dropdown
    const templateButton = screen.getByTitle('Insert template')
    await user.click(templateButton)

    // Select template
    const templateOption = screen.getByText('Greeting Template')
    await user.click(templateOption)

    // Should show parameter modal
    expect(screen.getByText('Fill Template Parameters')).toBeInTheDocument()
    expect(screen.getByText('Greeting Template')).toBeInTheDocument()
    expect(screen.getByText('name')).toBeInTheDocument()
    expect(screen.getByText('topic')).toBeInTheDocument()
  })

  it('substitutes parameters and inserts template', async () => {
    const user = userEvent.setup()
    mockStore.getTemplatePlaceholders.mockResolvedValue(['name'])
    mockStore.substituteTemplate.mockResolvedValue({
      template_id: 'template-1',
      original_content: 'Hello {{name}}!',
      substituted_content: 'Hello Alice!',
      placeholders_found: ['name']
    })

    render(<ChatInput onSend={mockOnSend} />)

    // Open template dropdown and select template
    const templateButton = screen.getByTitle('Insert template')
    await user.click(templateButton)
    const templateOption = screen.getByText('Greeting Template')
    await user.click(templateOption)

    // Fill parameter
    const nameInput = screen.getByPlaceholderText('Enter value for name')
    await user.type(nameInput, 'Alice')

    // Submit parameters
    const insertButton = screen.getByText('Insert Template')
    await user.click(insertButton)

    expect(mockStore.substituteTemplate).toHaveBeenCalledWith('template-1', { name: 'Alice' })
  })

  it('cancels parameter modal', async () => {
    const user = userEvent.setup()
    mockStore.getTemplatePlaceholders.mockResolvedValue(['name'])

    render(<ChatInput onSend={mockOnSend} />)

    // Open template dropdown and select template
    const templateButton = screen.getByTitle('Insert template')
    await user.click(templateButton)
    const templateOption = screen.getByText('Greeting Template')
    await user.click(templateOption)

    // Cancel modal
    const cancelButton = screen.getByText('Cancel')
    await user.click(cancelButton)

    expect(screen.queryByText('Fill Template Parameters')).not.toBeInTheDocument()
  })

  it('clears selected template', async () => {
    const user = userEvent.setup()
    mockStore.getTemplatePlaceholders.mockResolvedValue([])
    mockStore.substituteTemplate.mockResolvedValue({
      template_id: 'template-1',
      original_content: 'Hello!',
      substituted_content: 'Hello!',
      placeholders_found: []
    })

    render(<ChatInput onSend={mockOnSend} />)

    // Select a template
    const templateButton = screen.getByTitle('Insert template')
    await user.click(templateButton)
    const templateOption = screen.getByText('Greeting Template')
    await user.click(templateOption)

    // Should show template indicator
    expect(screen.getByPlaceholderText('Using template: Greeting Template')).toBeInTheDocument()

    // Clear template
    const clearButton = screen.getByTitle('Clear template')
    await user.click(clearButton)

    expect(screen.getByPlaceholderText('Ask me anything...')).toBeInTheDocument()
  })

  it('sends message with template content', async () => {
    const user = userEvent.setup()
    mockStore.getTemplatePlaceholders.mockResolvedValue([])
    mockStore.substituteTemplate.mockResolvedValue({
      template_id: 'template-1',
      original_content: 'Hello World!',
      substituted_content: 'Hello World!',
      placeholders_found: []
    })

    render(<ChatInput onSend={mockOnSend} />)

    // Select template
    const templateButton = screen.getByTitle('Insert template')
    await user.click(templateButton)
    const templateOption = screen.getByText('Greeting Template')
    await user.click(templateOption)

    // Send message
    const sendButton = screen.getByRole('button', { name: /send/i })
    await user.click(sendButton)

    expect(mockOnSend).toHaveBeenCalledWith('Hello World!')
  })

  it('disables send button when input is empty', () => {
    render(<ChatInput onSend={mockOnSend} />)

    const sendButton = screen.getByRole('button', { name: /send/i })
    expect(sendButton).toBeDisabled()
  })

  it('disables send button when loading', () => {
    render(<ChatInput onSend={mockOnSend} isLoading={true} />)

    const input = screen.getByPlaceholderText('Ask me anything...')
    const sendButton = screen.getByRole('button', { name: /send/i })

    expect(input).toBeDisabled()
    expect(sendButton).toBeDisabled()
  })

  it('handles enter key to send message', async () => {
    const user = userEvent.setup()
    render(<ChatInput onSend={mockOnSend} />)

    const input = screen.getByPlaceholderText('Ask me anything...')
    await user.type(input, 'Test message')
    await user.keyboard('{Enter}')

    expect(mockOnSend).toHaveBeenCalledWith('Test message')
  })
})