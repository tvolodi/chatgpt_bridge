import React, { useState, useRef, useEffect } from 'react'
import { Send, FileText, ChevronDown, X } from 'lucide-react'
import { useTemplateStore, MessageTemplateSummary } from '../stores/templateStore'

interface ChatInputProps {
  onSend: (message: string) => void
  isLoading?: boolean
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading = false }) => {
  const [input, setInput] = useState('')
  const [showTemplates, setShowTemplates] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<MessageTemplateSummary | null>(null)
  const [templateParameters, setTemplateParameters] = useState<Record<string, string>>({})
  const [showParameterModal, setShowParameterModal] = useState(false)

  const { templates, loadTemplates, substituteTemplate, getTemplatePlaceholders } = useTemplateStore()
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadTemplates()
  }, [loadTemplates])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowTemplates(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleTemplateSelect = async (template: MessageTemplateSummary) => {
    setSelectedTemplate(template)
    setShowTemplates(false)

    try {
      // Get placeholders for this template
      const placeholders = await getTemplatePlaceholders(template.id)

      if (placeholders.length > 0) {
        // If template has placeholders, show parameter modal
        setTemplateParameters(
          placeholders.reduce((acc, placeholder) => ({ ...acc, [placeholder]: '' }), {})
        )
        setShowParameterModal(true)
      } else {
        // If no placeholders, insert directly
        const result = await substituteTemplate(template.id, {})
        setInput(result.substituted_content)
      }
    } catch (error) {
      console.error('Failed to load template:', error)
    }
  }

  const handleParameterSubmit = async () => {
    if (!selectedTemplate) return

    try {
      const result = await substituteTemplate(selectedTemplate.id, templateParameters)
      setInput(result.substituted_content)
      setShowParameterModal(false)
      setSelectedTemplate(null)
      setTemplateParameters({})
    } catch (error) {
      console.error('Failed to substitute template:', error)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSend(input.trim())
      setInput('')
      setSelectedTemplate(null)
    }
  }

  const clearTemplate = () => {
    setSelectedTemplate(null)
    setTemplateParameters({})
    setShowParameterModal(false)
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={selectedTemplate ? `Using template: ${selectedTemplate.name}` : "Ask me anything..."}
            disabled={isLoading}
            className="w-full px-4 py-2 bg-slate-800 text-slate-50 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 pr-12"
          />

          {/* Template selector button */}
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
            {selectedTemplate && (
              <button
                type="button"
                onClick={clearTemplate}
                className="p-1 text-slate-400 hover:text-slate-50"
                title="Clear template"
              >
                <X size={16} />
              </button>
            )}
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setShowTemplates(!showTemplates)}
                className="p-1 text-slate-400 hover:text-slate-50"
                title="Insert template"
                disabled={isLoading}
              >
                <FileText size={16} />
              </button>

              {/* Templates dropdown */}
              {showTemplates && (
                <div className="absolute bottom-full right-0 mb-2 w-64 bg-slate-700 rounded-lg shadow-lg border border-slate-600 z-10 max-h-64 overflow-y-auto">
                  {templates.length === 0 ? (
                    <div className="p-3 text-center text-slate-400">
                      No templates available
                    </div>
                  ) : (
                    templates.map(template => (
                      <button
                        key={template.id}
                        type="button"
                        onClick={() => handleTemplateSelect(template)}
                        className="w-full text-left p-3 hover:bg-slate-600 border-b border-slate-600 last:border-b-0"
                      >
                        <div className="font-medium text-slate-50">{template.name}</div>
                        <div className="text-sm text-slate-400">{template.category}</div>
                        {template.description && (
                          <div className="text-xs text-slate-500 truncate">{template.description}</div>
                        )}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Send size={18} />
          <span className="hidden sm:inline">Send</span>
        </button>
      </form>

      {/* Parameter substitution modal */}
      {showParameterModal && selectedTemplate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-slate-50 mb-4">
                Fill Template Parameters
              </h3>
              <p className="text-slate-300 mb-4">
                Template: <span className="font-medium">{selectedTemplate.name}</span>
              </p>

              <div className="space-y-3">
                {Object.entries(templateParameters).map(([param, value]) => (
                  <div key={param}>
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      {param}
                    </label>
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => setTemplateParameters({
                        ...templateParameters,
                        [param]: e.target.value
                      })}
                      className="w-full px-3 py-2 bg-slate-700 text-slate-50 rounded border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={`Enter value for ${param}`}
                    />
                  </div>
                ))}
              </div>

              <div className="flex gap-2 mt-6">
                <button
                  onClick={handleParameterSubmit}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Insert Template
                </button>
                <button
                  onClick={() => setShowParameterModal(false)}
                  className="px-4 py-2 bg-slate-600 text-slate-50 rounded hover:bg-slate-700"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default ChatInput
