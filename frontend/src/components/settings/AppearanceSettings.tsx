import React from 'react'
import { UserPreferences } from '../../stores/settingsStore'

interface AppearanceSettingsProps {
  preferences: UserPreferences
  uiState: any
  onUpdatePreferences: (preferences: Partial<UserPreferences>) => void
  onUpdateUI: (uiState: any) => void
}

export const AppearanceSettings: React.FC<AppearanceSettingsProps> = ({
  preferences,
  uiState,
  onUpdatePreferences,
  onUpdateUI
}) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-50 mb-4">Appearance Settings</h2>
        <p className="text-slate-400 mb-6">Customize the look and feel of your interface.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <label htmlFor="theme-select" className="text-sm font-medium text-slate-200">Theme</label>
          <select
            id="theme-select"
            value={preferences.theme}
            onChange={(e) => onUpdatePreferences({ theme: e.target.value as 'light' | 'dark' | 'system' })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-200">Layout Density</label>
          <select
            value={preferences.layout}
            onChange={(e) => onUpdatePreferences({ layout: e.target.value as 'compact' | 'comfortable' | 'spacious' })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="compact">Compact</option>
            <option value="comfortable">Comfortable</option>
            <option value="spacious">Spacious</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-medium text-slate-200">UI State</h3>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="sidebar-collapsed"
            checked={uiState.sidebarCollapsed || false}
            onChange={(e) => onUpdateUI({ sidebarCollapsed: e.target.checked })}
            className="rounded border-slate-600 text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="sidebar-collapsed" className="text-sm text-slate-200">
            Start with sidebar collapsed
          </label>
        </div>
      </div>
    </div>
  )
}