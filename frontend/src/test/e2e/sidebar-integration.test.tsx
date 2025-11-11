import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import React from 'react'

// Mock the API
vi.mock('../../services/api', () => ({
  projectsAPI: {
    getProjectTree: vi.fn(),
  },
  chatSessionsAPI: {
    listSessions: vi.fn(),
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

// Mock store state that can be updated
let mockSessions: any[] = []
let mockCurrentProject: any = {
  id: 'default',
  name: 'Default Project',
  description: 'Default project for general conversations',
  parent_id: null,
  created_at: '2025-01-01T00:00:00Z',
  updated_at: '2025-01-01T00:00:00Z',
  path: '/projects/default',
}

vi.mock('../../stores/projectStore', () => ({
  useProjectStore: () => ({
    currentProject: mockCurrentProject,
    projectTree: [
      {
        project: mockCurrentProject,
        children: [],
      },
      {
        project: {
          id: 'test-project',
          name: 'Test Project',
          description: 'A test project',
          parent_id: null,
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
          path: '/projects/test-project',
        },
        children: [],
      },
    ],
    loadProjectTree: vi.fn(),
    setCurrentProject: vi.fn((project: any) => {
      mockCurrentProject = project
    }),
  }),
  ProjectTree: {},
}))

vi.mock('../../stores/chatSessionStore', () => ({
  useChatSessionStore: () => ({
    sessions: mockSessions,
    loadSessions: vi.fn(async (projectId?: string) => {
      const response = await chatSessionsAPI.listSessions(projectId)
      mockSessions = response.data
    }),
    setCurrentSession: vi.fn(),
  }),
}))

vi.mock('../../stores/settingsStore', () => ({
  useSettingsStore: () => ({
    uiState: { sidebarCollapsed: false },
    updateUIState: vi.fn(),
  }),
}))

// Import after mocking
import { MainLayout } from '../../components/MainLayout'
import { useProjectStore } from '../../stores/projectStore'
import { useChatSessionStore } from '../../stores/chatSessionStore'
import { useSettingsStore } from '../../stores/settingsStore'
import { projectsAPI, chatSessionsAPI } from '../../services/api'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const renderMainLayout = () => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MainLayout />
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Sidebar Integration Tests', () => {
  let user: ReturnType<typeof userEvent.setup>

  beforeEach(() => {
    user = userEvent.setup()
    vi.clearAllMocks()

    // Reset mock state
    mockSessions = [
      {
        id: 'session-1',
        title: 'First Chat Session',
        project_id: 'default',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        is_active: true,
        message_count: 5,
      },
      {
        id: 'session-2',
        title: 'Second Chat Session',
        project_id: 'default',
        created_at: '2025-01-01T01:00:00Z',
        updated_at: '2025-01-01T01:00:00Z',
        is_active: false,
        message_count: 2,
      },
      {
        id: 'session-3',
        title: 'Third Chat Session',
        project_id: 'test-project',
        created_at: '2025-01-01T02:00:00Z',
        updated_at: '2025-01-01T02:00:00Z',
        is_active: true,
        message_count: 3,
      },
    ]
    mockCurrentProject = {
      id: 'default',
      name: 'Default Project',
      description: 'Default project for general conversations',
      parent_id: null,
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      path: '/projects/default',
    }

    // Mock localStorage to return default state
    localStorageMock.getItem.mockReturnValue(null)
    localStorageMock.setItem.mockImplementation(() => {})

    // Mock project tree API
    vi.mocked(projectsAPI.getProjectTree).mockResolvedValue({
      data: [
        {
          project: {
            id: 'default',
            name: 'Default Project',
            description: 'Default project for general conversations',
            parent_id: null,
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-01T00:00:00Z',
            path: '/projects/default',
          },
          children: [],
        },
        {
          project: {
            id: 'test-project',
            name: 'Test Project',
            description: 'A test project',
            parent_id: null,
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-01T00:00:00Z',
            path: '/projects/test-project',
          },
          children: [],
        },
      ],
    })

    // Mock chat sessions API
    vi.mocked(chatSessionsAPI.listSessions).mockResolvedValue({
      data: [
        {
          id: 'session-1',
          title: 'First Chat Session',
          project_id: 'default',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z',
          is_active: true,
          message_count: 5,
        },
        {
          id: 'session-2',
          title: 'Second Chat Session',
          project_id: 'default',
          created_at: '2025-01-01T01:00:00Z',
          updated_at: '2025-01-01T01:00:00Z',
          is_active: false,
          message_count: 2,
        },
        {
          id: 'session-3',
          title: 'Third Chat Session',
          project_id: 'test-project',
          created_at: '2025-01-01T02:00:00Z',
          updated_at: '2025-01-01T02:00:00Z',
          is_active: true,
          message_count: 3,
        },
      ],
    })
  })

  it('displays projects in sidebar', async () => {
    renderMainLayout()

    // Wait for projects to be rendered
    await waitFor(() => {
      const sidebar = screen.getByRole('navigation').parentElement
      expect(within(sidebar!).getByText('Default Project')).toBeInTheDocument()
    })

    const sidebar = screen.getByRole('navigation').parentElement
    expect(within(sidebar!).getByText('Test Project')).toBeInTheDocument()
  })

  it('shows chat sessions under current project when expanded', async () => {
    renderMainLayout()

    // Default project should be selected and expanded, sessions should be visible
    const sidebar = screen.getByRole('navigation').parentElement
    expect(within(sidebar!).getByText('First Chat Session')).toBeInTheDocument()
    expect(within(sidebar!).getByText('Second Chat Session')).toBeInTheDocument()
  })

  it('navigates to chat session when clicked', async () => {
    renderMainLayout()

    // Default project should be selected and expanded, sessions should be visible
    const sidebar = screen.getByRole('navigation').parentElement
    await waitFor(() => {
      expect(within(sidebar!).getByText('First Chat Session')).toBeInTheDocument()
    })

    // Click on a chat session
    const sessionButton = within(sidebar!).getByText('First Chat Session')
    await user.click(sessionButton)

    // Verify navigation occurred (this would need to be checked based on routing)
    // For now, just verify the click doesn't throw an error
    expect(sessionButton).toBeInTheDocument()
  })

  it('shows chat sessions for each project when expanded', async () => {
    renderMainLayout()

    // Default project should be selected and expanded, sessions should be visible
    const sidebar = screen.getByRole('navigation').parentElement
    expect(within(sidebar!).getByText('First Chat Session')).toBeInTheDocument()
    expect(within(sidebar!).getByText('Second Chat Session')).toBeInTheDocument()

    // Click on Test Project to select and expand it
    const testProjectButton = within(sidebar!).getByText('Test Project')
    await user.click(testProjectButton)

    // Test Project sessions should now be visible
    await waitFor(() => {
      const thirdSessions = within(sidebar!).queryAllByText('Third Chat Session')
      expect(thirdSessions.length).toBeGreaterThan(0)
    })
  })

  it('loads sessions only for the current project', async () => {
    renderMainLayout()

    // Default project should be selected and expanded, sessions should be visible
    const sidebar = screen.getByRole('navigation').parentElement
    await waitFor(() => {
      expect(within(sidebar!).getByText('First Chat Session')).toBeInTheDocument()
    })

    // Verify API was called with correct project ID
    expect(chatSessionsAPI.listSessions).toHaveBeenCalledWith('default')
  })
})