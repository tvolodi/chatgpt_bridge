import React, { useState, useEffect } from 'react'
import { useProjectStore, ProjectSummary, CreateProjectData, UpdateProjectData } from '../stores/projectStore'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Plus, Edit, Trash2, Folder, FileText, Users } from 'lucide-react'

interface ProjectCardProps {
  project: ProjectSummary
  onEdit: (project: ProjectSummary) => void
  onDelete: (project: ProjectSummary) => void
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project, onEdit, onDelete }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Folder className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-50">{project.name}</h3>
            {project.description && (
              <p className="text-sm text-slate-400 mt-1">{project.description}</p>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onEdit(project)}
            className="text-slate-400 hover:text-white"
            aria-label={`Edit ${project.name}`}
            title={`Edit ${project.name}`}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => onDelete(project)}
            className="text-slate-400 hover:text-red-400"
            disabled={project.id === 'default'}
            aria-label={`Delete ${project.name}`}
            title={`Delete ${project.name}`}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm text-slate-400">
        <div className="flex items-center gap-1">
          <FileText className="h-4 w-4" />
          <span>Files</span>
        </div>
        {project.has_children && (
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            <span>{project.children_count} sub-projects</span>
          </div>
        )}
        <div className="ml-auto text-xs">
          {new Date(project.created_at).toLocaleDateString()}
        </div>
      </div>
    </div>
  )
}

interface ProjectModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: CreateProjectData | UpdateProjectData) => Promise<void>
  project?: ProjectSummary | null
  title: string
}

const ProjectModal: React.FC<ProjectModalProps> = ({
  isOpen,
  onClose,
  onSave,
  project,
  title
}) => {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (project) {
      setName(project.name)
      setDescription(project.description || '')
    } else {
      setName('')
      setDescription('')
    }
    setError('')
  }, [project, isOpen])

  const handleSave = async () => {
    if (!name.trim()) {
      setError('Project name is required')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      await onSave({
        name: name.trim(),
        description: description.trim() || undefined
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save project')
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md border border-slate-700">
        <h2 className="text-xl font-semibold text-slate-50 mb-4">{title}</h2>

        <div className="space-y-4">
          <div>
            <label htmlFor="project-name" className="block text-sm font-medium text-slate-200 mb-2">
              Project Name *
            </label>
            <Input
              id="project-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter project name"
              className={error ? 'border-red-500' : ''}
            />
          </div>

          <div>
            <label htmlFor="project-description" className="block text-sm font-medium text-slate-200 mb-2">
              Description
            </label>
            <textarea
              id="project-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter project description (optional)"
              rows={3}
              className="flex w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-slate-50 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm">{error}</div>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <Button
            onClick={handleSave}
            disabled={isLoading}
            className="flex-1"
          >
            {isLoading ? 'Saving...' : 'Save'}
          </Button>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  )
}

interface DeleteConfirmModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => Promise<void>
  project: ProjectSummary | null
}

const DeleteConfirmModal: React.FC<DeleteConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  project
}) => {
  const [isLoading, setIsLoading] = useState(false)

  const handleConfirm = async () => {
    setIsLoading(true)
    try {
      await onConfirm()
      onClose()
    } catch (err) {
      // Error is handled in the parent component
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen || !project) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg p-6 w-full max-w-md border border-slate-700">
        <h2 className="text-xl font-semibold text-slate-50 mb-4">Delete Project</h2>

        <p className="text-slate-300 mb-4">
          Are you sure you want to delete <strong>"{project.name}"</strong>?
          This action cannot be undone and will remove all associated files and chat sessions.
        </p>

        {project.has_children && (
          <div className="bg-yellow-900 border border-yellow-600 rounded p-3 mb-4">
            <p className="text-yellow-200 text-sm">
              This project has {project.children_count} sub-projects. Deleting it will also delete all child projects.
            </p>
          </div>
        )}

        <div className="flex gap-3">
          <Button
            variant="destructive"
            onClick={handleConfirm}
            disabled={isLoading}
            className="flex-1"
          >
            {isLoading ? 'Deleting...' : 'Delete'}
          </Button>
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
        </div>
      </div>
    </div>
  )
}

export const ProjectsPage: React.FC = () => {
  const {
    projects,
    isLoading,
    error,
    loadProjects,
    createProject,
    updateProject,
    deleteProject
  } = useProjectStore()

  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [selectedProject, setSelectedProject] = useState<ProjectSummary | null>(null)

  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  const handleCreateProject = async (data: CreateProjectData) => {
    await createProject(data)
  }

  const handleEditProject = (project: ProjectSummary) => {
    setSelectedProject(project)
    setEditModalOpen(true)
  }

  const handleUpdateProject = async (data: UpdateProjectData) => {
    if (selectedProject) {
      await updateProject(selectedProject.id, data)
      setSelectedProject(null)
    }
  }

  const handleDeleteProject = (project: ProjectSummary) => {
    setSelectedProject(project)
    setDeleteModalOpen(true)
  }

  const handleConfirmDelete = async () => {
    if (selectedProject) {
      await deleteProject(selectedProject.id)
      setSelectedProject(null)
    }
  }

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-50 mb-2">Projects</h1>
            <p className="text-slate-400">Manage your projects and organize your conversations</p>
          </div>
          <Button onClick={() => setCreateModalOpen(true)} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            New Project
          </Button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900 border border-red-600 rounded-lg p-4 mb-6">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && projects.length === 0 && (
          <div className="text-center py-12">
            <div className="text-slate-400">Loading projects...</div>
          </div>
        )}

        {/* Projects Grid */}
        {!isLoading || projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onEdit={handleEditProject}
                onDelete={handleDeleteProject}
              />
            ))}
          </div>
        ) : null}

        {/* Empty State */}
        {!isLoading && projects.length === 0 && (
          <div className="text-center py-12">
            <Folder className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-300 mb-2">No projects yet</h3>
            <p className="text-slate-400 mb-6">Create your first project to get started organizing your conversations.</p>
            <Button onClick={() => setCreateModalOpen(true)} className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Create Project
            </Button>
          </div>
        )}

        {/* Modals */}
        <ProjectModal
          isOpen={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
          onSave={handleCreateProject}
          title="Create New Project"
        />

        <ProjectModal
          isOpen={editModalOpen}
          onClose={() => {
            setEditModalOpen(false)
            setSelectedProject(null)
          }}
          onSave={handleUpdateProject}
          project={selectedProject}
          title="Edit Project"
        />

        <DeleteConfirmModal
          isOpen={deleteModalOpen}
          onClose={() => {
            setDeleteModalOpen(false)
            setSelectedProject(null)
          }}
          onConfirm={handleConfirmDelete}
          project={selectedProject}
        />
      </div>
    </div>
  )
}

export default ProjectsPage