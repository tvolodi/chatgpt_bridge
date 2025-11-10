import React from 'react'
import { UserPreferences } from '../../stores/settingsStore'

interface SystemSettingsProps {
  preferences: UserPreferences
  onUpdate: (preferences: Partial<UserPreferences>) => void
}

export const SystemSettings: React.FC<SystemSettingsProps> = ({ preferences, onUpdate }) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-50 mb-4">System Settings</h2>
        <p className="text-slate-400 mb-6">Configure system-wide preferences and behavior.</p>
      </div>

      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <label htmlFor="auto-save-checkbox" className="text-sm font-medium text-slate-200">Auto Save</label>
            <p className="text-sm text-slate-400">Automatically save your work</p>
          </div>
          <input
            id="auto-save-checkbox"
            type="checkbox"
            checked={preferences.autoSave}
            onChange={(e) => onUpdate({ autoSave: e.target.checked })}
            className="rounded border-slate-600 text-blue-600 focus:ring-blue-500"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-200">Auto Save Interval (seconds)</label>
          <input
            type="number"
            value={preferences.autoSaveInterval}
            onChange={(e) => onUpdate({ autoSaveInterval: parseInt(e.target.value) || 30 })}
            min="10"
            max="300"
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-200">Keyboard Shortcuts</label>
          <div className="text-sm text-slate-400 mb-2">
            Configure custom keyboard shortcuts (JSON format)
          </div>
          <textarea
            value={JSON.stringify(preferences.keyboardShortcuts, null, 2)}
            onChange={(e) => {
              try {
                const shortcuts = JSON.parse(e.target.value)
                onUpdate({ keyboardShortcuts: shortcuts })
              } catch (error) {
                // Invalid JSON, ignore
              }
            }}
            rows={6}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-slate-50 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder='{"save": "Ctrl+S", "new": "Ctrl+N"}'
          />
        </div>
      </div>
    </div>
  )
}