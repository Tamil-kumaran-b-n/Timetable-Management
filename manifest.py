import sys
import os
import json

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.abspath(os.path.dirname(__file__))

def load_manifest():
    default_manifest = {
        "app_name": "Smart Academic Timetable Management System",
        "version": "1.0.0",
        "build_commit": "main",
        "github_repo": "Tamil-kumaran-b-n/Timetable-Management",
        "release_url": "https://github.com/Tamil-kumaran-b-n/Timetable-Management/releases",
        "developers": [
            "Tamil Kumaran (BCA Year 3)",
            "Haridharan (BCA Year 3)",
            "Bakthavasalam (BCA Year 3)"
        ],
        "assisted_by": [
            "Joshua Thomas (External)",
            "Antigravity",
            "Codex"
        ],
        "tech_stack": [
            "Made entirely in Python",
            "UI Framework: PySide6"
        ]
    }
    manifest_path = os.path.join(get_base_dir(), 'manifest.json')
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                default_manifest.update(data)
        except Exception:
            pass
    return default_manifest

MANIFEST = load_manifest()
