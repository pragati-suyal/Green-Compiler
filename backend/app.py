from flask import Flask, request, jsonify, render_template
from pathlib import Path
import subprocess
import uuid
import os
import re

app = Flask(__name__)


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

ANALYZER_DIR = BASE_DIR / "analyzer"

COMPILER = ANALYZER_DIR / "green_compiler.exe"


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# ANALYZE C++ CODE
# ==========================================

@app.route("/analyze", methods=["POST"])
def analyze():

    # --------------------------------------
    # CHECK FILE
    # --------------------------------------

    if "file" not in request.files:

        return jsonify({
            "success": False,
            "error": "No file uploaded."
        })


    uploaded_file = request.files["file"]


    if uploaded_file.filename == "":

        return jsonify({
            "success": False,
            "error": "No file selected."
        })


    # --------------------------------------
    # CHECK COMPILER
    # --------------------------------------

    if not COMPILER.exists():

        return jsonify({
            "success": False,
            "error": "green_compiler.exe not found.",
            "expected_path": str(COMPILER)
        })


    # --------------------------------------
    # CREATE TEMP FILE
    # --------------------------------------

    temp_name = (
        "upload_" +
        uuid.uuid4().hex +
        ".cpp"
    )


    file_path = ANALYZER_DIR / temp_name

    result_file = (
        ANALYZER_DIR /
        "analysis_result.txt"
    )


    try:

        # ----------------------------------
        # SAVE UPLOADED C++ FILE
        # ----------------------------------

        uploaded_file.save(file_path)


        # ----------------------------------
        # READ ORIGINAL SOURCE CODE
        # ----------------------------------

        source_code = file_path.read_text(
            encoding="utf-8",
            errors="replace"
        )


        # ----------------------------------
        # REMOVE OLD RESULT
        # ----------------------------------

        if result_file.exists():

            result_file.unlink()


        # ----------------------------------
        # ENVIRONMENT
        # ----------------------------------

        env = os.environ.copy()


        msys_bin = r"C:\msys64\ucrt64\bin"


        if os.path.exists(msys_bin):

            env["PATH"] = (
                msys_bin +
                os.pathsep +
                env.get("PATH", "")
            )


        # ----------------------------------
        # RUN C++ ANALYZER
        # ----------------------------------

        process = subprocess.run(

            [str(COMPILER)],

            input=temp_name + "\n",

            text=True,

            capture_output=True,

            cwd=str(ANALYZER_DIR),

            env=env,

            timeout=15
        )


        # ----------------------------------
        # CHECK PROCESS
        # ----------------------------------

        if process.returncode != 0:

            return jsonify({

                "success": False,

                "error":
                    "C++ analyzer failed.",

                "return_code":
                    process.returncode,

                "stdout":
                    process.stdout,

                "stderr":
                    process.stderr
            })


        # ----------------------------------
        # CHECK RESULT FILE
        # ----------------------------------

        if not result_file.exists():

            return jsonify({

                "success": False,

                "error":
                    "Analyzer ran but result file was not created.",

                "stdout":
                    process.stdout,

                "stderr":
                    process.stderr
            })


        # ----------------------------------
        # READ REPORT
        # ----------------------------------

        report = result_file.read_text(

            encoding="utf-8",

            errors="replace"
        )


        # ==================================
        # PARSE LINE ENERGY
        # ==================================

        line_energy = []


        for report_line in report.splitlines():

            match = re.match(

                r"Line\s+(\d+)\s*:\s*([0-9.]+)",

                report_line.strip()
            )


            if match:

                line_number = int(
                    match.group(1)
                )

                energy_value = float(
                    match.group(2)
                )


                line_energy.append({

                    "line": line_number,

                    "energy": energy_value
                })


        # ==================================
        # RETURN EVERYTHING TO FRONTEND
        # ==================================

        return jsonify({

            "success": True,

            "report": report,

            "console": process.stdout,

            "source_code": source_code,

            "line_energy": line_energy

        })


    # ======================================
    # TIMEOUT
    # ======================================

    except subprocess.TimeoutExpired:

        return jsonify({

            "success": False,

            "error":
                "C++ analyzer took too long to respond."
        })


    # ======================================
    # OTHER ERROR
    # ======================================

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)
        })


    # ======================================
    # DELETE TEMP FILE
    # ======================================

    finally:

        if file_path.exists():

            file_path.unlink()


# ==========================================
# START FLASK
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
