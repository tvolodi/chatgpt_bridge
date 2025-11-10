import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { settingsAPI } from '../../services/api'

// Mock server setup
const server = setupServer(
  // Mock settings endpoints
  http.get('http://localhost:8000/api/settings/user/default/effective', () => {
    return HttpResponse.json({
      id: 'default',
      user_id: null,
      name: 'Default Settings',
      description: null,
      user_preferences: {
        theme: 'system',
        language: 'en',
        message_display_mode: 'comfortable',
        font_size: 14,
        auto_save: true,
        auto_save_interval: 30,
        show_timestamps: true,
        show_typing_indicators: true,
        sound_enabled: true,
        notification_level: 'all',
        max_conversation_history: 1000,
        default_export_format: 'json'
      },
      ai_model_settings: {
        temperature: 0.7,
        max_tokens: 2048,
        top_p: 1.0,
        frequency_penalty: 0.0,
        presence_penalty: 0.0,
        system_prompt: null,
        context_window_size: 10
      },
      api_providers: [],
      file_processing: {
        max_file_size: 10485760,
        allowed_extensions: ['.txt', '.md', '.pdf', '.docx', '.doc', '.rtf', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp3', '.wav', '.mp4', '.avi', '.mov', '.json', '.csv', '.xml', '.yaml', '.yml'],
        auto_process_files: true,
        enable_ocr: false,
        max_concurrent_processes: 3,
        processing_timeout: 300
      },
      privacy: {
        enable_analytics: false,
        enable_error_reporting: true,
        data_retention_days: 365,
        auto_delete_old_conversations: false,
        encrypt_sensitive_data: true,
        allow_data_export: true
      },
      system: {
        log_level: 'INFO',
        enable_debug_mode: false,
        backup_enabled: true,
        backup_interval_hours: 24,
        max_backup_count: 10,
        enable_performance_monitoring: false,
        cache_enabled: true,
        cache_ttl_seconds: 3600
      },
      created_at: '2025-01-10T00:00:00Z',
      updated_at: '2025-01-10T00:00:00Z',
      version: '1.0.0',
      is_active: true
    })
  }),

  http.put('http://localhost:8000/api/settings/categories/user_preferences', () => {
    return HttpResponse.json({
      message: 'user_preferences updated successfully'
    })
  }),

  http.get('http://localhost:8000/api/settings/categories/user_preferences', () => {
    return HttpResponse.json({
      user_preferences: {
        theme: 'dark',
        language: 'en',
        message_display_mode: 'comfortable',
        font_size: 14,
        auto_save: true,
        auto_save_interval: 30,
        show_timestamps: true,
        show_typing_indicators: true,
        sound_enabled: true,
        notification_level: 'all',
        max_conversation_history: 1000,
        default_export_format: 'json'
      }
    })
  }),

  http.get('http://localhost:8000/api/settings/default/export', () => {
    return HttpResponse.json({
      settings: {
        id: 'default',
        name: 'Default Settings',
        user_preferences: { theme: 'system' }
      },
      exported_at: '2025-01-10T00:00:00Z',
      export_version: '1.0.0',
      checksum: 'abc123'
    })
  }),

  http.post('http://localhost:8000/api/settings/import', () => {
    return HttpResponse.json({
      id: 'imported-settings',
      name: 'Imported Settings',
      user_preferences: { theme: 'light' }
    })
  })
)

// Start server before all tests
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))

// Reset handlers after each test
afterEach(() => server.resetHandlers())

// Close server after all tests
afterAll(() => server.close())

describe('Settings API Integration Tests', () => {
  describe('getSettings', () => {
    it('should fetch settings successfully', async () => {
      const response = await settingsAPI.getSettings()

      expect(response.data).toBeDefined()
      expect(response.data.id).toBe('default')
      expect(response.data.name).toBe('Default Settings')
      expect(response.data.user_preferences).toBeDefined()
      expect(response.data.user_preferences.theme).toBe('system')
      expect(response.data.ai_model_settings).toBeDefined()
      expect(response.data.system).toBeDefined()
    })

    it('should handle API errors gracefully', async () => {
      // Mock server error
      server.use(
        http.get('http://localhost:8000/api/settings/user/default/effective', () => {
          return HttpResponse.json({ error: 'Internal server error' }, { status: 500 })
        })
      )

      await expect(settingsAPI.getSettings()).rejects.toThrow()
    })
  })

  describe('updateSettingsByCategory', () => {
    it('should update user preferences successfully', async () => {
      const updateData = {
        theme: 'dark',
        language: 'en',
        auto_save: true
      }

      const response = await settingsAPI.updateSettingsByCategory('user_preferences', updateData)

      expect(response.data).toBeDefined()
      expect(response.data.message).toBe('user_preferences updated successfully')
    })

    it('should handle validation errors', async () => {
      server.use(
        http.put('http://localhost:8000/api/settings/categories/user_preferences', () => {
          return HttpResponse.json({ error: 'Invalid settings data' }, { status: 400 })
        })
      )

      await expect(settingsAPI.updateSettingsByCategory('user_preferences', {})).rejects.toThrow()
    })
  })

  describe('getSettingsByCategory', () => {
    it('should fetch category settings successfully', async () => {
      const response = await settingsAPI.getSettingsByCategory('user_preferences')

      expect(response.data).toBeDefined()
      expect(response.data.user_preferences).toBeDefined()
      expect(response.data.user_preferences.theme).toBe('dark')
    })
  })

  describe('exportSettings', () => {
    it('should export settings successfully', async () => {
      const response = await settingsAPI.exportSettings()

      expect(response.data).toBeDefined()
      expect(response.data.settings).toBeDefined()
      expect(response.data.exported_at).toBeDefined()
      expect(response.data.checksum).toBe('abc123')
    })
  })

  describe('importSettings', () => {
    it('should import settings successfully', async () => {
      const importData = {
        settings: {
          name: 'Imported Settings',
          user_preferences: { theme: 'light' }
        },
        import_version: '1.0.0'
      }

      const response = await settingsAPI.importSettings(importData)

      expect(response.data).toBeDefined()
      expect(response.data.id).toBe('imported-settings')
      expect(response.data.name).toBe('Imported Settings')
    })
  })

  describe('Cross-functional scenarios', () => {
    it('should handle complete settings workflow', async () => {
      // 1. Get current settings
      const initialSettings = await settingsAPI.getSettings()
      expect(initialSettings.data.user_preferences.theme).toBe('system')

      // 2. Update settings
      await settingsAPI.updateSettingsByCategory('user_preferences', {
        theme: 'dark',
        language: 'en'
      })

      // 3. Verify update by fetching category
      const updatedCategory = await settingsAPI.getSettingsByCategory('user_preferences')
      expect(updatedCategory.data.user_preferences.theme).toBe('dark')

      // 4. Export settings
      const exportData = await settingsAPI.exportSettings()
      expect(exportData.data.settings.name).toBe('Default Settings')

      // 5. Import settings (would create new settings in real scenario)
      const importResult = await settingsAPI.importSettings({
        settings: exportData.data.settings,
        import_version: '1.0.0'
      })
      expect(importResult.data.name).toBe('Imported Settings')
    })

    it('should handle network errors gracefully', async () => {
      // Simulate network failure
      server.use(
        http.get('http://localhost:8000/api/settings/user/default/effective', () => {
          return HttpResponse.error()
        })
      )

      await expect(settingsAPI.getSettings()).rejects.toThrow()
    })

    it('should handle timeout scenarios', async () => {
      server.use(
        http.put('http://localhost:8000/api/settings/categories/user_preferences', async () => {
          // Simulate delay
          await new Promise(resolve => setTimeout(resolve, 100))
          return HttpResponse.json({ message: 'Success' })
        })
      )

      // This would timeout in a real scenario, but for testing we'll just check it doesn't hang
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Timeout')), 50)
      )

      await expect(Promise.race([
        settingsAPI.updateSettingsByCategory('user_preferences', { theme: 'light' }),
        timeoutPromise
      ])).rejects.toThrow('Timeout')
    })
  })
})