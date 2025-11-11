import React, { useState, useEffect } from 'react'
import { Save, Download, Upload, RotateCcw, User, Palette, Bell, Monitor, Globe, Settings as SettingsIcon } from 'lucide-react'
import { useSettingsStore, UserPreferences } from '../stores/settingsStore'
import { settingsAPI } from '../services/api'
import { ProfileSettings } from '../components/settings/ProfileSettings'
import { AppearanceSettings } from '../components/settings/AppearanceSettings'
import { NotificationSettings } from '../components/settings/NotificationSettings'
import { SystemSettings } from '../components/settings/SystemSettings'
import { AccountSettings } from '../components/settings/AccountSettings'
import { ProviderManagementPage } from './ProviderManagementPage'

type SettingsTab = 'profile' | 'appearance' | 'notifications' | 'system' | 'account' | 'providers'

export const SettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile')
  const [isLoading, setIsLoading] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')

  const { preferences, uiState, updatePreferences, updateUIState } = useSettingsStore()

  // Load settings from backend on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setIsLoading(true)
        const response = await settingsAPI.getSettings()
        // Map backend response to frontend structure
        const backendSettings = response.data
        updatePreferences({
          theme: backendSettings.user_preferences?.theme || 'system',
          layout: 'comfortable', // Map from message_display_mode or default
          language: backendSettings.user_preferences?.language || 'en',
          timezone: 'UTC', // Not in backend, use default
          dateFormat: 'YYYY-MM-DD', // Not in backend, use default
          timeFormat: '24h', // Not in backend, use default
          notifications: {
            enabled: backendSettings.user_preferences?.sound_enabled || true,
            soundEnabled: backendSettings.user_preferences?.sound_enabled || true,
            desktopNotifications: true, // Not in backend, use default
            emailNotifications: false, // Not in backend, use default
            notificationTypes: {}
          },
          autoSave: backendSettings.user_preferences?.auto_save || true,
          autoSaveInterval: backendSettings.user_preferences?.auto_save_interval || 30,
          keyboardShortcuts: {}
        })
        updateUIState({
          sidebarCollapsed: false, // Not in backend, use default
          expandedSections: []
        })
      } catch (error) {
        console.error('Failed to load settings:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadSettings()
  }, [])

  const handleSaveSettings = async () => {
    try {
      setSaveStatus('saving')
      // Map frontend structure to backend categories
      const userPreferencesData = {
        theme: preferences.theme,
        language: preferences.language,
        sound_enabled: preferences.notifications.soundEnabled,
        auto_save: preferences.autoSave,
        auto_save_interval: preferences.autoSaveInterval
      }
      
      await settingsAPI.updateSettingsByCategory('user_preferences', userPreferencesData)
      setSaveStatus('saved')
      setTimeout(() => setSaveStatus('idle'), 2000)
    } catch (error) {
      console.error('Failed to save settings:', error)
      setSaveStatus('error')
      setTimeout(() => setSaveStatus('idle'), 3000)
    }
  }

  const handleExportSettings = async () => {
    try {
      const response = await settingsAPI.exportSettings()
      const dataStr = JSON.stringify(response.data, null, 2)
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)

      const exportFileDefaultName = `ai-chat-settings-${new Date().toISOString().split('T')[0]}.json`

      const linkElement = document.createElement('a')
      linkElement.setAttribute('href', dataUri)
      linkElement.setAttribute('download', exportFileDefaultName)
      linkElement.click()
    } catch (error) {
      console.error('Failed to export settings:', error)
    }
  }

  const handleImportSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        const importedSettings = JSON.parse(e.target?.result as string)

        if (importedSettings.preferences) {
          updatePreferences(importedSettings.preferences)
        }
        if (importedSettings.ui_state) {
          updateUIState(importedSettings.ui_state)
        }

        // Save to backend
        await settingsAPI.updateSettings({
          preferences: importedSettings.preferences || preferences,
          ui_state: importedSettings.ui_state || uiState
        })

        alert('Settings imported successfully!')
      } catch (error) {
        console.error('Failed to import settings:', error)
        alert('Failed to import settings. Please check the file format.')
      }
    }
    reader.readAsText(file)
  }

  const handleResetToDefaults = async () => {
    if (!confirm('Are you sure you want to reset all settings to defaults? This action cannot be undone.')) {
      return
    }

    try {
      // Reset local store
      updatePreferences({
        theme: 'system',
        layout: 'comfortable',
        language: 'en',
        timezone: 'UTC',
        dateFormat: 'YYYY-MM-DD',
        timeFormat: '24h',
        notifications: {
          enabled: true,
          soundEnabled: true,
          desktopNotifications: true,
          emailNotifications: false,
          notificationTypes: {}
        },
        autoSave: true,
        autoSaveInterval: 30,
        keyboardShortcuts: {}
      })

      updateUIState({
        sidebarCollapsed: false,
        expandedSections: []
      })

      // Save to backend
      await handleSaveSettings()

      alert('Settings reset to defaults successfully!')
    } catch (error) {
      console.error('Failed to reset settings:', error)
      alert('Failed to reset settings.')
    }
  }

  const tabs = [
    { id: 'profile' as SettingsTab, label: 'Profile', icon: User },
    { id: 'appearance' as SettingsTab, label: 'Appearance', icon: Palette },
    { id: 'notifications' as SettingsTab, label: 'Notifications', icon: Bell },
    { id: 'providers' as SettingsTab, label: 'Providers', icon: SettingsIcon },
    { id: 'system' as SettingsTab, label: 'System', icon: Monitor },
    { id: 'account' as SettingsTab, label: 'Account', icon: Globe }
  ]

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-50 mb-2">Settings</h1>
        <p className="text-slate-400">Customize your AI Chat Assistant experience</p>
      </div>

      <div className="flex gap-8">
        {/* Sidebar */}
        <div className="w-64 flex-shrink-0">
          <nav className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white'
                      : 'hover:bg-slate-800 text-slate-300 hover:text-white'
                  }`}
                >
                  <Icon size={20} />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </nav>

          {/* Action Buttons */}
          <div className="mt-8 space-y-3">
            <button
              onClick={handleSaveSettings}
              disabled={saveStatus === 'saving'}
              className="w-full flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              <Save size={16} />
              {saveStatus === 'saving' ? 'Saving...' : saveStatus === 'saved' ? 'Saved!' : saveStatus === 'error' ? 'Error!' : 'Save Settings'}
            </button>

            <button
              onClick={handleExportSettings}
              className="w-full flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
            >
              <Download size={16} />
              Export Settings
            </button>

            <label className="w-full flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors cursor-pointer">
              <Upload size={16} />
              Import Settings
              <input
                type="file"
                accept=".json"
                onChange={handleImportSettings}
                className="hidden"
              />
            </label>

            <button
              onClick={handleResetToDefaults}
              className="w-full flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              <RotateCcw size={16} />
              Reset to Defaults
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="bg-slate-800 rounded-lg p-6">
            {activeTab === 'profile' && <ProfileSettings preferences={preferences} onUpdate={updatePreferences} />}
            {activeTab === 'appearance' && <AppearanceSettings preferences={preferences} uiState={uiState} onUpdatePreferences={updatePreferences} onUpdateUI={updateUIState} />}
            {activeTab === 'notifications' && <NotificationSettings preferences={preferences} onUpdate={updatePreferences} />}
            {activeTab === 'providers' && <ProviderManagementPage />}
            {activeTab === 'system' && <SystemSettings preferences={preferences} onUpdate={updatePreferences} />}
            {activeTab === 'account' && <AccountSettings />}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage