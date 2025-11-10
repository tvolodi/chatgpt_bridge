import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import MainLayout from './components/MainLayout'
import ChatPage from './pages/ChatPage'
import SearchPage from './pages/SearchPage'
import FilesPage from './pages/FilesPage'
import ProjectsPage from './pages/ProjectsPage'
import ChatSessionsPage from './pages/ChatSessionsPage'
import SettingsPage from './pages/SettingsPage'
import './App.css'

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/files" element={<FilesPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/chat-sessions" element={<ChatSessionsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </MainLayout>
    </Router>
  )
}

export default App
