import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatSessionCard } from '../../pages/ChatSessionsPage'

// Mock Lucide icons
vi.mock('lucide-react', () => ({
  MessageSquare: () => <div data-testid="message-square-icon" />,
  Edit: () => <div data-testid="edit-icon" />,
  Trash2: () => <div data-testid="trash-icon" />,
  Calendar: () => <div data-testid="calendar-icon" />,
  FileText: () => <div data-testid="file-text-icon" />,
}))

describe('ChatSessionCard Component', () => {
  const mockSession = {
    id: 'session-1',
    project_id: 'project-1',
    title: 'Test Chat Session',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    is_active: true,
    message_count: 5,
    last_message_preview: 'Hello, how are you?',
  }

  const mockProps = {
    session: mockSession,
    onEdit: vi.fn(),
    onDelete: vi.fn(),
    onSelect: vi.fn(),
  }

  let user: ReturnType<typeof userEvent.setup>

  beforeEach(() => {
    user = userEvent.setup()
    vi.clearAllMocks()
  })

  it('renders session information correctly', () => {
    render(<ChatSessionCard {...mockProps} />)

    expect(screen.getByText('Test Chat Session')).toBeInTheDocument()
    // Check that the message count appears (it appears in both header and footer)
    expect(screen.getAllByText('5 messages')).toHaveLength(2) // One in header, one in footer
    expect(screen.getByText('• Hello, how are you?')).toBeInTheDocument()
    expect(screen.getByText('01.01.2025')).toBeInTheDocument()
  })

  it('displays message square icon', () => {
    render(<ChatSessionCard {...mockProps} />)
    expect(screen.getByTestId('message-square-icon')).toBeInTheDocument()
  })

  it('shows edit and delete buttons with correct labels', () => {
    render(<ChatSessionCard {...mockProps} />)

    const editButton = screen.getByLabelText('Edit Test Chat Session')
    const deleteButton = screen.getByLabelText('Delete Test Chat Session')

    expect(editButton).toBeInTheDocument()
    expect(deleteButton).toBeInTheDocument()
    expect(screen.getByTestId('edit-icon')).toBeInTheDocument()
    expect(screen.getByTestId('trash-icon')).toBeInTheDocument()
  })

  it('calls onSelect when clicking the card', async () => {
    render(<ChatSessionCard {...mockProps} />)

    const card = screen.getByText('Test Chat Session').closest('.bg-slate-800')
    await user.click(card!)

    expect(mockProps.onSelect).toHaveBeenCalledWith(mockSession)
  })

  it('calls onEdit when clicking edit button', async () => {
    render(<ChatSessionCard {...mockProps} />)

    const editButton = screen.getByLabelText('Edit Test Chat Session')
    await user.click(editButton)

    expect(mockProps.onEdit).toHaveBeenCalledWith(mockSession)
  })

  it('calls onDelete when clicking delete button', async () => {
    render(<ChatSessionCard {...mockProps} />)

    const deleteButton = screen.getByLabelText('Delete Test Chat Session')
    await user.click(deleteButton)

    expect(mockProps.onDelete).toHaveBeenCalledWith(mockSession)
  })

  it('prevents card selection when clicking edit button', async () => {
    render(<ChatSessionCard {...mockProps} />)

    const editButton = screen.getByLabelText('Edit Test Chat Session')
    await user.click(editButton)

    expect(mockProps.onSelect).not.toHaveBeenCalled()
    expect(mockProps.onEdit).toHaveBeenCalledWith(mockSession)
  })

  it('prevents card selection when clicking delete button', async () => {
    render(<ChatSessionCard {...mockProps} />)

    const deleteButton = screen.getByLabelText('Delete Test Chat Session')
    await user.click(deleteButton)

    expect(mockProps.onSelect).not.toHaveBeenCalled()
    expect(mockProps.onDelete).toHaveBeenCalledWith(mockSession)
  })

  it('displays inactive status for inactive sessions', () => {
    const inactiveSession = { ...mockSession, is_active: false }
    render(<ChatSessionCard {...mockProps} session={inactiveSession} />)

    expect(screen.getByText('Inactive')).toBeInTheDocument()
  })

  it('handles long message previews correctly', () => {
    const longPreview = 'A'.repeat(200)
    const longPreviewSession = { ...mockSession, last_message_preview: longPreview }
    render(<ChatSessionCard {...mockProps} session={longPreviewSession} />)

    // The preview should be displayed (truncated by CSS or not, but present)
    expect(screen.getByText((content: string) => content.includes('A'.repeat(50)))).toBeInTheDocument()
  })

  it('displays zero messages correctly', () => {
    const emptySession = { ...mockSession, message_count: 0, last_message_preview: null }
    render(<ChatSessionCard {...mockProps} session={emptySession} />)

    // Check for "0 messages" in the header (should be the only one)
    const messageElements = screen.getAllByText(/0 messages/)
    expect(messageElements.length).toBeGreaterThan(0)
  })

  it('formats dates correctly', () => {
    const dateSession = { ...mockSession, created_at: '2025-12-25T15:30:00Z' }
    render(<ChatSessionCard {...mockProps} session={dateSession} />)

    expect(screen.getByText('25.12.2025')).toBeInTheDocument()
  })
})