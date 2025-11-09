from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from backend.services.project_service import ProjectService
from backend.models.project import (
    Project, ProjectCreate, ProjectUpdate,
    ProjectTree, ProjectSummary, ProjectStats
)

# Create router
router = APIRouter(prefix="/api/projects", tags=["projects"])

# Dependency to get project service
def get_project_service() -> ProjectService:
    """Dependency to get project service instance"""
    return ProjectService()


@router.get("/", response_model=List[ProjectSummary])
async def list_projects(
    parent_id: Optional[str] = None,
    project_service: ProjectService = Depends(get_project_service)
):
    """
    List all projects, optionally filtered by parent project.

    - **parent_id**: Filter by parent project ID (optional)
    - Returns list of project summaries
    """
    try:
        return project_service.list_projects(parent_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")


@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Create a new project.

    - **name**: Project name (required, 1-100 characters)
    - **description**: Project description (optional)
    - **parent_id**: Parent project ID for nested projects (optional)
    - Returns created project
    """
    try:
        return project_service.create_project(project)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get project details by ID.

    - **project_id**: Project identifier
    - Returns project details
    """
    try:
        project = project_service.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Update project information.

    - **project_id**: Project identifier
    - **name**: New project name (optional)
    - **description**: New project description (optional)
    - **parent_id**: New parent project ID (optional)
    - Returns updated project
    """
    try:
        updated_project = project_service.update_project(project_id, project_update)
        if not updated_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return updated_project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    force: bool = False,
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Delete a project and all its contents.

    - **project_id**: Project identifier
    - **force**: Force deletion even if project has children (default: false)
    - Returns success message
    """
    try:
        deleted = project_service.delete_project(project_id, force)
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


@router.get("/{project_id}/tree", response_model=List[ProjectTree])
async def get_project_tree(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get project hierarchy tree starting from specified project.

    - **project_id**: Root project identifier
    - Returns project tree structure
    """
    try:
        tree = project_service.get_project_tree(project_id)
        return tree
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project tree: {str(e)}")


@router.get("/tree/all", response_model=List[ProjectTree])
async def get_all_projects_tree(
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get complete project hierarchy tree for all root projects.

    - Returns complete project tree structure
    """
    try:
        tree = project_service.get_project_tree()
        return tree
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project tree: {str(e)}")


@router.get("/stats/overview", response_model=ProjectStats)
async def get_project_stats(
    project_service: ProjectService = Depends(get_project_service)
):
    """
    Get overall project statistics.

    - Returns project statistics including counts and storage info
    """
    try:
        return project_service.get_project_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get project stats: {str(e)}")