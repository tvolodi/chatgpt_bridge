import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Menu, X, Settings, User, Search, MessageSquare, FileText, Folder, Zap } from 'lucide-react'
import { useSettingsStore } from '../stores/settingsStore'

interface MainLayoutProps {
  children: React.ReactNode
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { uiState, updateUIState } = useSettingsStore()

  const sidebarCollapsed = uiState.sidebarCollapsed

  const navigationItems = [
    { id: 'chat', label: 'Chat', icon: MessageSquare, path: '/' },
    { id: 'search', label: 'Search', icon: Search, path: '/search' },
    { id: 'files', label: 'Files', icon: FileText, path: '/files' },
    { id: 'projects', label: 'Projects', icon: Folder, path: '/projects' },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/settings' },
  ]

  const getActiveView = () => {
    const currentItem = navigationItems.find(item => item.path === location.pathname)
    return currentItem?.id || 'chat'
  }

  const activeView = getActiveView()

  const toggleSidebar = () => {
    updateUIState({ sidebarCollapsed: !sidebarCollapsed })
  }

  const handleNavigation = (path: string) => {
    navigate(path)
  }

  return (
    <div className="flex h-screen bg-slate-950 text-slate-50">
      {/* Sidebar */}
      <div className={`bg-slate-900 border-r border-slate-800 transition-all duration-300 ${
        sidebarCollapsed ? 'w-16' : 'w-64'
      }`}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          {!sidebarCollapsed && (
            <h1 className="text-lg font-bold text-blue-400">AI Assistant</h1>
          )}
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-slate-800 transition-colors"
          >
            {sidebarCollapsed ? <Menu size={20} /> : <X size={20} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const isActive = activeView === item.id

            return (
              <button
                key={item.id}
                onClick={() => handleNavigation(item.path)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'hover:bg-slate-800 text-slate-300 hover:text-white'
                }`}
              >
                <Icon size={20} />
                {!sidebarCollapsed && <span>{item.label}</span>}
              </button>
            )
          })}
        </nav>

        {/* User Section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-800">
          <div className={`flex items-center gap-3 ${sidebarCollapsed ? 'justify-center' : ''}`}>
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <User size={16} />
            </div>
            {!sidebarCollapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">User</p>
                <p className="text-xs text-slate-400 truncate">Online</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-slate-900 border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold">
                {navigationItems.find(item => item.id === activeView)?.label || 'Dashboard'}
              </h2>
              <p className="text-sm text-slate-400">
                {activeView === 'chat' && 'Start a conversation with your AI assistant'}
                {activeView === 'search' && 'Search through your conversations and files'}
                {activeView === 'files' && 'Browse and manage your workspace files'}
                {activeView === 'projects' && 'Organize your work into projects'}
                {activeView === 'settings' && 'Configure your preferences and settings'}
              </p>
            </div>

            <div className="flex items-center gap-4">
              {/* Quick Actions */}
              <div className="flex items-center gap-2">
                <button className="p-2 rounded-lg hover:bg-slate-800 transition-colors">
                  <Zap size={20} className="text-yellow-400" />
                </button>
                <button className="p-2 rounded-lg hover:bg-slate-800 transition-colors">
                  <Settings size={20} />
                </button>
              </div>

              {/* User Menu */}
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <User size={16} />
                </div>
                <span className="text-sm font-medium">User</span>
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  )
}

export default MainLayout