import React from 'react'

export const AccountSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-50 mb-4">Account Settings</h2>
        <p className="text-slate-400 mb-6">Manage your account and privacy settings.</p>
      </div>

      <div className="space-y-6">
        <div className="bg-slate-700 rounded-lg p-4">
          <h3 className="text-lg font-medium text-slate-200 mb-2">Account Information</h3>
          <p className="text-slate-400 text-sm">
            Account management features will be available in a future update.
          </p>
        </div>

        <div className="bg-slate-700 rounded-lg p-4">
          <h3 className="text-lg font-medium text-slate-200 mb-2">Privacy & Security</h3>
          <p className="text-slate-400 text-sm">
            Privacy and security settings will be available in a future update.
          </p>
        </div>

        <div className="bg-slate-700 rounded-lg p-4">
          <h3 className="text-lg font-medium text-slate-200 mb-2">Data Management</h3>
          <p className="text-slate-400 text-sm">
            Data export and deletion options will be available in a future update.
          </p>
        </div>
      </div>
    </div>
  )
}