from pathlib import Path
import shutil
import subprocess


def export_html_to_pdf(html_path, pdf_path):

    edge_paths = [
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]

    edge_exe = next(
        (
            path for path in edge_paths
            if Path(path).exists()
        ),
        shutil.which("msedge")
    )

    if not edge_exe:

        print("Edge was not found; skipping PDF export.")

        return False

    html_url = Path(html_path).resolve().as_uri()

    command = [
        edge_exe,
        "--headless=new",
        "--disable-gpu",
        f"--print-to-pdf={pdf_path}",
        html_url
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=120
    )

    if completed.returncode != 0:

        print(
            "PDF export failed:",
            completed.stderr.strip() or completed.stdout.strip()
        )

        return False

    return True
