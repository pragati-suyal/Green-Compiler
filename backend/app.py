
from flask import Flask, request, jsonify, render_template
from pathlib import Path
import subprocess
import uuid
import os
import re

app = Flask(__name__)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
ANALYZER_DIR = BASE_DIR / "analyzer"
COMPILER = ANALYZER_DIR / "green_compiler.exe"


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Analyze uploaded C++ code
@app.route("/analyze", methods=["POST"])
def analyze():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "No file uploaded."
        })

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:
        return jsonify({
            "success": False,
            "error": "No file selected."
        })

    if not COMPILER.exists():
        return jsonify({
            "success": False,
            "error": "green_compiler.exe not found.",
            "expected_path": str(COMPILER)
        })

    temp_name = f"upload_{uuid.uuid4().hex}.cpp"
    file_path = ANALYZER_DIR / temp_name
    result_file = ANALYZER_DIR / "analysis_result.txt"

    try:
        ANALYZER_DIR.mkdir(parents=True, exist_ok=True)

        uploaded_file.save(file_path)

        source_code = file_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        # Remove any previous report
        if result_file.exists():
            result_file.unlink()

        # Configure compiler environment
        env = os.environ.copy()
        msys_bin = r"C:\msys64\ucrt64\bin"

        if os.path.exists(msys_bin):
            env["PATH"] = (
                msys_bin
                + os.pathsep
                + env.get("PATH", "")
            )

        # Run the analyzer
        process = subprocess.run(
            [str(COMPILER)],
            input=temp_name + "\n",
            text=True,
            capture_output=True,
            cwd=str(ANALYZER_DIR),
            env=env,
            timeout=15
        )

        if process.returncode != 0:
            return jsonify({
                "success": False,
                "error": "C++ analyzer failed.",
                "return_code": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr
            })

        if not result_file.exists():
            return jsonify({
                "success": False,
                "error": "Analyzer ran but result file was not created.",
                "stdout": process.stdout,
                "stderr": process.stderr
            })

        report = result_file.read_text(
            encoding="utf-8",
            errors="replace"
        )

        # Parse report lines such as:
        # Line 2: 15.5
        line_energy = []

        pattern = re.compile(
            r"Line\s+(\d+)\s*:\s*([0-9]+(?:\.[0-9]+)?)"
        )

        for report_line in report.splitlines():
            match = pattern.match(report_line.strip())

            if match:
                line_energy.append({
                    "line": int(match.group(1)),
                    "energy": float(match.group(2))
                })

        return jsonify({
            "success": True,
            "report": report,
            "console": process.stdout,
            "source_code": source_code,
            "line_energy": line_energy
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "C++ analyzer took too long to respond."
        })

    except Exception:
        app.logger.exception("Analysis failed")

        return jsonify({
            "success": False,
            "error": "An unexpected error occurred during analysis."
        })

    finally:
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                app.logger.exception("Could not delete temporary upload")


if __name__ == "__main__":
    app.run(debug=True)
