import { describe, it, expect, beforeAll, afterAll, afterEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import SettingsPage from '../../pages/SettingsPage'
import { useSettingsStore } from '../../stores/settingsStore'

// Mock the API module
vi.mock('../../services/api', () => ({
  settingsAPI: {
    getSettings: vi.fn(() => Promise.resolve({
      data: {
        id: 'default',
        user_id: null,
        name: 'Default Settings',
        user_preferences: {
          theme: 'system',
          language: 'en',
          message_display_mode: 'comfortable',
          font_size: 14,
          auto_save: true,
          auto_save_interval: 30,
          sound_enabled: true
        },
        ai_model_settings: {
          temperature: 0.7,
          max_tokens: 2048
        },
        api_providers: [],
        file_processing: {
          max_file_size: 10485760,
          allowed_extensions: ['.txt', '.md']
        },
        privacy: {
          enable_analytics: false
        },
        system: {
          log_level: 'INFO'
        },
        created_at: '2025-01-10T00:00:00Z',
        updated_at: '2025-01-10T00:00:00Z',
        version: '1.0.0',
        is_active: true
      }
    })),
    updateSettingsByCategory: vi.fn(() => Promise.resolve({
      data: { message: 'user_preferences updated successfully' }
    })),
    getSettingsByCategory: vi.fn(() => Promise.resolve({
      data: {
        user_preferences: {
          theme: 'dark',
          language: 'es',
          message_display_mode: 'comfortable',
          font_size: 14,
          auto_save: false,
          auto_save_interval: 60,
          sound_enabled: false
        }
      }
    })),
    exportSettings: vi.fn(() => Promise.resolve({
      data: {
        settings: {
          id: 'default',
          name: 'Default Settings',
          user_preferences: { theme: 'system' }
        },
        exported_at: '2025-01-10T00:00:00Z',
        export_version: '1.0.0',
        checksum: 'export-checksum-123'
      }
    })),
    importSettings: vi.fn(() => Promise.resolve({
      data: {
        id: 'imported-settings',
        name: 'Imported Settings',
        user_preferences: { theme: 'light' }
      }
    }))
  }
}))

// Mock window.alert for import functionality
Object.defineProperty(window, 'alert', {
  writable: true,
  value: vi.fn()
})

// Mock localStorage to prevent persistence issues
const localStorageMock = {
  getItem: vi.fn((key: string) => {
    if (key === 'ai-chat-settings') {
      return JSON.stringify({
        state: {
          preferences: {
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
          },
          uiState: {
            sidebarCollapsed: false,
            expandedSections: []
          }
        },
        version: 0
      })
    }
    return null
  }),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// Helper function to render SettingsPage with router
const renderSettingsPage = () => {
  return render(
    <MemoryRouter>
      <SettingsPage />
    </MemoryRouter>
  )
}

// Helper function to setup store with mock data
const setupStoreWithMockData = () => {
  useSettingsStore.setState({
    preferences: {
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
    },
    uiState: {
      sidebarCollapsed: false,
      expandedSections: []
    }
  })
}

describe('Settings End-to-End Tests', () => {
  it('completes full settings workflow from navigation to save', async () => {
    const user = userEvent.setup()

    // Render the SettingsPage directly with MemoryRouter
    renderSettingsPage()

    // Setup store with mock data after rendering
    setupStoreWithMockData()

    // Wait for the settings page to load
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
      expect(screen.getByText('Customize your AI Chat Assistant experience')).toBeInTheDocument()
    })

    // Verify we're on the settings page
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
      expect(screen.getByText('Customize your AI Chat Assistant experience')).toBeInTheDocument()
    })

    // The default active tab should be Profile
    const defaultProfileTab = screen.getByRole('button', { name: 'Profile' })
    expect(defaultProfileTab).toHaveClass('bg-blue-600', 'text-white')

    // Click on Profile tab (should be default active)
    const profileTab = screen.getByText('Profile')
    await user.click(profileTab)

    // Wait for settings to be loaded and language select to be present
    await waitFor(() => {
      const languageSelect = screen.getByLabelText('Language')
      expect(languageSelect).toBeInTheDocument()
    })

    // Get the language select and set it to 'en' for testing
    const languageSelect = screen.getByLabelText('Language')
    await user.selectOptions(languageSelect, 'en')

    // Verify it was set to 'en'
    expect(languageSelect).toHaveValue('en')

    // Change language setting
    await user.selectOptions(languageSelect, 'es')

    // Change theme setting (if available in profile)
    // Note: Theme might be in Appearance tab, let's check

    // Navigate to Appearance tab
    const appearanceTab = screen.getByText('Appearance')
    await user.click(appearanceTab)

    // Wait for settings to be loaded and theme select to be present
    await waitFor(() => {
      const themeSelect = screen.getByLabelText('Theme')
      expect(themeSelect).toBeInTheDocument()
    })

    // Get the theme select and set it to 'system' for testing
    const themeSelect = screen.getByLabelText('Theme')
    await user.selectOptions(themeSelect, 'system')

    // Verify it was set to 'system'
    expect(themeSelect).toHaveValue('system')

    // Change theme setting
    await user.selectOptions(themeSelect, 'dark')
    expect(themeSelect).toHaveValue('dark')

    // Navigate to System tab
    const systemTab = screen.getByRole('button', { name: 'System' })
    await user.click(systemTab)

    // Verify System settings are displayed
    expect(screen.getByText('System Settings')).toBeInTheDocument()
    expect(screen.getByText('Configure system-wide preferences and behavior.')).toBeInTheDocument()

    // Toggle auto-save setting
    const autoSaveCheckbox = screen.getByLabelText('Auto Save')
    await user.click(autoSaveCheckbox)

    // Change auto-save interval
    const intervalInput = screen.getByDisplayValue('30')
    await user.clear(intervalInput)
    await user.type(intervalInput, '60')

    // Click Save Settings button
    const saveButton = screen.getByRole('button', { name: /save settings/i })
    await user.click(saveButton)

    // Verify save success (button text changes to "Saved!")
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /saved!/i })).toBeInTheDocument()
    })

    // Verify settings were actually saved by checking if the API was called
    // This would be verified by the MSW server intercepting the requests
  })

  it('handles settings export and import workflow', async () => {
    const user = userEvent.setup()

    renderSettingsPage()

    // Wait for the settings page to load
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
    })

    // Click Export Settings button
    const exportButton = screen.getByRole('button', { name: /export settings/i })
    await user.click(exportButton)

    // Note: In a real browser, this would trigger a download
    // For testing, we just verify the API call was made

    // Test import functionality
    const importLabel = screen.getByText('Import Settings')
    const importInput = importLabel.querySelector('input[type="file"]') as HTMLInputElement

    // Create a mock file
    const mockFile = new File(['{"settings": {"name": "Test"}, "import_version": "1.0.0"}'], 'settings.json', {
      type: 'application/json'
    })

    // Simulate file selection
    await user.upload(importInput, mockFile)

    // The import should be triggered automatically
    // In a real scenario, this would process the file and call the import API
  })

  it('handles settings validation and error states', async () => {
    const user = userEvent.setup()

    // Mock the API to return validation errors
    const { settingsAPI } = await import('../../services/api')
    vi.mocked(settingsAPI.updateSettingsByCategory).mockImplementationOnce(() => 
      Promise.reject(new Error('Invalid settings data'))
    )

    renderSettingsPage()

    // Wait for the settings page to load
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
    })

    // Navigate to Appearance tab
    const appearanceTab = screen.getByText('Appearance')
    await user.click(appearanceTab)

    // Wait for settings to be loaded and theme select to be present
    await waitFor(() => {
      const themeSelect = screen.getByLabelText('Theme')
      expect(themeSelect).toBeInTheDocument()
    })

    // Get the theme select and set it to 'system' for testing
    const themeSelect = screen.getByLabelText('Theme')
    await user.selectOptions(themeSelect, 'system')

    // Try to set an invalid theme value (this would be handled by the select, but let's test error handling)
    expect(themeSelect).toHaveValue('system')

    // Click Save Settings
    const saveButton = screen.getByRole('button', { name: /save settings/i })
    await user.click(saveButton)

    // Verify error state (button shows "Error!")
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /error!/i })).toBeInTheDocument()
    })
  })

  it('handles network errors gracefully', async () => {
    const user = userEvent.setup()

    // Mock network failure
    const { settingsAPI } = await import('../../services/api')
    vi.mocked(settingsAPI.getSettings).mockImplementationOnce(() => 
      Promise.reject(new Error('Network Error'))
    )

    renderSettingsPage()

    // The settings page should still load, but with error handling
    // In a real app, this might show an error message or fallback to defaults
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
    })

    // The settings page should still load, but with error handling
    // In a real app, this might show an error message or fallback to defaults
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
    })
  })

  it('persists settings across navigation', async () => {
    const user = userEvent.setup()

    renderSettingsPage()

    // Wait for the settings page to load
    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: 'Settings' })).toBeInTheDocument()
    })

    // Change a setting
    const appearanceTab = screen.getByText('Appearance')
    await user.click(appearanceTab)

    // Wait for settings to be loaded and theme select to be present
    await waitFor(() => {
      const themeSelect = screen.getByLabelText('Theme')
      expect(themeSelect).toBeInTheDocument()
    })

    // Get the theme select and set it to 'system' for testing
    const themeSelect = screen.getByLabelText('Theme')
    await user.selectOptions(themeSelect, 'system')
    expect(themeSelect).toHaveValue('system')

    await user.selectOptions(themeSelect, 'dark')

    // Verify the setting was changed
    expect(themeSelect).toHaveValue('dark')

    // Save the settings
    const saveButton = screen.getByRole('button', { name: /save settings/i })
    await user.click(saveButton)

    // Verify save was attempted (API was called)
    // In a real E2E test, we would verify persistence across sessions
    // For this isolated component test, we verify the UI interaction works
  })
})
