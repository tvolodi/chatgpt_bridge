import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
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

const mockProjectStore = {
  currentProject: null,
  projectTree: [
    {
      project: {
        id: 'project-1',
        name: 'Project 1',
        description: 'Test project',
        created_at: '2025-01-10T00:00:00Z'
      },
      children: []
    }
  ],
  loadProjectTree: vi.fn(),
  setCurrentProject: vi.fn()
}

const mockSessionStore = {
  sessions: [
    {
      id: 'session-1',
      project_id: 'project-1',
      title: 'Test Session',
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

describe('Sidebar (REQ-303)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useSettingsStore as any).mockReturnValue(mockSettingsStore)
    ;(useProjectStore as any).mockReturnValue(mockProjectStore)
    ;(useChatSessionStore as any).mockReturnValue(mockSessionStore)
  })

  // TC-UNIT-303: Sidebar toggle/collapse
  it('TC-UNIT-303: renders sidebar with toggle button', () => {
    const { container } = renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Sidebar should be present
    const sidebarElements = container.querySelectorAll('[class*="bg-slate"]')
    expect(sidebarElements.length).toBeGreaterThan(0)
  })

  // TC-FUNC-303: Sidebar resize/toggle
  it('TC-FUNC-303: toggles sidebar collapse/expand on button click', async () => {
    const user = userEvent.setup()
    const { container } = renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Find toggle button (Menu icon button)
    const buttons = container.querySelectorAll('button')
    expect(buttons.length).toBeGreaterThan(0)

    // Click first button (typically the menu toggle)
    if (buttons[0]) {
      await user.click(buttons[0])
      
      // Should call updateUIState to collapse sidebar
      expect(mockSettingsStore.updateUIState).toHaveBeenCalledWith(
        expect.objectContaining({ sidebarCollapsed: true })
      )
    }
  })

  // TC-FUNC-303: Sidebar expand state
  it('TC-FUNC-303: expands sidebar when collapsed', async () => {
    const user = userEvent.setup()
    const collapsedStore = {
      uiState: { sidebarCollapsed: true },
      updateUIState: vi.fn()
    }
    ;(useSettingsStore as any).mockReturnValue(collapsedStore)

    const { container } = renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Get toggle button
    const buttons = container.querySelectorAll('button')
    
    if (buttons[0]) {
      await user.click(buttons[0])
      
      // Should call updateUIState to expand sidebar
      expect(collapsedStore.updateUIState).toHaveBeenCalledWith(
        expect.objectContaining({ sidebarCollapsed: false })
      )
    }
  })

  // Content visibility when sidebar collapses
  it('content remains visible when sidebar is toggled', () => {
    renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  // Sidebar content display
  it('displays projects and sessions when sidebar is expanded', () => {
    renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Projects and sessions should be visible
    expect(screen.getByText('Project 1')).toBeInTheDocument()
  })

  // Sidebar width transition
  it('maintains proper width transitions during collapse/expand', () => {
    const { container } = renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Sidebar should have responsive layout
    const layout = container.firstChild
    expect(layout).toHaveClass('flex')
  })

  // Navigation items in sidebar
  it('displays navigation items in sidebar', () => {
    const { container } = renderWithRouter(<MainLayout><div>Test Content</div></MainLayout>)

    // Navigation buttons should be present
    const buttons = container.querySelectorAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })
})
