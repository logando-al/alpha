import pytest
from unittest.mock import patch, MagicMock, ANY
from pathlib import Path
from alpha.initializer import ProjectInitializer

# Fixture for Initializer
@pytest.fixture
def initializer():
    return ProjectInitializer()

# Test 1: Configuration Loading
def test_commands_config_loaded(initializer):
    """Ensure commands.json is loaded correctly."""
    assert "django" in initializer.get_available_stacks()
    assert "fastapi" in initializer.get_available_stacks()
    assert "nextjs" in initializer.get_available_stacks()

# Test 2: Django Generation (Mocked)
def test_generate_django_mocked(initializer, tmp_path):
    config = {
        "project_name": "My Django App",
        "target_dir": str(tmp_path),
        "stack": "django"
    }
    
    with patch("alpha.initializer.subprocess.run") as mock_run:
        initializer.generate_project(config)
        
        # Verify call args
        # Should sanitize "My Django App" -> "my_django_app"
        # Command should contain sanitized name
        args = mock_run.call_args[0][0]
        assert "my_django_app" in args
        assert "startproject" in args
        assert "venv" in args

# Test 3: FastAPI Generation (Mocked) - Checks escaping fix
def test_generate_fastapi_mocked(initializer, tmp_path):
    config = {
        "project_name": "My API",
        "target_dir": str(tmp_path),
        "stack": "fastapi"
    }
    
    with patch("alpha.initializer.subprocess.run") as mock_run:
        initializer.generate_project(config)
        
        args = mock_run.call_args[0][0]
        assert "my_api" in args
        # Ensure the brace format didn't crash and injected correctly
        # The command should contain 'return {"Hello": "World"}' (Sanity check)
        # However, shell escaping might vary, but at least python side shouldn't crash.
        assert 'return {"Hello": "World"}' in args

# Test 4: Next.js Generation (Mocked)
def test_generate_nextjs_mocked(initializer, tmp_path):
    config = {
        "project_name": "My Frontend",
        "target_dir": str(tmp_path),
        "stack": "nextjs"
    }
    
    with patch("alpha.initializer.subprocess.run") as mock_run:
        initializer.generate_project(config)
        
        args = mock_run.call_args[0][0]
        # Kebab case
        assert "my-frontend" in args
        assert "create-next-app" in args

# Test 5: Sanitization Logic
def test_sanitization_snake_case():
    init = ProjectInitializer()
    config = {"project_name": "Test Project-One", "stack": "django", "target_dir": "."}
    
    with patch("alpha.initializer.subprocess.run") as mock_run:
        init.generate_project(config)
        args = mock_run.call_args[0][0]
        assert "test_project_one" in args

def test_sanitization_kebab_case():
    init = ProjectInitializer()
    config = {"project_name": "Test Project_One", "stack": "react", "target_dir": "."}
    
    with patch("alpha.initializer.subprocess.run") as mock_run:
        init.generate_project(config)
        args = mock_run.call_args[0][0]
        assert "test-project-one" in args

# Test 6: Cross Platform Path logic (Mocking OS)
def test_cross_platform_paths():
    init = ProjectInitializer()
    
    with patch("os.name", "posix"):
        with patch("alpha.initializer.subprocess.run") as mock_run:
            cmd_windows = "python -m venv venv && venv\\Scripts\\pip install x"
            init._run_command(cmd_windows, Path("."))
            
            args = mock_run.call_args[0][0]
            # Should have replaced Scripts with bin
            assert "venv/bin/pip" in args
