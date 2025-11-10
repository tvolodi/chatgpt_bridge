import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'

// Mock the project store
vi.mock('../../stores/projectStore', () => ({
  useProjectStore: vi.fn(),
}))

// Mock the API
vi.mock('../../services/api', () => ({
  projectsAPI: {
    listProjects: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn(),
  },
}))

// Import after mocking
import { ProjectsPage } from '../../pages/ProjectsPage'
import { useProjectStore } from '../../stores/projectStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const mockStore = {
  projects: [
    {
      id: 'default',
      name: 'Default Project',
      description: 'Default project for general conversations',
      parent_id: null,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      has_children: false,
      children_count: 0,
    },
    {
      id: 'project1',
      name: 'Project 1',
      description: 'First project',
      parent_id: null,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      has_children: true,
      children_count: 2,
    },
  ],
  currentProject: null,
  projectTree: [],
  isLoading: false,
  error: null,
  setCurrentProject: vi.fn(),
  setProjects: vi.fn(),
  setProjectTree: vi.fn(),
  setLoading: vi.fn(),
  setError: vi.fn(),
  loadProjects: vi.fn(),
  loadProjectTree: vi.fn(),
  createProject: vi.fn(),
  updateProject: vi.fn(),
  deleteProject: vi.fn(),
  getProject: vi.fn(),
  getProjectStats: vi.fn(),
}

const renderProjectsPage = () => {
  vi.mocked(useProjectStore).mockReturnValue(mockStore)

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ProjectsPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('ProjectsPage Integration Tests', () => {
  let user: ReturnType<typeof userEvent.setup>

  beforeEach(() => {
    user = userEvent.setup()
    vi.clearAllMocks()
  })

  it('renders projects list correctly', () => {
    renderProjectsPage()

    expect(screen.getByText('Projects')).toBeInTheDocument()
    expect(screen.getByText('Default Project')).toBeInTheDocument()
    expect(screen.getByText('Project 1')).toBeInTheDocument()
    expect(screen.getByText('Default project for general conversations')).toBeInTheDocument()
    expect(screen.getByText('First project')).toBeInTheDocument()
  })

  it('shows loading state', () => {
    vi.mocked(useProjectStore).mockReturnValue({
      ...mockStore,
      isLoading: true,
      projects: [], // Empty projects to show loading state
    })

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ProjectsPage />
        </MemoryRouter>
      </QueryClientProvider>
    )

    expect(screen.getByText('Loading projects...')).toBeInTheDocument()
  })

  it('shows error state', () => {
    vi.mocked(useProjectStore).mockReturnValue({
      ...mockStore,
      error: 'Failed to load projects',
    })

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ProjectsPage />
        </MemoryRouter>
      </QueryClientProvider>
    )

    expect(screen.getByText('Failed to load projects')).toBeInTheDocument()
  })

  it('opens create project modal when New Project button is clicked', async () => {
    renderProjectsPage()

    const createButton = screen.getByRole('button', { name: /new project/i })
    await user.click(createButton)

    expect(screen.getByText('Create New Project')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter project name')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter project description (optional)')).toBeInTheDocument()
  })

  it('calls createProject when form is submitted', async () => {
    renderProjectsPage()

    // Open create modal
    const createButton = screen.getByRole('button', { name: /new project/i })
    await user.click(createButton)

    // Fill form
    const nameInput = screen.getByPlaceholderText('Enter project name')
    const descriptionTextarea = screen.getByPlaceholderText('Enter project description (optional)')

    await user.type(nameInput, 'New Test Project')
    await user.type(descriptionTextarea, 'Test description')

    // Submit form
    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)

    expect(mockStore.createProject).toHaveBeenCalledWith({
      name: 'New Test Project',
      description: 'Test description',
    })
  })

  it('opens edit modal when edit button is clicked', async () => {
    renderProjectsPage()

    const editButtons = screen.getAllByRole('button', { name: /edit/i })
    await user.click(editButtons[0]) // Click first edit button

    expect(screen.getByText('Edit Project')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Default Project')).toBeInTheDocument()
  })

  it('calls updateProject when edit form is submitted', async () => {
    renderProjectsPage()

    // Open edit modal
    const editButtons = screen.getAllByRole('button', { name: /edit/i })
    await user.click(editButtons[0])

    // Update form
    const nameInput = screen.getByDisplayValue('Default Project')
    await user.clear(nameInput)
    await user.type(nameInput, 'Updated Project Name')

    // Submit form
    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)

    expect(mockStore.updateProject).toHaveBeenCalledWith('default', {
      name: 'Updated Project Name',
      description: 'Default project for general conversations',
    })
  })

  it('opens delete confirmation modal when delete button is clicked', async () => {
    renderProjectsPage()

    // Find the delete button for the second project (not disabled)
    const deleteButtons = screen.getAllByRole('button').filter((button: HTMLElement) =>
      button.querySelector('svg') && button.className.includes('hover:text-red-400')
    )
    const enabledDeleteButton = deleteButtons.find((button: HTMLButtonElement) => !button.disabled)
    expect(enabledDeleteButton).toBeTruthy()

    await user.click(enabledDeleteButton!)

    expect(screen.getByText('Delete Project')).toBeInTheDocument()
    expect(screen.getByText(/Are you sure you want to delete/)).toBeInTheDocument()
  })

  it('calls deleteProject when delete is confirmed', async () => {
    renderProjectsPage()

    // Find and click the enabled delete button
    const deleteButtons = screen.getAllByRole('button').filter((button: HTMLElement) =>
      button.querySelector('svg') && button.className.includes('hover:text-red-400')
    )
    const enabledDeleteButton = deleteButtons.find((button: HTMLButtonElement) => !button.disabled)
    await user.click(enabledDeleteButton!)

    // Confirm deletion - find the Delete button in the modal (not the icon buttons)
    const confirmButton = screen.getByRole('button', { name: /^Delete$/ })
    await user.click(confirmButton)

    expect(mockStore.deleteProject).toHaveBeenCalledWith('project1')
  })

  it('disables delete button for default project', () => {
    renderProjectsPage()

    // Find all delete buttons
    const deleteButtons = screen.getAllByRole('button').filter((button: HTMLElement) =>
      button.querySelector('svg') && button.className.includes('hover:text-red-400')
    )

    // First delete button should be disabled (default project)
    expect(deleteButtons[0]).toBeDisabled()
    // Second delete button should be enabled
    expect(deleteButtons[1]).not.toBeDisabled()
  })

  it('shows project statistics', () => {
    renderProjectsPage()

    const filesElements = screen.getAllByText('Files')
    expect(filesElements.length).toBeGreaterThan(0)
  })

  it('shows empty state when no projects', () => {
    vi.mocked(useProjectStore).mockReturnValue({
      ...mockStore,
      projects: [],
      isLoading: false,
    })

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ProjectsPage />
        </MemoryRouter>
      </QueryClientProvider>
    )

    expect(screen.getByText('No projects yet')).toBeInTheDocument()
    expect(screen.getByText('Create your first project to get started organizing your conversations.')).toBeInTheDocument()
  })

  it('closes modal when cancel button is clicked', async () => {
    renderProjectsPage()

    // Open create modal
    const createButton = screen.getByRole('button', { name: /new project/i })
    await user.click(createButton)

    expect(screen.getByText('Create New Project')).toBeInTheDocument()

    // Click cancel
    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    expect(screen.queryByText('Create New Project')).not.toBeInTheDocument()
  })

  it('validates required fields', async () => {
    renderProjectsPage()

    // Open create modal
    const createButton = screen.getByRole('button', { name: /new project/i })
    await user.click(createButton)

    // Try to submit without name
    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)

    expect(screen.getByText('Project name is required')).toBeInTheDocument()
  })

  it('clears error when modal is reopened', async () => {
    renderProjectsPage()

    // Open create modal and submit invalid form
    const createButton = screen.getByRole('button', { name: /new project/i })
    await user.click(createButton)

    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)

    expect(screen.getByText('Project name is required')).toBeInTheDocument()

    // Close and reopen modal
    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    await user.click(createButton)

    // Error should be cleared
    expect(screen.queryByText('Project name is required')).not.toBeInTheDocument()
  })
})