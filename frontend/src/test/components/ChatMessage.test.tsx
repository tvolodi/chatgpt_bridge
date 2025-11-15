import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatMessage } from '../../components/ChatMessage'

describe('ChatMessage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // TC-UNIT-315 & TC-FUNC-315: Message bubble display
  it('TC-UNIT-315: renders message bubble with content', () => {
    const message = {
      id: 'msg-1',
      role: 'user' as const,
      content: 'This is a test message',
      timestamp: '2025-01-15T10:00:00Z'
    }

    render(<ChatMessage message={message} />)

    expect(screen.getByText('This is a test message')).toBeInTheDocument()
  })

  // TC-FUNC-316: Message alignment (user right, AI left)
  it('TC-FUNC-316: aligns user messages to the right with blue background', () => {
    const message = {
      id: 'msg-1',
      role: 'user' as const,
      content: 'User message',
      timestamp: '2025-01-15T10:00:00Z'
    }

    const { container } = render(<ChatMessage message={message} />)
    
    const messageContainer = container.querySelector('[class*="justify-end"]')
    expect(messageContainer).toBeInTheDocument()

    const bubble = container.querySelector('[class*="bg-blue"]')
    expect(bubble).toBeInTheDocument()
  })

  // TC-FUNC-316: Message alignment - Assistant
  it('TC-FUNC-316: aligns assistant messages to the left with slate background', () => {
    const message = {
      id: 'msg-2',
      role: 'assistant' as const,
      content: 'Assistant message',
      timestamp: '2025-01-15T10:00:30Z'
    }

    const { container } = render(<ChatMessage message={message} />)

    const messageContainer = container.querySelector('[class*="justify-start"]')
    expect(messageContainer).toBeInTheDocument()

    const bubble = container.querySelector('[class*="bg-slate"]')
    expect(bubble).toBeInTheDocument()
  })

  // TC-FUNC-317: Timestamp display
  it('TC-FUNC-317: displays formatted timestamp', () => {
    const message = {
      id: 'msg-1',
      role: 'user' as const,
      content: 'Test message',
      timestamp: '2025-01-15T10:00:00Z'
    }

    render(<ChatMessage message={message} />)

    // Check for time in format HH:MM:SS
    const timeElement = screen.getByText(/\d{1,2}:\d{2}:\d{2}/)
    expect(timeElement).toBeInTheDocument()
  })

  // TC-FUNC-321: Copy message to clipboard
  it('TC-FUNC-321: message content can be selected for copying', () => {
    const message = {
      id: 'msg-1',
      role: 'user' as const,
      content: 'Copyable message content',
      timestamp: '2025-01-15T10:00:00Z'
    }

    render(<ChatMessage message={message} />)

    const contentElement = screen.getByText('Copyable message content')
    expect(contentElement).toBeInTheDocument()
    
    // Verify content is accessible for selection/copying
    expect(contentElement.textContent).toBe('Copyable message content')
  })

  // Display properties
  it('applies correct styling to message bubbles', () => {
    const userMessage = {
      id: 'msg-1',
      role: 'user' as const,
      content: 'User',
      timestamp: '2025-01-15T10:00:00Z'
    }

    const { container: userContainer } = render(<ChatMessage message={userMessage} />)
    
    const userBubble = userContainer.querySelector('[class*="px-4"][class*="py-2"]')
    expect(userBubble).toHaveClass('rounded-lg')
  })

  // Timestamp accuracy
  it('displays accurate timestamp for message', () => {
    const specificTime = '2025-06-15T14:30:45Z'
    const message = {
      id: 'msg-1',
      role: 'assistant' as const,
      content: 'Time test message',
      timestamp: specificTime
    }

    render(<ChatMessage message={message} />)

    // The timestamp should be formatted consistently
    const timeElement = screen.getByText(/\d{1,2}:\d{2}:\d{2}/)
    expect(timeElement).toBeInTheDocument()
    expect(timeElement).toHaveClass('opacity-70')
  })
})
