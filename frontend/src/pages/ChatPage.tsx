import React, { useState, useEffect } from 'react'
import ChatArea from '../components/ChatArea'
import ChatInput from '../components/ChatInput'
import { useChatStore } from '../stores/chatStore'
import { useUserStateStore } from '../stores/userStateStore'
import { chatAPI } from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  id: string
  timestamp: string
}

export const ChatPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const { messages, addMessage, setMessages, sessionId, setSessionId } = useChatStore()
  const { addRecentActivity, updateSession } = useUserStateStore()

  // Initialize chat session
  useEffect(() => {
    const initChat = async () => {
      try {
        const response = await chatAPI.createSession()
        setSessionId(response.data.session_id)

        // Update user state with session
        updateSession({
          sessionId: response.data.session_id,
          lastActivity: new Date()
        })

        // Add recent activity
        addRecentActivity({
          action: 'start',
          resourceType: 'session',
          resourceId: response.data.session_id,
          title: 'Started new chat session',
          timestamp: new Date(),
          metadata: { session_type: 'chat' }
        })
      } catch (error) {
        console.error('Failed to create session:', error)
      }
    }

    if (!sessionId) {
      initChat()
    }
  }, [sessionId, setSessionId, updateSession, addRecentActivity])

  const handleSendMessage = async (text: string) => {
    if (!sessionId) return

    // Add user message immediately
    const userMessage: Message = {
      role: 'user',
      content: text,
      id: `msg-${Date.now()}`,
      timestamp: new Date().toISOString(),
    }
    addMessage(userMessage)
    setIsLoading(true)

    // Update session activity
    updateSession({
      lastActivity: new Date(),
      draftContent: undefined
    })

    // Add recent activity
    addRecentActivity({
      action: 'send',
      resourceType: 'message',
      resourceId: userMessage.id,
      title: 'Sent message',
      timestamp: new Date(),
      metadata: { message_length: text.length }
    })

    try {
      const response = await chatAPI.sendMessage(sessionId, text)

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.message,
        id: `msg-${Date.now()}-resp`,
        timestamp: new Date().toISOString(),
      }
      addMessage(assistantMessage)

      // Add assistant response activity
      addRecentActivity({
        action: 'receive',
        resourceType: 'message',
        resourceId: assistantMessage.id,
        title: 'Received AI response',
        timestamp: new Date(),
        metadata: { response_length: response.data.message.length }
      })
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        id: `msg-${Date.now()}-error`,
        timestamp: new Date().toISOString(),
      }
      addMessage(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="flex flex-col h-full">
      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        <ChatArea messages={messages} isLoading={isLoading} />
        
        {/* Input area */}
        <div className="bg-slate-900 border-t border-slate-800 p-4">
          <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  )
}

export default ChatPage
