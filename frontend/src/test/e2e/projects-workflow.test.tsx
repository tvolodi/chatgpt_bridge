import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'

// Mock the API
vi.mock('../../services/api', () => ({
  projectsAPI: {
    listProjects: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn(),
    getProjectTree: vi.fn(),
  },
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Import after mocking
import { ProjectsPage } from '../../pages/ProjectsPage'
import { projectsAPI } from '../../services/api'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const renderProjectsPage = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ProjectsPage />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Projects End-to-End Tests', () => {
  let user: ReturnType<typeof userEvent.setup>

  beforeEach(() => {
    user = userEvent.setup()
    vi.clearAllMocks()

    // Mock localStorage to return default state
    localStorageMock.getItem.mockReturnValue(null)
    localStorageMock.setItem.mockImplementation(() => {})

    // Mock API responses
    vi.mocked(projectsAPI.listProjects).mockResolvedValue({
      data: [
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
          id: 'test-project',
          name: 'Test Project',
          description: 'A test project for deletion',
          parent_id: null,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
          has_children: false,
          children_count: 0,
        },
      ],
    })

    vi.mocked(projectsAPI.createProject).mockResolvedValue({
      data: {
        id: 'test-project',
        name: 'Test Project',
        description: 'A test project',
        parent_id: null,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        path: '/projects/test-project',
      },
    })

    vi.mocked(projectsAPI.updateProject).mockResolvedValue({
      data: {
        id: 'default',
        name: 'Updated Default Project',
        description: 'Updated description',
        parent_id: null,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        path: '/projects/default',
      },
    })

    vi.mocked(projectsAPI.deleteProject).mockResolvedValue(undefined)
  })

  it('loads and displays projects list', async () => {
    renderProjectsPage()

    // Wait for projects to load
    await waitFor(() => {
      expect(screen.getByText('Default Project')).toBeInTheDocument()
    })

    // Check project details are displayed
    expect(screen.getByText('Default project for general conversations')).toBeInTheDocument()
    expect(screen.getAllByText('Files')).toHaveLength(2) // Both projects have Files
  })

  it('creates a new project successfully', async () => {
    renderProjectsPage()

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Default Project')).toBeInTheDocument()
    })

    // Click create project button
    const createButton = screen.getByRole('button', { name: /new project/i })
    await user.click(createButton)

    // Fill out the form
    const nameInput = screen.getByLabelText('Project Name *')
    const descriptionTextarea = screen.getByPlaceholderText('Enter project description (optional)')

    await user.type(nameInput, 'Test Project')
    await user.type(descriptionTextarea, 'A test project')

    // Submit the form
    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)

    // Verify API was called
    await waitFor(() => {
      expect(projectsAPI.createProject).toHaveBeenCalledWith({
        name: 'Test Project',
        description: 'A test project',
      })
    })

    // Verify projects list was refreshed
    expect(projectsAPI.listProjects).toHaveBeenCalledTimes(2)
  })

  it('validates project name is required', async () => {
    renderProjectsPage()

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Default Project')).toBeInTheDocument()
    })

    // Click create project button
    const createButton = screen.getByRole('button', { name: /new project/i })
    await user.click(createButton)

    // Try to submit without name
    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)

    // Check validation error
    expect(screen.getByText('Project name is required')).toBeInTheDocument()
  })

  it('edits an existing project', async () => {
    renderProjectsPage()

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Default Project')).toBeInTheDocument()
    })

    // Click edit button on the project card
    const editButton = screen.getByRole('button', { name: /edit default project/i })
    await user.click(editButton)

    // Update the form
    const nameInput = screen.getByDisplayValue('Default Project')
    const descriptionTextarea = screen.getByDisplayValue('Default project for general conversations')

    await user.clear(nameInput)
    await user.type(nameInput, 'Updated Default Project')
    await user.clear(descriptionTextarea)
    await user.type(descriptionTextarea, 'Updated description')

    // Submit the form
    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)

    // Verify API was called
    await waitFor(() => {
      expect(projectsAPI.updateProject).toHaveBeenCalledWith('default', {
        name: 'Updated Default Project',
        description: 'Updated description',
      })
    })
  })

  it('deletes a project with confirmation', async () => {
    renderProjectsPage()

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })

    // Click delete button on the test project card
    const deleteButton = screen.getByRole('button', { name: /delete test project/i })
    await user.click(deleteButton)

    // Confirm deletion in modal
    expect(screen.getByText('Delete Project')).toBeInTheDocument()
    expect(screen.getByText(/Are you sure you want to delete/)).toBeInTheDocument()

    const confirmButton = screen.getByRole('button', { name: 'Delete' }) // Exact match for the modal button
    await user.click(confirmButton)

    // Verify API was called
    await waitFor(() => {
      expect(projectsAPI.deleteProject).toHaveBeenCalledWith('test-project', false)
    })
  })

  it('handles API errors gracefully', async () => {
    // Mock API to reject
    vi.mocked(projectsAPI.createProject).mockRejectedValue(new Error('API Error'))

    renderProjectsPage()

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Default Project')).toBeInTheDocument()
    })

    // Try to create a project
    const createButton = screen.getByRole('button', { name: /new project/i })
    await user.click(createButton)

    const nameInput = screen.getByLabelText('Project Name *')
    await user.type(nameInput, 'Test Project')

    const saveButton = screen.getByRole('button', { name: /save/i })
    await user.click(saveButton)

    // Check error is displayed in the modal
    await waitFor(() => {
      const errorElements = screen.getAllByText('API Error')
      expect(errorElements.length).toBeGreaterThan(0)
    })
  })

  it('shows empty state when no projects exist', async () => {
    // Mock empty projects list
    vi.mocked(projectsAPI.listProjects).mockResolvedValue({ data: [] })

    renderProjectsPage()

    // Wait for empty state
    await waitFor(() => {
      expect(screen.getByText('No projects yet')).toBeInTheDocument()
    })

    expect(screen.getByText('Create your first project to get started organizing your conversations.')).toBeInTheDocument()
  })

  it('prevents deleting the default project', async () => {
    renderProjectsPage()

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Default Project')).toBeInTheDocument()
    })

    // The delete button should be disabled for default project
    const deleteButton = screen.getByRole('button', { name: 'Delete Default Project' })
    expect(deleteButton).toBeDisabled()
  })
})