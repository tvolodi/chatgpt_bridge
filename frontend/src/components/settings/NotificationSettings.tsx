import React from 'react'
import { UserPreferences } from '../../stores/settingsStore'

interface NotificationSettingsProps {
  preferences: UserPreferences
  onUpdate: (preferences: Partial<UserPreferences>) => void
}

export const NotificationSettings: React.FC<NotificationSettingsProps> = ({ preferences, onUpdate }) => {
  const updateNotifications = (updates: Partial<UserPreferences['notifications']>) => {
    onUpdate({
      notifications: { ...preferences.notifications, ...updates }
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-50 mb-4">Notification Settings</h2>
        <p className="text-slate-400 mb-6">Configure how and when you receive notifications.</p>
      </div>

      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-slate-200">Enable Notifications</h3>
            <p className="text-sm text-slate-400">Receive notifications from the application</p>
          </div>
          <input
            type="checkbox"
            checked={preferences.notifications.enabled}
            onChange={(e) => updateNotifications({ enabled: e.target.checked })}
            className="rounded border-slate-600 text-blue-600 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-slate-200">Sound Notifications</h3>
            <p className="text-sm text-slate-400">Play sound when receiving notifications</p>
          </div>
          <input
            type="checkbox"
            checked={preferences.notifications.soundEnabled}
            onChange={(e) => updateNotifications({ soundEnabled: e.target.checked })}
            disabled={!preferences.notifications.enabled}
            className="rounded border-slate-600 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-slate-200">Desktop Notifications</h3>
            <p className="text-sm text-slate-400">Show system notifications</p>
          </div>
          <input
            type="checkbox"
            checked={preferences.notifications.desktopNotifications}
            onChange={(e) => updateNotifications({ desktopNotifications: e.target.checked })}
            disabled={!preferences.notifications.enabled}
            className="rounded border-slate-600 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-slate-200">Email Notifications</h3>
            <p className="text-sm text-slate-400">Receive notifications via email</p>
          </div>
          <input
            type="checkbox"
            checked={preferences.notifications.emailNotifications}
            onChange={(e) => updateNotifications({ emailNotifications: e.target.checked })}
            disabled={!preferences.notifications.enabled}
            className="rounded border-slate-600 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
          />
        </div>
      </div>
    </div>
  )
}