"""Auto-update checker for GitHub releases."""
import sys
import requests
import webbrowser
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import QThread, pyqtSignal
from alpha.version import __version__, GITHUB_REPO


class UpdateChecker(QThread):
    """Background thread to check for updates."""
    update_available = pyqtSignal(str, str)  # version, url
    no_update = pyqtSignal()

    def run(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get("tag_name", "").lstrip("v")
                html_url = data.get("html_url", "")
                
                if self._is_newer(latest_tag, __version__):
                    self.update_available.emit(latest_tag, html_url)
                else:
                    self.no_update.emit()
            else:
                self.no_update.emit()
        except Exception:
            self.no_update.emit()

    def _is_newer(self, latest, current):
        try:
            # Semantic versioning check (x.y.z)
            l_parts = [int(x) for x in latest.split(".")]
            c_parts = [int(x) for x in current.split(".")]
            return l_parts > c_parts
        except:
            return False


def check_for_updates_blocking():
    """
    Synchronous update check. Returns (is_update_available, version, url).
    Used at startup before showing main window.
    """
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_tag = data.get("tag_name", "").lstrip("v")
            html_url = data.get("html_url", "")
            
            # Compare versions
            l_parts = [int(x) for x in latest_tag.split(".")]
            c_parts = [int(x) for x in __version__.split(".")]
            
            if l_parts > c_parts:
                return True, latest_tag, html_url
    except Exception:
        pass
    
    return False, None, None


def show_forced_update_dialog(version, url):
    """
    Show a forced update dialog. User MUST update.
    After clicking OK, opens browser and exits app.
    """
    msg = QMessageBox()
    msg.setWindowTitle("Update Required")
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setText(f"A new version (v{version}) is available!")
    msg.setInformativeText(
        "This update is required to continue.\n\n"
        "Click OK to open the download page.\n"
        "The application will now close."
    )
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setDefaultButton(QMessageBox.StandardButton.Ok)
    
    msg.exec()
    
    # Open browser and exit
    webbrowser.open(url)
    sys.exit(0)


def show_optional_update_dialog(parent, version, url):
    """Show an optional update dialog (legacy behavior)."""
    msg = QMessageBox(parent)
    msg.setWindowTitle("Update Available")
    msg.setText(f"A new version (v{version}) is available!")
    msg.setInformativeText("Would you like to view the release page?")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setDefaultButton(QMessageBox.StandardButton.Yes)
    
    if msg.exec() == QMessageBox.StandardButton.Yes:
        webbrowser.open(url)
