import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Menu, X, Settings, User, Search, MessageSquare, FileText, Folder, Zap, ChevronDown, ChevronRight } from 'lucide-react'
import { useSettingsStore } from '../stores/settingsStore'
import { useProjectStore, ProjectTree } from '../stores/projectStore'
import { useChatSessionStore } from '../stores/chatSessionStore'

interface MainLayoutProps {
  children: React.ReactNode
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { uiState, updateUIState } = useSettingsStore()
  const { currentProject, projectTree, loadProjectTree, setCurrentProject } = useProjectStore()
  const { sessions, loadSessions, setCurrentSession } = useChatSessionStore()

  const sidebarCollapsed = uiState.sidebarCollapsed
  const [expandedProjects, setExpandedProjects] = useState<Set<string>>(new Set(['default']))

  useEffect(() => {
    loadProjectTree()
  }, [loadProjectTree])

  useEffect(() => {
    if (currentProject) {
      loadSessions(currentProject.id)
    }
  }, [currentProject, loadSessions])

  const navigationItems = [
    { id: 'chat', label: 'Chat', icon: MessageSquare, path: '/' },
    { id: 'search', label: 'Search', icon: Search, path: '/search' },
    { id: 'files', label: 'Files', icon: FileText, path: '/files' },
    { id: 'chat-sessions', label: 'Chat Sessions', icon: MessageSquare, path: '/chat-sessions' },
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

  const toggleProjectExpansion = (projectId: string) => {
    const newExpanded = new Set(expandedProjects)
    if (newExpanded.has(projectId)) {
      newExpanded.delete(projectId)
    } else {
      newExpanded.add(projectId)
    }
    setExpandedProjects(newExpanded)
  }

  const handleProjectSelect = (project: any) => {
    setCurrentProject(project)
    // Navigate to chat or project workspace
    navigate('/')
  }

  const renderProjectTree = (projects: ProjectTree[], level = 0) => {
    return projects.map((item) => {
      const isExpanded = expandedProjects.has(item.project.id)
      const hasChildren = item.children && item.children.length > 0
      const isSelected = currentProject?.id === item.project.id

      return (
        <div key={item.project.id}>
          <button
            onClick={() => {
              if (hasChildren) {
                toggleProjectExpansion(item.project.id)
              } else {
                handleProjectSelect(item.project)
              }
            }}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-left ${
              isSelected
                ? 'bg-blue-600 text-white'
                : 'hover:bg-slate-800 text-slate-300 hover:text-white'
            } ${level > 0 ? 'ml-4' : ''}`}
            style={{ paddingLeft: `${12 + level * 16}px` }}
          >
            {hasChildren ? (
              isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
            ) : (
              <div className="w-4" />
            )}
            <Folder size={16} />
            {!sidebarCollapsed && (
              <span className="truncate text-sm">{item.project.name}</span>
            )}
          </button>

          {hasChildren && isExpanded && (
            <div>
              {renderProjectTree(item.children, level + 1)}
            </div>
          )}
        </div>
      )
    })
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

        {/* Projects Section */}
        {!sidebarCollapsed && (
          <div className="px-4 pb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
                Projects
              </h3>
              <button
                onClick={() => handleNavigation('/projects')}
                className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800"
              >
                <Settings size={14} />
              </button>
            </div>
            <div className="space-y-1 max-h-64 overflow-y-auto">
              {projectTree.length > 0 ? (
                renderProjectTree(projectTree)
              ) : (
                <div className="text-xs text-slate-500 px-3 py-2">
                  No projects
                </div>
              )}
            </div>

            {/* Chat Sessions Section */}
            {currentProject && (
              <>
                <div className="flex items-center justify-between mt-4 mb-2">
                  <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
                    Chat Sessions
                  </h3>
                  <button
                    onClick={() => handleNavigation('/chat-sessions')}
                    className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800"
                  >
                    <Settings size={14} />
                  </button>
                </div>
                <div className="space-y-1 max-h-64 overflow-y-auto">
                  {sessions.length > 0 ? (
                    sessions.slice(0, 10).map((session) => (
                      <button
                        key={session.id}
                        onClick={() => {
                          setCurrentSession(session)
                          handleNavigation('/')
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-left hover:bg-slate-800 text-slate-300 hover:text-white"
                      >
                        <MessageSquare size={16} />
                        <div className="flex-1 min-w-0">
                          <span className="truncate text-sm block">{session.title}</span>
                          <span className="text-xs text-slate-500">{session.message_count} messages</span>
                        </div>
                      </button>
                    ))
                  ) : (
                    <div className="text-xs text-slate-500 px-3 py-2">
                      No chat sessions
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}

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
              <div className="flex items-center gap-2 mt-1">
                <p className="text-sm text-slate-400">
                  {activeView === 'chat' && (currentProject ? `Working on ${currentProject.name}` : 'Start a conversation with your AI assistant')}
                  {activeView === 'search' && 'Search through your conversations and files'}
                  {activeView === 'files' && 'Browse and manage your workspace files'}
                  {activeView === 'chat-sessions' && (currentProject ? `Manage chat sessions in ${currentProject.name}` : 'Select a project to manage chat sessions')}
                  {activeView === 'projects' && 'Organize your work into projects'}
                  {activeView === 'settings' && 'Configure your preferences and settings'}
                </p>
                {currentProject && activeView === 'chat' && (
                  <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                    {currentProject.name}
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Quick Actions */}
              <div className="flex items-center gap-2">
                <button className="p-2 rounded-lg hover:bg-slate-800 transition-colors">
                  <Zap size={20} className="text-yellow-400" />
                </button>
                <button 
                  onClick={() => handleNavigation('/settings')}
                  className="p-2 rounded-lg hover:bg-slate-800 transition-colors"
                >
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