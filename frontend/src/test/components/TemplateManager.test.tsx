import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TemplateManager } from '../../components/TemplateManager'
import { useTemplateStore } from '../../stores/templateStore'

// Mock the template store
vi.mock('../../stores/templateStore', () => ({
  useTemplateStore: vi.fn()
}))

const mockStore = {
  templates: [
    {
      id: 'template-1',
      name: 'Code Review Template',
      category: 'coding',
      description: 'Template for code review requests',
      project_id: null,
      created_at: '2025-01-10T00:00:00Z',
      updated_at: '2025-01-10T00:00:00Z'
    },
    {
      id: 'template-2',
      name: 'Writing Assistant',
      category: 'writing',
      description: 'Help with writing tasks',
      project_id: 'project-1',
      created_at: '2025-01-11T00:00:00Z',
      updated_at: '2025-01-11T00:00:00Z'
    }
  ],
  categories: [
    { name: 'coding', count: 1, description: 'Programming and development templates' },
    { name: 'writing', count: 1, description: 'Writing and content creation templates' },
    { name: 'general', count: 0, description: 'General purpose templates' }
  ],
  isLoading: false,
  error: null,
  loadTemplates: vi.fn(),
  loadCategories: vi.fn(),
  createTemplate: vi.fn(),
  updateTemplate: vi.fn(),
  deleteTemplate: vi.fn(),
  getTemplate: vi.fn()
}

describe('TemplateManager', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useTemplateStore as any).mockReturnValue(mockStore)
  })

  it('renders template manager when open', () => {
    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    expect(screen.getByText('Template Manager')).toBeInTheDocument()
    expect(screen.getByText('Code Review Template')).toBeInTheDocument()
    expect(screen.getByText('Writing Assistant')).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(<TemplateManager isOpen={false} onClose={() => {}} />)

    expect(screen.queryByText('Template Manager')).not.toBeInTheDocument()
  })

  it('loads templates and categories on open', () => {
    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    expect(mockStore.loadTemplates).toHaveBeenCalled()
    expect(mockStore.loadCategories).toHaveBeenCalled()
  })

  it('filters templates by category', async () => {
    const user = userEvent.setup()
    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    const categorySelect = screen.getByDisplayValue('All Categories')
    await user.selectOptions(categorySelect, 'coding')

    expect(screen.getByText('Code Review Template')).toBeInTheDocument()
    expect(screen.queryByText('Writing Assistant')).not.toBeInTheDocument()
  })

  it('opens create template form', async () => {
    const user = userEvent.setup()
    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    const newButton = screen.getByText('New')
    await user.click(newButton)

    expect(screen.getByText('Create Template')).toBeInTheDocument()
  })

  it('creates a new template', async () => {
    const user = userEvent.setup()
    mockStore.createTemplate.mockResolvedValue({
      id: 'template-3',
      name: 'New Template',
      content: 'Template content',
      category: 'general',
      description: 'New template description',
      created_at: '2025-01-12T00:00:00Z',
      updated_at: '2025-01-12T00:00:00Z'
    })

    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    // Open create form
    const newButton = screen.getByText('New')
    await user.click(newButton)

    // Fill form
    const nameInput = screen.getByPlaceholderText('Template name')
    const contentTextarea = screen.getByPlaceholderText('Template content with optional {{placeholders}}')
    const descriptionInput = screen.getByPlaceholderText('Brief description')

    await user.type(nameInput, 'New Template')
    fireEvent.change(contentTextarea, { target: { value: 'Template content with {{variable}}' } })
    await user.type(descriptionInput, 'New template description')

    // Submit form
    const createButton = screen.getByText('Create')
    await user.click(createButton)

    expect(mockStore.createTemplate).toHaveBeenCalledWith({
      name: 'New Template',
      content: 'Template content with {{variable}}',
      category: 'general',
      description: 'New template description'
    })
  })

  it('edits an existing template', async () => {
    const user = userEvent.setup()
    mockStore.getTemplate.mockResolvedValue({
      id: 'template-1',
      name: 'Code Review Template',
      content: 'Please review this code: {{code}}',
      category: 'coding',
      description: 'Template for code review requests',
      project_id: null,
      created_at: '2025-01-10T00:00:00Z',
      updated_at: '2025-01-10T00:00:00Z'
    })
    mockStore.updateTemplate.mockResolvedValue({
      id: 'template-1',
      name: 'Updated Template',
      content: 'Updated content',
      category: 'coding',
      description: 'Updated description',
      project_id: null,
      created_at: '2025-01-10T00:00:00Z',
      updated_at: '2025-01-10T00:00:00Z'
    })

    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    // Click edit button
    const editButtons = screen.getAllByTitle('Edit')
    await user.click(editButtons[0])

    // Update form
    const nameInput = screen.getByDisplayValue('Code Review Template')
    await user.clear(nameInput)
    await user.type(nameInput, 'Updated Template')

    // Submit form
    const updateButton = screen.getByText('Update')
    await user.click(updateButton)

    expect(mockStore.updateTemplate).toHaveBeenCalledWith('template-1', {
      name: 'Updated Template',
      content: 'Please review this code: {{code}}',
      category: 'coding',
      description: 'Template for code review requests',
      project_id: null
    })
  })

  it('previews a template', async () => {
    const user = userEvent.setup()
    mockStore.getTemplate.mockResolvedValue({
      id: 'template-1',
      name: 'Code Review Template',
      content: 'Please review this code: {{code}}',
      category: 'coding',
      description: 'Template for code review requests',
      project_id: null,
      created_at: '2025-01-10T00:00:00Z',
      updated_at: '2025-01-10T00:00:00Z'
    })

    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    // Click preview button
    const previewButtons = screen.getAllByTitle('Preview')
    await user.click(previewButtons[0])

    expect(screen.getByText('Template Preview')).toBeInTheDocument()
    
    // Look for the template name within the preview section
    const previewSection = screen.getByText('Template Preview').closest('.w-1\\/2')
    expect(previewSection).toHaveTextContent('Code Review Template')
    expect(previewSection).toHaveTextContent('Please review this code: {{code}}')
  })

  it('deletes a template', async () => {
    const user = userEvent.setup()
    // Mock window.confirm
    vi.spyOn(window, 'confirm').mockReturnValue(true)

    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    // Click delete button
    const deleteButtons = screen.getAllByTitle('Delete')
    await user.click(deleteButtons[0])

    expect(mockStore.deleteTemplate).toHaveBeenCalledWith('template-1')
  })

  it('closes modal when close button is clicked', async () => {
    const mockOnClose = vi.fn()
    const user = userEvent.setup()
    render(<TemplateManager isOpen={true} onClose={mockOnClose} />)

    const closeButton = screen.getByRole('button', { name: /close template manager/i })
    await user.click(closeButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('shows error message when operations fail', () => {
    const errorStore = { ...mockStore, error: 'Test error message' }
    ;(useTemplateStore as any).mockReturnValue(errorStore)

    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    expect(screen.getByText('Test error message')).toBeInTheDocument()
  })

  it('shows loading state during operations', () => {
    const loadingStore = { ...mockStore, isLoading: true }
    ;(useTemplateStore as any).mockReturnValue(loadingStore)

    render(<TemplateManager isOpen={true} onClose={() => {}} />)

    // Should still render but buttons might be disabled
    expect(screen.getByText('Template Manager')).toBeInTheDocument()
  })
})