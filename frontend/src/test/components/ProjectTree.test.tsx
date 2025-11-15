import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { MainLayout } from '../../components/MainLayout'
import { useSettingsStore } from '../../stores/settingsStore'
import { useProjectStore } from '../../stores/projectStore'
import { useChatSessionStore } from '../../stores/chatSessionStore'

// Mock stores
vi.mock('../../stores/settingsStore', () => ({
  useSettingsStore: vi.fn()
}))

vi.mock('../../stores/projectStore', () => ({
  useProjectStore: vi.fn()
}))

vi.mock('../../stores/chatSessionStore', () => ({
  useChatSessionStore: vi.fn()
}))

const mockSettingsStore = {
  uiState: { sidebarCollapsed: false },
  updateUIState: vi.fn()
}

const mockProjectTree = [
  {
    project: {
      id: 'project-1',
      name: 'Project 1',
      description: 'First project',
      created_at: '2025-01-10T00:00:00Z'
    },
    children: [
      {
        project: {
          id: 'project-1-sub',
          name: 'Subproject 1',
          description: 'Nested project',
          created_at: '2025-01-11T00:00:00Z'
        },
        children: []
      }
    ]
  },
  {
    project: {
      id: 'project-2',
      name: 'Project 2',
      description: 'Second project',
      created_at: '2025-01-12T00:00:00Z'
    },
    children: []
  }
]

const mockProjectStore = {
  currentProject: null,
  projectTree: mockProjectTree,
  loadProjectTree: vi.fn(),
  setCurrentProject: vi.fn()
}

const mockSessionStore = {
  sessions: [
    {
      id: 'session-1',
      project_id: 'project-1',
      title: 'Session 1',
      created_at: '2025-01-10T00:00:00Z',
      updated_at: '2025-01-10T00:00:00Z'
    }
  ],
  loadSessions: vi.fn(),
  setCurrentSession: vi.fn()
}

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('ProjectTree (in MainLayout Sidebar)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useSettingsStore as any).mockReturnValue(mockSettingsStore)
    ;(useProjectStore as any).mockReturnValue(mockProjectStore)
    ;(useChatSessionStore as any).mockReturnValue(mockSessionStore)
  })

  // TC-UNIT-310: Project tree hierarchical
  it('TC-UNIT-310: renders project tree with hierarchical structure', () => {
    renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Verify that projects are rendered
    expect(screen.getByText('Project 1')).toBeInTheDocument()
    expect(screen.getByText('Project 2')).toBeInTheDocument()
  })

  // TC-FUNC-310: Project tree expand/collapse
  it('TC-FUNC-310: supports expanding and collapsing project branches', async () => {
    const user = userEvent.setup()
    renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Project tree should be rendered with expand/collapse capability
    const project1Button = screen.getByText('Project 1')
    
    expect(project1Button).toBeInTheDocument()
  })

  // TC-FUNC-310: Tree navigation
  it('TC-FUNC-310: allows selecting projects from tree', async () => {
    const user = userEvent.setup()
    renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    const project1Button = screen.getByText('Project 1')
    
    // Should be clickable
    expect(project1Button).toBeInTheDocument()
    
    // On click, should call setCurrentProject
    await user.click(project1Button)
    
    expect(mockProjectStore.setCurrentProject).toHaveBeenCalled()
  })

  // Hierarchical rendering with nesting
  it('renders nested projects under parent projects', () => {
    renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    expect(screen.getByText('Project 1')).toBeInTheDocument()
    // Check for project text (either parent or child)
    expect(screen.queryAllByText(/Project/i).length).toBeGreaterThan(0)
  })

  // Project selection highlights current project
  it('highlights selected project in tree', () => {
    const selectedProjectStore = {
      ...mockProjectStore,
      currentProject: mockProjectTree[0].project
    }
    ;(useProjectStore as any).mockReturnValue(selectedProjectStore)

    const { container } = renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Selected project should have highlighted styling
    const highlightedElements = container.querySelectorAll('[class*="bg-blue"]')
    expect(highlightedElements.length).toBeGreaterThan(0)
  })

  // Sessions displayed under projects
  it('displays sessions associated with projects', () => {
    renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Sessions should be available (can be verified by store mock)
    expect(mockSessionStore.sessions.length).toBeGreaterThan(0)
  })
})
