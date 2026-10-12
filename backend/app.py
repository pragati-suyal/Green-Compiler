
from flask import Flask, request, jsonify, render_template
from pathlib import Path
import subprocess
import uuid
import os
import re
import threading

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent.parent
ANALYZER_DIR = BASE_DIR / "analyzer"
COMPILER = ANALYZER_DIR / "green_compiler.exe"
REPORT_FILE = ANALYZER_DIR / "analysis_result.txt"

# Prevent simultaneous runs from overwriting the same report.
ANALYZER_LOCK = threading.Lock()

MSYS_BIN = r"C:\msys64\ucrt64\bin"


def validate_upload(file_storage):
    if file_storage is None or not file_storage.filename:
        raise ValueError("Please select a C++ source file.")

    suffix = Path(file_storage.filename).suffix.lower()

    if suffix not in {".cpp", ".cc", ".cxx"}:
        raise ValueError("Please upload a valid C++ source file.")

    return suffix


def analyze_file(file_storage):
    """Run the existing C++ analyzer and parse its report."""
    validate_upload(file_storage)

    if not COMPILER.is_file():
        raise FileNotFoundError(
            f"Analyzer executable not found: {COMPILER}"
        )

    ANALYZER_DIR.mkdir(parents=True, exist_ok=True)

    temp_name = f"upload_{uuid.uuid4().hex}.cpp"
    file_path = ANALYZER_DIR / temp_name

    try:
        file_storage.save(file_path)

        source_code = file_path.read_text(
            encoding="utf-8",
            errors="replace"
        )

        env = os.environ.copy()

        if os.path.isdir(MSYS_BIN):
            env["PATH"] = (
                MSYS_BIN + os.pathsep + env.get("PATH", "")
            )

        # The analyzer writes to one fixed report file.
        with ANALYZER_LOCK:
            if REPORT_FILE.exists():
                REPORT_FILE.unlink()

            process = subprocess.run(
                [str(COMPILER)],
                input=temp_name + "\n",
                text=True,
                capture_output=True,
                cwd=str(ANALYZER_DIR),
                env=env,
                timeout=15,
                check=False,
            )

            if process.returncode != 0:
                details = (
                    process.stderr.strip()
                    or process.stdout.strip()
                )

                raise RuntimeError(
                    "C++ analyzer failed. "
                    f"Return code: {process.returncode}. "
                    f"Details: {details}"
                )

            if not REPORT_FILE.is_file():
                raise RuntimeError(
                    "Analyzer ran, but analysis_result.txt "
                    "was not created."
                )

            report = REPORT_FILE.read_text(
                encoding="utf-8",
                errors="replace"
            )

        score_match = re.search(
            r"Energy Consumption Score\s*:\s*"
            r"([0-9]+(?:\.[0-9]+)?)",
            report,
            re.IGNORECASE,
        )

        level_match = re.search(
            r"Energy Level\s*:\s*(LOW|MEDIUM|HIGH)\b",
            report,
            re.IGNORECASE,
        )

        line_energy = []

        line_pattern = re.compile(
            r"^\s*Line\s+(\d+)\s*:\s*"
            r"([0-9]+(?:\.[0-9]+)?)\s*$",
            re.IGNORECASE,
        )

        for report_line in report.splitlines():
            match = line_pattern.match(report_line)

            if match:
                line_energy.append({
                    "line": int(match.group(1)),
                    "energy": float(match.group(2)),
                })

        return {
            "report": report,
            "console": process.stdout,
            "source_code": source_code,
            "energy_score": (
                float(score_match.group(1))
                if score_match else None
            ),
            "energy_level": (
                level_match.group(1).upper()
                if level_match else None
            ),
            "line_energy": line_energy,
        }

    finally:
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            app.logger.exception(
                "Could not delete temporary upload"
            )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "No file uploaded."
        }), 400

    try:
        result = analyze_file(request.files["file"])

        return jsonify({
            "success": True,
            **result
        }), 200

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except FileNotFoundError as exc:
        app.logger.error("%s", exc)

        return jsonify({
            "success": False,
            "error": "green_compiler.exe not found.",
            "expected_path": str(COMPILER),
        }), 500

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "C++ analyzer took too long to respond."
        }), 504

    except RuntimeError as exc:
        app.logger.error("Analysis failed: %s", exc)

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

    except Exception:
        app.logger.exception("Analysis failed")

        return jsonify({
            "success": False,
            "error": (
                "An unexpected error occurred during analysis."
            )
        }), 500


@app.route("/compare", methods=["POST"])
def compare():
    if (
        "baseline_file" not in request.files
        or "optimized_file" not in request.files
    ):
        return jsonify({
            "success": False,
            "error": (
                "Upload both baseline_file and optimized_file."
            )
        }), 400

    try:
        # Analyze both files sequentially.
        baseline = analyze_file(
            request.files["baseline_file"]
        )

        optimized = analyze_file(
            request.files["optimized_file"]
        )

        baseline_score = baseline["energy_score"]
        optimized_score = optimized["energy_score"]

        if (
            baseline_score is None
            or optimized_score is None
        ):
            return jsonify({
                "success": False,
                "error": (
                    "Could not find the Energy Consumption "
                    "Score in one of the reports."
                )
            }), 500

        reduction = None

        if baseline_score != 0:
            reduction = (
                (baseline_score - optimized_score)
                / baseline_score
            ) * 100

        return jsonify({
            "success": True,

            "baseline": {
                "energy_score": baseline_score,
                "energy_level": baseline["energy_level"],
            },

            "optimized": {
                "energy_score": optimized_score,
                "energy_level": optimized["energy_level"],
            },

            "score_reduction_percent": reduction,

            "metric_note": (
                "Percentage change in the static heuristic "
                "score only; not measured electricity or joules."
            ),
        }), 200

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except FileNotFoundError as exc:
        app.logger.error("%s", exc)

        return jsonify({
            "success": False,
            "error": "green_compiler.exe not found.",
            "expected_path": str(COMPILER),
        }), 500

    except subprocess.TimeoutExpired:
        return jsonify({
            "success": False,
            "error": "C++ analyzer took too long to respond."
        }), 504

    except RuntimeError as exc:
        app.logger.error("Comparison failed: %s", exc)

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

    except Exception:
        app.logger.exception("Comparison failed")

        return jsonify({
            "success": False,
            "error": (
                "An unexpected error occurred during comparison."
            )
        }), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "error": "File is too large. Maximum upload size is 1 MB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True)
