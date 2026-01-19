# ALPHA Init Tool

**ALPHA** is a modern, modular project scaffolding tool designed for rapid stack initialization.

![Version](https://img.shields.io/badge/version-1.6.0-purple)
![License](https://img.shields.io/badge/license-Open%20Source-blue)

## Features

- **Dynamic Stack Config**: Add/Edit stacks via GUI (`commands.json`)
- **Multi-Framework Support**: Django, FastAPI, Next.js, React, Vue, and more
- **Docker Ready**: Auto-generates Dockerfile and docker-compose.yml
- **Modern UI**: Dark-themed PyQt6 interface with splash screen
- **Auto-Update**: Automatically notifies you of new releases on startup

## Installation

### Option 1: Windows Installer (Recommended)

1. Download the latest `ALPHA_Installer_vX.X.X.exe` from [Releases](https://github.com/logando-al/alpha/releases)
2. Run the installer
3. Launch ALPHA from the Start Menu or Desktop shortcut

### Option 2: From Source

```bash
# Clone the repository
git clone https://github.com/logando-al/alpha.git
cd alpha

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

1. **Enter Project Name**: Give your project a descriptive name
2. **Select Target Directory**: Choose where to create the project
3. **Choose Tech Stack**: Select from Django, FastAPI, Next.js, React, Vue, etc.
4. **Optional - UI Framework**: For JS projects, add Tailwind, Shadcn, etc.
5. **Optional - Docker**: Enable Docker containerization
6. Click **Initialize Project** and wait for completion!

## Supported Stacks

| Stack | Type | Command |
|-------|------|---------|
| Django | Python | Creates venv, installs Django, runs startproject |
| FastAPI | Python | Creates venv, installs FastAPI + Uvicorn |
| Next.js | JavaScript | `npx create-next-app@latest` |
| React | JavaScript | `npm create vite@latest` with React template |
| Vue | JavaScript | `npm create vite@latest` with Vue template |
| PyQt6 | Python | Creates venv with PyQt6 |

## Custom Stacks

Click **Manage** next to the stack dropdown to add your own stack configurations!

## Auto-Update

ALPHA automatically checks for updates on startup. If a new version is available, you'll be prompted to download it from the releases page.

## Credits

Developed by **logando-al** | Open Source

### Superpower Framework

The bundled Superpower Framework for Google Antigravity IDE is developed by **anthonylee991**.

🔗 [gemini-superpowers-antigravity](https://github.com/anthonylee991/gemini-superpowers-antigravity)
