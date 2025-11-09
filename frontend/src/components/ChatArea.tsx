import React, { useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'

interface Message {
  role: 'user' | 'assistant'
  content: string
  id: string
  timestamp: string
}

interface ChatAreaProps {
  messages: Message[]
  isLoading?: boolean
}

export const ChatArea: React.FC<ChatAreaProps> = ({ messages, isLoading = false }) => {
  const endOfMessagesRef = useRef<HTMLDivElement>(null)
  
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-slate-400">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">Welcome to AI Chat Assistant</h2>
            <p>Start a conversation to get began</p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-slate-800 px-4 py-2 rounded-lg">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </>
      )}
    </div>
  )
}

export default ChatArea
