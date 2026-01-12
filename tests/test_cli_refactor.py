import pytest
from unittest.mock import patch, call, MagicMock
from pathlib import Path
from alpha.initializer import ProjectInitializer

# We are testing the NEW behavior where ProjectInitializer uses subprocess logic.
# This might require a new class or refactoring the existing one.
# For TDD, we assume we will refactor the existing class.

@pytest.fixture
def mock_subprocess():
    with patch("alpha.initializer.subprocess.run") as mock_run:
        yield mock_run

def test_nextjs_cli_command(mock_subprocess, tmp_path):
    """Verify Next.js initialization runs npx create-next-app."""
    initializer = ProjectInitializer()
    
    config = {
        "project_name": "my-next-app",
        "target_dir": str(tmp_path),
        "stack": "nextjs",
        "use_docker": False, # Focus on CLI first
        "ui_framework": None
    }
    
    initializer.generate_project(config)
    
    # Assert npx command was called
    # Expected: npx create-next-app@latest my-next-app --yes --use-npm (or similar)
    # We check if *any* call matches the core command
    
    calls = mock_subprocess.call_args_list
    command_found = False
    for c in calls:
        cmd_args = c[0][0] # First arg of run() is the command list/str
        if "npx" in cmd_args and "create-next-app@latest" in cmd_args and "my-next-app" in cmd_args:
            command_found = True
            break
            
    assert command_found, "npx create-next-app was not called"

def test_django_venv_workflow(mock_subprocess, tmp_path):
    """Verify Django initialization creates venv and installs django."""
    initializer = ProjectInitializer()
    
    config = {
        "project_name": "my-django-app",
        "target_dir": str(tmp_path),
        "stack": "django",
    }
    
    # We need to mock Path.exists/mkdir if the code checks for directories before running commands
    # But usually subprocess runs first for creation? 
    # Actually for venv, we create the dir first often.
    
    initializer.generate_project(config)
    
    calls = mock_subprocess.call_args_list
    
    # 1. Check for venv creation
    # cmd: python -m venv venv
    venv_called = any("venv" in c[0][0] and "-m" in c[0][0] for c in calls)
    assert venv_called, "python -m venv was not called"
    
    # 2. Check for pip install django
    # It should use the venv pip. On windows: venv\Scripts\pip
    # We'll just check for 'install' and 'django' in the same command
    install_called = any("install" in c[0][0] and "django" in c[0][0] for c in calls)
    assert install_called, "pip install django was not called"
    
    # 3. Check for startproject
    start_called = any("startproject" in c[0][0] and "my-django-app" in c[0][0] for c in calls)
    assert start_called, "django-admin startproject was not called"

def test_fastapi_manual_creation(mock_subprocess, tmp_path):
    """Verify FastAPI creates files manually + venv."""
    initializer = ProjectInitializer()
    config = {
        "project_name": "my-fastapi-app",
        "target_dir": str(tmp_path),
        "stack": "fastapi",
    }
    
    initializer.generate_project(config)
    
    project_root = tmp_path / "my-fastapi-app"
    
    # 1. Verify Venv (Mocked subprocess)
    venv_called = any("venv" in c[0][0] for c in mock_subprocess.call_args_list)
    assert venv_called
    
    # 2. Verify File Creation (Real file check in tmp_path)
    # Since the code *should* write these files:
    assert (project_root / "main.py").exists()
    assert (project_root / "requirements.txt").exists()
    
    # 3. Verify Pip Install
    install_reqs = any("install" in c[0][0] and "fastapi" in c[0][0] for c in mock_subprocess.call_args_list)
    assert install_reqs
