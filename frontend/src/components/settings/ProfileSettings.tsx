import React from 'react'
import { UserPreferences } from '../../stores/settingsStore'

interface ProfileSettingsProps {
  preferences: UserPreferences
  onUpdate: (preferences: Partial<UserPreferences>) => void
}

export const ProfileSettings: React.FC<ProfileSettingsProps> = ({ preferences, onUpdate }) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-50 mb-4">Profile Settings</h2>
        <p className="text-slate-400 mb-6">Manage your personal information and preferences.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-2">
          <label htmlFor="language-select" className="text-sm font-medium text-slate-200">Language</label>
          <select
            id="language-select"
            value={preferences.language}
            onChange={(e) => onUpdate({ language: e.target.value })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="zh">Chinese</option>
          </select>
        </div>

        <div className="space-y-2">
          <label htmlFor="timezone-select" className="text-sm font-medium text-slate-200">Timezone</label>
          <select
            id="timezone-select"
            value={preferences.timezone}
            onChange={(e) => onUpdate({ timezone: e.target.value })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="UTC">UTC</option>
            <option value="America/New_York">Eastern Time</option>
            <option value="America/Chicago">Central Time</option>
            <option value="America/Denver">Mountain Time</option>
            <option value="America/Los_Angeles">Pacific Time</option>
            <option value="Europe/London">London</option>
            <option value="Europe/Paris">Paris</option>
            <option value="Asia/Tokyo">Tokyo</option>
          </select>
        </div>

        <div className="space-y-2">
          <label htmlFor="date-format-select" className="text-sm font-medium text-slate-200">Date Format</label>
          <select
            id="date-format-select"
            value={preferences.dateFormat}
            onChange={(e) => onUpdate({ dateFormat: e.target.value })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
          </select>
        </div>

        <div className="space-y-2">
          <label htmlFor="time-format-select" className="text-sm font-medium text-slate-200">Time Format</label>
          <select
            id="time-format-select"
            value={preferences.timeFormat}
            onChange={(e) => onUpdate({ timeFormat: e.target.value as '12h' | '24h' })}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="12h">12 Hour</option>
            <option value="24h">24 Hour</option>
          </select>
        </div>
      </div>
    </div>
  )
}