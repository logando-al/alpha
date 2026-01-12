from alpha.initializer import ProjectInitializer
from pathlib import Path
import shutil

# Setup
PROJECT_NAME = "Test-NextJS-Fix"
TARGET = Path("C:/Users/logan/Documents/ALPHA-Init/_manual_test_fix")
if TARGET.exists():
    shutil.rmtree(TARGET)
TARGET.mkdir()

config = {
    "project_name": PROJECT_NAME,
    "target_dir": str(TARGET),
    "stack": "nextjs",
    "use_docker": True,
    "ui_framework": "tailwind"
}

# Run
print("Running Initializer...")
initializer = ProjectInitializer()
initializer.generate_project(config)

# Verify
project_path = TARGET / PROJECT_NAME
files = list(project_path.glob("**/*"))
print(f"Generated {len(files)} files/dirs at {project_path}")
for f in files:
    print(f" - {f.relative_to(project_path)}")

# specific checks
has_package = (project_path / "package.json").exists()
has_pages = (project_path / "pages").exists()
print(f"Has package.json: {has_package}")
print(f"Has pages/: {has_pages}")
