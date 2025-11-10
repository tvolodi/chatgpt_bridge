import React, { useState, useEffect } from 'react'
import ChatArea from '../components/ChatArea'
import ChatInput from '../components/ChatInput'
import { useChatStore } from '../stores/chatStore'
import { useUserStateStore } from '../stores/userStateStore'
import { useProjectStore } from '../stores/projectStore'
import { useChatSessionStore } from '../stores/chatSessionStore'
import { chatSessionsAPI } from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  id: string
  timestamp: string
}

export const ChatPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false)
  const { messages, addMessage, setMessages, clearChat } = useChatStore()
  const { addRecentActivity, updateSession } = useUserStateStore()
  const { currentProject } = useProjectStore()
  const { currentSession, setCurrentSession, getSessionWithMessages, addMessage: addSessionMessage } = useChatSessionStore()

  // Clear chat when project changes
  useEffect(() => {
    clearChat()
    setCurrentSession(null)
  }, [currentProject?.id, clearChat, setCurrentSession])

  // Initialize or load chat session
  useEffect(() => {
    const initChatSession = async () => {
      if (!currentProject) return

      try {
        // If we have a current session, load its messages
        if (currentSession) {
          const sessionWithMessages = await getSessionWithMessages(currentSession.id)
          if (sessionWithMessages) {
            setMessages(sessionWithMessages.messages.map(msg => ({
              role: msg.role as 'user' | 'assistant',
              content: msg.content,
              id: msg.id,
              timestamp: msg.timestamp
            })))
          }
        } else {
          // Create a new session if none selected
          const newSession = await chatSessionsAPI.createSession({
            project_id: currentProject.id,
            title: `Chat ${new Date().toLocaleString()}`,
            description: 'New chat session'
          })

          setCurrentSession(newSession.data)

          // Update user state with session
          updateSession({
            sessionId: newSession.data.id,
            lastActivity: new Date(),
            projectId: currentProject.id
          })

          // Add recent activity
          addRecentActivity({
            action: 'start',
            resourceType: 'session',
            resourceId: newSession.data.id,
            title: `Started new chat session in ${currentProject.name}`,
            timestamp: new Date(),
            metadata: { 
              session_type: 'chat',
              project_id: currentProject.id,
              project_name: currentProject.name
            }
          })
        }
      } catch (error) {
        console.error('Failed to initialize chat session:', error)
      }
    }

    initChatSession()
  }, [currentSession, currentProject, setCurrentSession, getSessionWithMessages, setMessages, updateSession, addRecentActivity])

  const handleSendMessage = async (text: string) => {
    if (!currentSession) return

    // Add user message immediately
    const userMessage: Message = {
      role: 'user',
      content: text,
      id: `msg-${Date.now()}`,
      timestamp: new Date().toISOString(),
    }
    addMessage(userMessage)

    // Add message to session
    try {
      await addSessionMessage(currentSession.id, {
        role: 'user',
        content: text
      })
    } catch (error) {
      console.error('Failed to save user message:', error)
    }

    setIsLoading(true)

    // Update session activity
    updateSession({
      lastActivity: new Date(),
      draftContent: undefined,
      projectId: currentProject?.id
    })

    // Add recent activity
    addRecentActivity({
      action: 'send',
      resourceType: 'message',
      resourceId: userMessage.id,
      title: `Sent message in ${currentProject?.name || 'Default Project'}`,
      timestamp: new Date(),
      metadata: { 
        message_length: text.length,
        project_id: currentProject?.id,
        project_name: currentProject?.name
      }
    })

    try {
      // TODO: Implement AI response via chat API
      // For now, just simulate a response
      setTimeout(() => {
        const assistantMessage: Message = {
          role: 'assistant',
          content: 'This is a placeholder response. AI integration to be implemented.',
          id: `msg-${Date.now()}-resp`,
          timestamp: new Date().toISOString(),
        }
        addMessage(assistantMessage)

        // Add assistant message to session
        addSessionMessage(currentSession.id, {
          role: 'assistant',
          content: assistantMessage.content
        }).catch(error => console.error('Failed to save assistant message:', error))

        // Add assistant response activity
        addRecentActivity({
          action: 'receive',
          resourceType: 'message',
          resourceId: assistantMessage.id,
          title: `Received AI response in ${currentProject?.name || 'Default Project'}`,
          timestamp: new Date(),
          metadata: { 
            response_length: assistantMessage.content.length,
            project_id: currentProject?.id,
            project_name: currentProject?.name
          }
        })
      }, 1000)
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
