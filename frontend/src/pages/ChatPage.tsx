import React, { useState, useEffect } from 'react'
import ChatArea from '../components/ChatArea'
import ChatInput from '../components/ChatInput'
import { useChatStore } from '../stores/chatStore'
import { chatAPI } from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  id: string
  timestamp: string
}

export const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  // Initialize chat session
  useEffect(() => {
    const initChat = async () => {
      try {
        const response = await chatAPI.createSession()
        // Store session ID (in real app, would use store)
        localStorage.setItem('sessionId', response.data.session_id)
      } catch (error) {
        console.error('Failed to create session:', error)
      }
    }
    
    initChat()
  }, [])
  
  const handleSendMessage = async (text: string) => {
    const sessionId = localStorage.getItem('sessionId') || 'default'
    
    // Add user message immediately
    const userMessage: Message = {
      role: 'user',
      content: text,
      id: `msg-${Date.now()}`,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    
    try {
      const response = await chatAPI.sendMessage(sessionId, text)
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.message,
        id: `msg-${Date.now()}-resp`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        id: `msg-${Date.now()}-error`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="flex flex-col h-screen bg-slate-950">
      {/* Header */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 py-4 shadow-sm">
        <h1 className="text-xl font-bold text-slate-50">AI Chat Assistant</h1>
        <p className="text-sm text-slate-400">Your personal AI workspace companion</p>
      </div>
      
      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Chat area */}
        <div className="flex-1 flex flex-col">
          <ChatArea messages={messages} isLoading={isLoading} />
          
          {/* Input area */}
          <div className="bg-slate-900 border-t border-slate-800 p-4">
            <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatPage
