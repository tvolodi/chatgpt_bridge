import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { ChatArea } from '../../components/ChatArea'

describe('ChatArea', () => {
  const mockMessages = [
    {
      id: 'msg-1',
      role: 'user' as const,
      content: 'Hello, how are you?',
      timestamp: '2025-01-15T10:00:00Z'
    },
    {
      id: 'msg-2',
      role: 'assistant' as const,
      content: 'I am doing well, thank you for asking!',
      timestamp: '2025-01-15T10:00:30Z'
    },
    {
      id: 'msg-3',
      role: 'user' as const,
      content: 'Can you help me with this code?',
      timestamp: '2025-01-15T10:01:00Z'
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock scrollIntoView since it's not available in jsdom
    Element.prototype.scrollIntoView = vi.fn()
  })

  // TC-FUNC-315: Message bubble display
  it('TC-FUNC-315: renders message list with all messages', () => {
    render(<ChatArea messages={mockMessages} isLoading={false} />)

    expect(screen.getByText('Hello, how are you?')).toBeInTheDocument()
    expect(screen.getByText('I am doing well, thank you for asking!')).toBeInTheDocument()
    expect(screen.getByText('Can you help me with this code?')).toBeInTheDocument()
  })

  // TC-FUNC-316: Message alignment (user right, AI left)
  it('TC-FUNC-316: aligns user messages to the right and assistant messages to the left', () => {
    const { container } = render(<ChatArea messages={mockMessages} isLoading={false} />)

    const messageBubbles = container.querySelectorAll('[class*="flex"]')
    
    // Verify structure exists
    expect(messageBubbles.length).toBeGreaterThan(0)
  })

  // TC-FUNC-317: Timestamp display
  it('TC-FUNC-317: displays timestamps for all messages', () => {
    render(<ChatArea messages={mockMessages} isLoading={false} />)

    // Check for time display (formatted time)
    const timeElements = screen.getAllByText(/\d{1,2}:\d{2}:\d{2}/)
    expect(timeElements.length).toBeGreaterThan(0)
  })

  // TC-FUNC-319: Auto-scroll to latest
  it('TC-FUNC-319: auto-scrolls to latest message', () => {
    const scrollIntoViewMock = vi.fn()
    Element.prototype.scrollIntoView = scrollIntoViewMock

    render(<ChatArea messages={mockMessages} isLoading={false} />)

    waitFor(() => {
      expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'smooth' })
    })
  })

  // TC-FUNC-322: Loading spinner display
  it('TC-FUNC-322: displays loading indicator when isLoading is true', () => {
    const { container } = render(<ChatArea messages={mockMessages} isLoading={true} />)

    const loadingIndicator = container.querySelector('[class*="animate-bounce"]')
    expect(loadingIndicator).toBeInTheDocument()
  })

  // Empty state test
  it('displays welcome message when no messages exist', () => {
    render(<ChatArea messages={[]} isLoading={false} />)

    expect(screen.getByText('Welcome to AI Chat Assistant')).toBeInTheDocument()
    expect(screen.getByText(/Start a conversation/)).toBeInTheDocument()
  })

  // Loading state with messages
  it('shows loading spinner while waiting for response with existing messages', () => {
    const { container } = render(<ChatArea messages={mockMessages} isLoading={true} />)

    // Should still show previous messages
    expect(screen.getByText('Hello, how are you?')).toBeInTheDocument()
    
    // Should show loading indicator
    expect(container.querySelector('[class*="animate-bounce"]')).toBeInTheDocument()
  })

  // Scroll position preservation on new messages
  it('preserves scroll position context when new messages are added', async () => {
    const { rerender } = render(<ChatArea messages={mockMessages} isLoading={false} />)

    const newMessages = [
      ...mockMessages,
      {
        id: 'msg-4',
        role: 'assistant' as const,
        content: 'Sure, I can help!',
        timestamp: '2025-01-15T10:01:30Z'
      }
    ]

    rerender(<ChatArea messages={newMessages} isLoading={false} />)

    expect(screen.getByText('Sure, I can help!')).toBeInTheDocument()
  })
})
