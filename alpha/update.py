import requests
import webbrowser
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from alpha.version import __version__, GITHUB_REPO

class UpdateChecker(QThread):
    update_available = pyqtSignal(str, str) # version, url

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
        except Exception:
            pass

    def _is_newer(self, latest, current):
        try:
            # Simple semantic versioning check (x.y.z)
            l_parts = [int(x) for x in latest.split(".")]
            c_parts = [int(x) for x in current.split(".")]
            return l_parts > c_parts
        except:
            return False

def show_update_dialog(parent, version, url):
    msg = QMessageBox(parent)
    msg.setWindowTitle("Update Available")
    msg.setText(f"A new version (v{version}) is available!")
    msg.setInformativeText("Would you like to view the release page?")
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setDefaultButton(QMessageBox.StandardButton.Yes)
    
    if msg.exec() == QMessageBox.StandardButton.Yes:
        webbrowser.open(url)
