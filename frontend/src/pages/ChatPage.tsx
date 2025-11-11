import React, { useState, useEffect } from 'react'
import ChatArea from '../components/ChatArea'
import ChatInput from '../components/ChatInput'
import { ProviderSelector } from '../components/ProviderSelector'
import { useChatStore } from '../stores/chatStore'
import { useUserStateStore } from '../stores/userStateStore'
import { useProjectStore } from '../stores/projectStore'
import { useChatSessionStore } from '../stores/chatSessionStore'
import { useProvidersStore } from '../stores/providersStore'
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
  const { addRecentActivity, updateSession, session } = useUserStateStore()
  const { currentProject } = useProjectStore()
  const { currentSession, setCurrentSession, getSessionWithMessages, addMessage: addSessionMessage } = useChatSessionStore()
  const { getActiveProviders } = useProvidersStore()

  // Initialize default provider
  useEffect(() => {
    const activeProviders = getActiveProviders();
    if (activeProviders.length > 0 && !session?.selectedProviderId) {
      updateSession({ selectedProviderId: activeProviders[0].id });
    }
  }, [getActiveProviders, session?.selectedProviderId, updateSession]);

  const handleProviderChange = (providerId: string) => {
    updateSession({ selectedProviderId: providerId });
  };

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
      // Get the selected provider and use its first available model
      const activeProviders = getActiveProviders();
      const selectedProvider = activeProviders.find(p => p.id === session?.selectedProviderId) || activeProviders[0];

      if (!selectedProvider) {
        const errorMessage: Message = {
          role: 'assistant',
          content: 'No AI provider available. Please configure a provider in Settings.',
          id: `msg-${Date.now()}-error`,
          timestamp: new Date().toISOString(),
        };
        addMessage(errorMessage);
        setIsLoading(false);
        return;
      }

      // Use the first available model from the selected provider
      const selectedModel = selectedProvider.models?.[0]?.name;

      // TODO: Replace with actual chat API call
      // const response = await chatAPI.sendMessage(currentSession.id, text, selectedModel);

      // For now, simulate response with provider info
      setTimeout(() => {
        const assistantMessage: Message = {
          role: 'assistant',
          content: `This is a response from ${selectedProvider.displayName} using model ${selectedModel || 'default'}. AI integration to be implemented.`,
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
          title: `Received AI response from ${selectedProvider.displayName} in ${currentProject?.name || 'Default Project'}`,
          timestamp: new Date(),
          metadata: {
            response_length: assistantMessage.content.length,
            project_id: currentProject?.id,
            project_name: currentProject?.name,
            provider: selectedProvider.displayName,
            model: selectedModel
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
      {/* Chat header with provider selector */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-slate-200">Chat</h2>
            <ProviderSelector
              selectedProviderId={session?.selectedProviderId}
              onProviderChange={handleProviderChange}
            />
          </div>
        </div>
      </div>

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
