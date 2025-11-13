import React, { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Eye, X, Save, FileText, Tag } from 'lucide-react'
import { useTemplateStore, MessageTemplate, MessageTemplateSummary, CreateTemplateData, UpdateTemplateData } from '../stores/templateStore'

interface TemplateManagerProps {
  isOpen: boolean
  onClose: () => void
}

export const TemplateManager: React.FC<TemplateManagerProps> = ({ isOpen, onClose }) => {
  const {
    templates,
    categories,
    isLoading,
    error,
    loadTemplates,
    loadCategories,
    createTemplate,
    updateTemplate,
    deleteTemplate,
    getTemplate
  } = useTemplateStore()

  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [isCreating, setIsCreating] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<MessageTemplate | null>(null)
  const [previewTemplate, setPreviewTemplate] = useState<MessageTemplate | null>(null)
  const [formData, setFormData] = useState<CreateTemplateData | UpdateTemplateData>({
    name: '',
    content: '',
    category: 'general',
    description: ''
  })

  useEffect(() => {
    if (isOpen) {
      loadTemplates()
      loadCategories()
    }
  }, [isOpen, loadTemplates, loadCategories])

  const resetForm = () => {
    setFormData({
      name: '',
      content: '',
      category: 'general',
      description: ''
    })
    setIsCreating(false)
    setEditingTemplate(null)
  }

  const handleCreate = async () => {
    try {
      await createTemplate(formData as CreateTemplateData)
      resetForm()
    } catch (error) {
      console.error('Failed to create template:', error)
    }
  }

  const handleUpdate = async () => {
    if (!editingTemplate) return
    try {
      await updateTemplate(editingTemplate.id, formData as UpdateTemplateData)
      resetForm()
    } catch (error) {
      console.error('Failed to update template:', error)
    }
  }

  const handleDelete = async (templateId: string) => {
    if (!confirm('Are you sure you want to delete this template?')) return
    try {
      await deleteTemplate(templateId)
    } catch (error) {
      console.error('Failed to delete template:', error)
    }
  }

  const handleEdit = async (templateSummary: MessageTemplateSummary) => {
    try {
      const template = await getTemplate(templateSummary.id)
      setEditingTemplate(template)
      setFormData({
        name: template.name,
        content: template.content,
        category: template.category,
        project_id: template.project_id,
        description: template.description
      })
    } catch (error) {
      console.error('Failed to load template for editing:', error)
    }
  }

  const handlePreview = async (templateId: string) => {
    try {
      const template = await getTemplate(templateId)
      setPreviewTemplate(template)
    } catch (error) {
      console.error('Failed to load template for preview:', error)
    }
  }

  const filteredTemplates = selectedCategory
    ? templates.filter(t => t.category === selectedCategory)
    : templates

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-slate-50">Template Manager</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-50"
            aria-label="Close template manager"
          >
            <X size={24} />
          </button>
        </div>

        <div className="flex h-[calc(90vh-80px)]">
          {/* Templates List */}
          <div className="w-1/2 border-r border-slate-700 p-6 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-slate-50">Templates</h3>
              <button
                onClick={() => setIsCreating(true)}
                className="flex items-center gap-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <Plus size={16} />
                New
              </button>
            </div>

            {/* Category Filter */}
            <div className="mb-4">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 text-slate-50 rounded border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category.name} value={category.name}>
                    {category.name} ({category.count})
                  </option>
                ))}
              </select>
            </div>

            {/* Templates List */}
            <div className="space-y-2">
              {filteredTemplates.map(template => (
                <div
                  key={template.id}
                  className="p-3 bg-slate-700 rounded border border-slate-600 hover:border-slate-500"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-slate-50">{template.name}</h4>
                      <div className="flex items-center gap-2 mt-1">
                        <Tag size={12} className="text-slate-400" />
                        <span className="text-sm text-slate-400">{template.category}</span>
                        {template.description && (
                          <span className="text-sm text-slate-500 truncate">
                            • {template.description}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handlePreview(template.id)}
                        className="p-1 text-slate-400 hover:text-slate-50"
                        title="Preview"
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        onClick={() => handleEdit(template)}
                        className="p-1 text-slate-400 hover:text-slate-50"
                        title="Edit"
                      >
                        <Edit size={16} />
                      </button>
                      <button
                        onClick={() => handleDelete(template.id)}
                        className="p-1 text-red-400 hover:text-red-300"
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {filteredTemplates.length === 0 && (
              <div className="text-center py-8 text-slate-400">
                <FileText size={48} className="mx-auto mb-4 opacity-50" />
                <p>No templates found</p>
                <p className="text-sm">Create your first template to get started</p>
              </div>
            )}
          </div>

          {/* Form Panel */}
          <div className="w-1/2 p-6 overflow-y-auto">
            {(isCreating || editingTemplate) && (
              <div>
                <h3 className="text-lg font-medium text-slate-50 mb-4">
                  {isCreating ? 'Create Template' : 'Edit Template'}
                </h3>

                <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Name
                    </label>
                    <input
                      type="text"
                      value={formData.name || ''}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-700 text-slate-50 rounded border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Template name"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Category
                    </label>
                    <select
                      value={formData.category || 'general'}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-700 text-slate-50 rounded border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {categories.map(category => (
                        <option key={category.name} value={category.name}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Description (optional)
                    </label>
                    <input
                      type="text"
                      value={formData.description || ''}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-700 text-slate-50 rounded border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Brief description"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">
                      Content
                    </label>
                    <textarea
                      value={formData.content || ''}
                      onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-700 text-slate-50 rounded border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 h-32 resize-none"
                      placeholder="Template content with optional {{placeholders}}"
                      required
                    />
                    <p className="text-xs text-slate-400 mt-1">
                      Use &#123;&#123;variable&#125;&#125; for placeholders that will be substituted
                    </p>
                  </div>

                  <div className="flex gap-2 pt-4">
                    <button
                      onClick={isCreating ? handleCreate : handleUpdate}
                      disabled={isLoading}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      <Save size={16} />
                      {isCreating ? 'Create' : 'Update'}
                    </button>
                    <button
                      onClick={resetForm}
                      className="px-4 py-2 bg-slate-600 text-slate-50 rounded hover:bg-slate-700"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Preview Panel */}
            {previewTemplate && !isCreating && !editingTemplate && (
              <div>
                <h3 className="text-lg font-medium text-slate-50 mb-4">Template Preview</h3>

                <div className="bg-slate-700 rounded p-4 border border-slate-600">
                  <h4 className="font-medium text-slate-50 mb-2">{previewTemplate.name}</h4>
                  <div className="flex items-center gap-2 mb-3">
                    <Tag size={12} className="text-slate-400" />
                    <span className="text-sm text-slate-400">{previewTemplate.category}</span>
                    {previewTemplate.description && (
                      <span className="text-sm text-slate-500">• {previewTemplate.description}</span>
                    )}
                  </div>
                  <div className="bg-slate-800 rounded p-3 border border-slate-600">
                    <pre className="text-slate-50 whitespace-pre-wrap text-sm">
                      {previewTemplate.content}
                    </pre>
                  </div>
                  <div className="mt-3 text-xs text-slate-400">
                    Created: {new Date(previewTemplate.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => handleEdit(previewTemplate)}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    <Edit size={16} />
                    Edit
                  </button>
                  <button
                    onClick={() => setPreviewTemplate(null)}
                    className="px-4 py-2 bg-slate-600 text-slate-50 rounded hover:bg-slate-700"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!isCreating && !editingTemplate && !previewTemplate && (
              <div className="text-center py-12 text-slate-400">
                <FileText size={48} className="mx-auto mb-4 opacity-50" />
                <p>Select a template to preview or edit</p>
                <p className="text-sm">Or create a new template to get started</p>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-900 border-t border-red-700">
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default TemplateManager