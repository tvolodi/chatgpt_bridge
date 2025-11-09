import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from backend.services.project_service import ProjectService
from backend.models.project import ProjectCreate, ProjectUpdate


class TestProjectService:
    """Test cases for ProjectService"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.service = ProjectService(str(self.temp_dir))

    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_create_project(self):
        """Test creating a new project"""
        project_data = ProjectCreate(
            name="Test Project",
            description="A test project",
            parent_id=None
        )

        project = self.service.create_project(project_data)

        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.parent_id is None
        assert project.id is not None

        # Verify project directory exists
        project_dir = self.service._get_project_directory(project.id)
        assert project_dir.exists()

        # Verify metadata file exists
        metadata_path = self.service._get_project_metadata_path(project.id)
        assert metadata_path.exists()

    def test_get_project(self):
        """Test getting a project by ID"""
        # Create a project first
        project_data = ProjectCreate(name="Test Project")
        created_project = self.service.create_project(project_data)

        # Get the project
        retrieved_project = self.service.get_project(created_project.id)

        assert retrieved_project is not None
        assert retrieved_project.id == created_project.id
        assert retrieved_project.name == created_project.name

    def test_list_projects(self):
        """Test listing projects"""
        # Create multiple projects
        project1 = self.service.create_project(ProjectCreate(name="Project 1"))
        project2 = self.service.create_project(ProjectCreate(name="Project 2"))

        projects = self.service.list_projects()

        assert len(projects) >= 2  # At least the two we created plus default
        project_names = [p.name for p in projects]
        assert "Project 1" in project_names
        assert "Project 2" in project_names

    def test_update_project(self):
        """Test updating a project"""
        # Create a project
        project = self.service.create_project(ProjectCreate(name="Original Name"))

        # Update the project
        update_data = ProjectUpdate(name="Updated Name", description="Updated description")
        updated_project = self.service.update_project(project.id, update_data)

        assert updated_project is not None
        assert updated_project.name == "Updated Name"
        assert updated_project.description == "Updated description"

    def test_delete_project(self):
        """Test deleting a project"""
        # Create a project
        project = self.service.create_project(ProjectCreate(name="To Delete"))

        # Delete the project
        result = self.service.delete_project(project.id)

        assert result is True

        # Verify project is gone
        retrieved = self.service.get_project(project.id)
        assert retrieved is None

        # Verify directory is gone
        project_dir = self.service._get_project_directory(project.id)
        assert not project_dir.exists()

    def test_nested_projects(self):
        """Test nested project hierarchy"""
        # Create parent project
        parent = self.service.create_project(ProjectCreate(name="Parent Project"))

        # Create child project
        child = self.service.create_project(ProjectCreate(
            name="Child Project",
            parent_id=parent.id
        ))

        # Verify parent-child relationship
        assert child.parent_id == parent.id

        # List children of parent
        children = self.service.list_projects(parent.id)
        assert len(children) == 1
        assert children[0].id == child.id

    def test_project_validation(self):
        """Test project name validation"""
        # Test invalid names
        invalid_names = ["", "   ", "name>with<invalid", "a" * 101]

        for invalid_name in invalid_names:
            with pytest.raises(ValueError):
                self.service.create_project(ProjectCreate(name=invalid_name))

    def test_default_project_creation(self):
        """Test that default project is created automatically"""
        # Default project should exist
        default_project = self.service.get_project("default")
        assert default_project is not None
        assert default_project.name == "Default Project"

    def test_project_tree(self):
        """Test project tree structure"""
        # Create hierarchy: Parent -> Child1, Child2
        parent = self.service.create_project(ProjectCreate(name="Parent"))
        child1 = self.service.create_project(ProjectCreate(name="Child1", parent_id=parent.id))
        child2 = self.service.create_project(ProjectCreate(name="Child2", parent_id=parent.id))

        # Get tree
        tree = self.service.get_project_tree(parent.id)

        assert len(tree) == 1
        assert tree[0].project.id == parent.id
        assert len(tree[0].children) == 2

        child_ids = [child.project.id for child in tree[0].children]
        assert child1.id in child_ids
        assert child2.id in child_ids

    def test_circular_reference_prevention(self):
        """Test prevention of circular references"""
        # Create two projects
        project1 = self.service.create_project(ProjectCreate(name="Project 1"))
        project2 = self.service.create_project(ProjectCreate(name="Project 2"))

        # First, set project2 as child of project1 (this should work)
        self.service.update_project(project2.id, ProjectUpdate(parent_id=project1.id))

        # Now try to create circular reference: set project1 as child of project2
        # This would create: project1 -> project2 -> project1 (circular)
        with pytest.raises(ValueError, match="Circular reference"):
            self.service.update_project(project1.id, ProjectUpdate(parent_id=project2.id))

    def test_project_stats(self):
        """Test project statistics"""
        # Create some projects
        self.service.create_project(ProjectCreate(name="Project 1"))
        self.service.create_project(ProjectCreate(name="Project 2"))

        stats = self.service.get_project_stats()

        assert stats.total_projects >= 3  # 2 created + 1 default
        assert isinstance(stats.storage_size, int)
        assert isinstance(stats.total_files, int)

    def test_project_with_special_characters(self):
        """Test project creation with various valid names"""
        valid_names = [
            "Project-with-dashes",
            "Project with spaces",
            "Project_123",
            "Project.with.dots"
        ]

        for name in valid_names:
            project = self.service.create_project(ProjectCreate(name=name))
            assert project.name == name
            # Clean up
            self.service.delete_project(project.id, force=True)

    def test_project_timestamps(self):
        """Test that timestamps are properly set"""
        before_create = datetime.now()
        project = self.service.create_project(ProjectCreate(name="Timestamp Test"))
        after_create = datetime.now()

        assert before_create <= project.created_at <= after_create
        assert before_create <= project.updated_at <= after_create

        # Test update timestamp
        before_update = datetime.now()
        updated_project = self.service.update_project(project.id, ProjectUpdate(description="Updated"))
        after_update = datetime.now()

        assert updated_project.updated_at >= before_update
        assert updated_project.created_at == project.created_at  # Created should not change

    def test_project_directory_structure(self):
        """Test that project directories are created correctly"""
        project = self.service.create_project(ProjectCreate(name="Directory Test"))

        # Check project directory exists
        project_dir = self.service._get_project_directory(project.id)
        assert project_dir.exists()
        assert project_dir.is_dir()

        # Check metadata directory exists
        metadata_dir = self.service.metadata_path
        assert metadata_dir.exists()

        # Check metadata file exists
        metadata_file = self.service._get_project_metadata_path(project.id)
        assert metadata_file.exists()
        assert metadata_file.is_file()

    def test_delete_default_project_fails(self):
        """Test that deleting the default project fails"""
        with pytest.raises(ValueError, match="Cannot delete default project"):
            self.service.delete_project("default")

    def test_update_nonexistent_project(self):
        """Test updating a project that doesn't exist"""
        result = self.service.update_project("nonexistent-id", ProjectUpdate(name="New Name"))
        assert result is None

    def test_get_nonexistent_project(self):
        """Test getting a project that doesn't exist"""
        result = self.service.get_project("nonexistent-id")
        assert result is None

    def test_complex_hierarchy(self):
        """Test complex nested hierarchy"""
        # Create: Root -> Child1, Child2 -> GrandChild
        root = self.service.create_project(ProjectCreate(name="Root"))
        child1 = self.service.create_project(ProjectCreate(name="Child1", parent_id=root.id))
        child2 = self.service.create_project(ProjectCreate(name="Child2", parent_id=root.id))
        grandchild = self.service.create_project(ProjectCreate(name="GrandChild", parent_id=child1.id))

        # Verify hierarchy
        tree = self.service.get_project_tree(root.id)
        assert len(tree) == 1
        assert tree[0].project.id == root.id
        assert len(tree[0].children) == 2

        # Find child1 and verify it has grandchild
        child1_node = next(child for child in tree[0].children if child.project.id == child1.id)
        assert len(child1_node.children) == 1
        assert child1_node.children[0].project.id == grandchild.id

    def test_project_filtering(self):
        """Test project listing with parent filtering"""
        # Create hierarchy
        parent = self.service.create_project(ProjectCreate(name="Parent"))
        child1 = self.service.create_project(ProjectCreate(name="Child1", parent_id=parent.id))
        child2 = self.service.create_project(ProjectCreate(name="Child2", parent_id=parent.id))

        # Get all projects
        all_projects = self.service.list_projects()
        assert len(all_projects) >= 3  # parent + children + default

        # Get children of parent
        children = self.service.list_projects(parent.id)
        assert len(children) == 2
        child_ids = [p.id for p in children]
        assert child1.id in child_ids
        assert child2.id in child_ids

    def test_project_metadata_persistence(self):
        """Test that project metadata persists correctly"""
        project_data = ProjectCreate(
            name="Persistence Test",
            description="Testing metadata persistence",
            parent_id=None
        )

        # Create project
        project = self.service.create_project(project_data)

        # Reload service (simulate restart)
        new_service = ProjectService(str(self.temp_dir))

        # Get project from new service instance
        reloaded_project = new_service.get_project(project.id)

        assert reloaded_project is not None
        assert reloaded_project.id == project.id
        assert reloaded_project.name == project.name
        assert reloaded_project.description == project.description
        assert reloaded_project.parent_id == project.parent_id
        assert reloaded_project.path == project.path