import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ProfileSettings } from '../components/settings/ProfileSettings'
import { useSettingsStore } from '../stores/settingsStore'

// Mock the settings store
const mockUpdatePreferences = vi.fn()
vi.mock('../stores/settingsStore', () => ({
  useSettingsStore: vi.fn()
}))

describe('ProfileSettings Component', () => {
  const mockPreferences = {
    theme: 'system' as const,
    layout: 'comfortable' as const,
    language: 'en',
    timezone: 'UTC',
    dateFormat: 'YYYY-MM-DD',
    timeFormat: '24h' as const,
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
  }

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useSettingsStore as any).mockReturnValue({
      preferences: mockPreferences,
      updatePreferences: mockUpdatePreferences
    })
  })

  it('renders profile settings form correctly', () => {
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    expect(screen.getByText('Profile Settings')).toBeInTheDocument()
    expect(screen.getByText('Manage your personal information and preferences.')).toBeInTheDocument()
    expect(screen.getByText('Language')).toBeInTheDocument()
    expect(screen.getByText('Timezone')).toBeInTheDocument()
    expect(screen.getByText('Date Format')).toBeInTheDocument()
    expect(screen.getByText('Time Format')).toBeInTheDocument()
  })

  it('displays current preference values', () => {
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    const languageSelect = screen.getByDisplayValue('en')
    const timezoneSelect = screen.getByDisplayValue('UTC')
    const dateFormatSelect = screen.getByDisplayValue('YYYY-MM-DD')
    const timeFormatSelect = screen.getByDisplayValue('24 Hour')

    expect(languageSelect).toBeInTheDocument()
    expect(timezoneSelect).toBeInTheDocument()
    expect(dateFormatSelect).toBeInTheDocument()
    expect(timeFormatSelect).toBeInTheDocument()
  })

  it('calls onUpdate when language is changed', async () => {
    const user = userEvent.setup()
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    const languageSelect = screen.getByDisplayValue('en')
    await user.selectOptions(languageSelect, 'es')

    expect(mockUpdatePreferences).toHaveBeenCalledWith({ language: 'es' })
  })

  it('calls onUpdate when timezone is changed', async () => {
    const user = userEvent.setup()
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    const timezoneSelect = screen.getByDisplayValue('UTC')
    await user.selectOptions(timezoneSelect, 'America/New_York')

    expect(mockUpdatePreferences).toHaveBeenCalledWith({ timezone: 'America/New_York' })
  })

  it('calls onUpdate when date format is changed', async () => {
    const user = userEvent.setup()
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    const dateFormatSelect = screen.getByDisplayValue('YYYY-MM-DD')
    await user.selectOptions(dateFormatSelect, 'MM/DD/YYYY')

    expect(mockUpdatePreferences).toHaveBeenCalledWith({ dateFormat: 'MM/DD/YYYY' })
  })

  it('calls onUpdate when time format is changed', async () => {
    const user = userEvent.setup()
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    const timeFormatSelect = screen.getByDisplayValue('24 Hour')
    await user.selectOptions(timeFormatSelect, '12h')

    expect(mockUpdatePreferences).toHaveBeenCalledWith({ timeFormat: '12h' })
  })

  it('handles all supported languages', () => {
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    const languageSelect = screen.getByDisplayValue('en')
    const options = Array.from(languageSelect.querySelectorAll('option')).map(option => option.value)

    expect(options).toEqual(['en', 'es', 'fr', 'de', 'zh'])
  })

  it('handles all supported timezones', () => {
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    const timezoneSelect = screen.getByDisplayValue('UTC')
    const options = Array.from(timezoneSelect.querySelectorAll('option')).map(option => option.value)

    expect(options).toContain('UTC')
    expect(options).toContain('America/New_York')
    expect(options).toContain('Europe/London')
    expect(options).toContain('Asia/Tokyo')
  })

  it('handles all supported date formats', () => {
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    const dateFormatSelect = screen.getByDisplayValue('YYYY-MM-DD')
    const options = Array.from(dateFormatSelect.querySelectorAll('option')).map(option => option.value)

    expect(options).toEqual(['YYYY-MM-DD', 'MM/DD/YYYY', 'DD/MM/YYYY'])
  })

  it('handles all supported time formats', () => {
    render(<ProfileSettings preferences={mockPreferences} onUpdate={mockUpdatePreferences} />)

    const timeFormatSelect = screen.getByDisplayValue('24 Hour')
    const options = Array.from(timeFormatSelect.querySelectorAll('option')).map(option => option.value)

    expect(options).toEqual(['12h', '24h'])
  })
})