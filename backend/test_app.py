import io
import subprocess
import app as app_module


def test_no_file_uploaded():
    client = app_module.app.test_client()

    response = client.post("/analyze", data={})

    assert response.status_code == 200
    assert response.get_json() == {
        "success": False,
        "error": "No file uploaded."
    }


def test_empty_filename():
    client = app_module.app.test_client()

    response = client.post(
        "/analyze",
        data={
            "file": (io.BytesIO(b""), "")
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "success": False,
        "error": "No file selected."
    }


def test_compiler_not_found(monkeypatch, tmp_path):
    client = app_module.app.test_client()
    missing_compiler = tmp_path / "missing.exe"

    monkeypatch.setattr(
        app_module, "COMPILER", missing_compiler
    )

    response = client.post(
        "/analyze",
        data={
            "file": (
                io.BytesIO(b"int main() { return 0; }"),
                "sample.cpp"
            )
        },
        content_type="multipart/form-data"
    )

    result = response.get_json()

    assert response.status_code == 200
    assert result["success"] is False
    assert result["error"] == "green_compiler.exe not found."
    assert result["expected_path"] == str(missing_compiler)


def test_successful_analysis(monkeypatch, tmp_path):
    client = app_module.app.test_client()

    monkeypatch.setattr(
        app_module, "ANALYZER_DIR", tmp_path
    )

    compiler = tmp_path / "green_compiler.exe"
    compiler.touch()

    monkeypatch.setattr(
        app_module, "COMPILER", compiler
    )

    def fake_run(*args, **kwargs):
        result_file = tmp_path / "analysis_result.txt"

        result_file.write_text(
            "Green Compiler Analysis Report\n"
            "Line 2: 15.5\n"
            "Line 4: 20.0\n",
            encoding="utf-8"
        )

        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="Analysis completed",
            stderr=""
        )

    monkeypatch.setattr(
        app_module.subprocess, "run", fake_run
    )

    source_code = "int main() { return 0; }"

    response = client.post(
        "/analyze",
        data={
            "file": (
                io.BytesIO(source_code.encode("utf-8")),
                "sample.cpp"
            )
        },
        content_type="multipart/form-data"
    )

    result = response.get_json()

    assert response.status_code == 200
    assert result["success"] is True
    assert "Green Compiler Analysis Report" in result["report"]
    assert result["console"] == "Analysis completed"
    assert result["source_code"] == source_code
    assert result["line_energy"] == [
        {"line": 2, "energy": 15.5},
        {"line": 4, "energy": 20.0}
    ]
    assert list(tmp_path.glob("upload_*.cpp")) == []


def test_analyzer_failure(monkeypatch, tmp_path):
    client = app_module.app.test_client()

    monkeypatch.setattr(
        app_module, "ANALYZER_DIR", tmp_path
    )

    compiler = tmp_path / "green_compiler.exe"
    compiler.touch()

    monkeypatch.setattr(
        app_module, "COMPILER", compiler
    )

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr="Compilation failed"
        )

    monkeypatch.setattr(
        app_module.subprocess, "run", fake_run
    )

    response = client.post(
        "/analyze",
        data={
            "file": (
                io.BytesIO(b"invalid C++ code"),
                "sample.cpp"
            )
        },
        content_type="multipart/form-data"
    )

    result = response.get_json()

    assert response.status_code == 200
    assert result["success"] is False
    assert result["error"] == "C++ analyzer failed."
    assert result["return_code"] == 1
    assert result["stdout"] == ""
    assert result["stderr"] == "Compilation failed"
    assert list(tmp_path.glob("upload_*.cpp")) == []


def test_missing_report(monkeypatch, tmp_path):
    client = app_module.app.test_client()

    monkeypatch.setattr(
        app_module, "ANALYZER_DIR", tmp_path
    )

    compiler = tmp_path / "green_compiler.exe"
    compiler.touch()

    monkeypatch.setattr(
        app_module, "COMPILER", compiler
    )

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="Analyzer completed",
            stderr=""
        )

    monkeypatch.setattr(
        app_module.subprocess, "run", fake_run
    )

    response = client.post(
        "/analyze",
        data={
            "file": (
                io.BytesIO(b"int main() { return 0; }"),
                "sample.cpp"
            )
        },
        content_type="multipart/form-data"
    )

    result = response.get_json()

    assert response.status_code == 200
    assert result["success"] is False
    assert result["error"] == (
        "Analyzer ran but result file was not created."
    )
    assert result["stdout"] == "Analyzer completed"
    assert list(tmp_path.glob("upload_*.cpp")) == []


def test_analyzer_timeout(monkeypatch, tmp_path):
    client = app_module.app.test_client()

    monkeypatch.setattr(
        app_module, "ANALYZER_DIR", tmp_path
    )

    compiler = tmp_path / "green_compiler.exe"
    compiler.touch()

    monkeypatch.setattr(
        app_module, "COMPILER", compiler
    )

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=args[0],
            timeout=15
        )

    monkeypatch.setattr(
        app_module.subprocess, "run", fake_run
    )

    response = client.post(
        "/analyze",
        data={
            "file": (
                io.BytesIO(b"int main() { return 0; }"),
                "sample.cpp"
            )
        },
        content_type="multipart/form-data"
    )

    result = response.get_json()

    assert response.status_code == 200
    assert result["success"] is False
    assert result["error"] == (
        "C++ analyzer took too long to respond."
    )
    assert list(tmp_path.glob("upload_*.cpp")) == []


def test_unexpected_exception(monkeypatch, tmp_path):
    client = app_module.app.test_client()

    monkeypatch.setattr(
        app_module, "ANALYZER_DIR", tmp_path
    )

    compiler = tmp_path / "green_compiler.exe"
    compiler.touch()

    monkeypatch.setattr(
        app_module, "COMPILER", compiler
    )

    def fake_run(*args, **kwargs):
        raise RuntimeError("Simulated unexpected error")

    monkeypatch.setattr(
        app_module.subprocess, "run", fake_run
    )

    response = client.post(
        "/analyze",
        data={
            "file": (
                io.BytesIO(b"int main() { return 0; }"),
                "sample.cpp"
            )
        },
        content_type="multipart/form-data"
    )

    result = response.get_json()

    assert response.status_code == 200
    assert result["success"] is False
    assert result["error"] == (
        "An unexpected error occurred during analysis."
    )
    assert list(tmp_path.glob("upload_*.cpp")) == []


def test_energy_report_parsing(monkeypatch, tmp_path):
    client = app_module.app.test_client()

    monkeypatch.setattr(
        app_module, "ANALYZER_DIR", tmp_path
    )

    compiler = tmp_path / "green_compiler.exe"
    compiler.touch()

    monkeypatch.setattr(
        app_module, "COMPILER", compiler
    )

    def fake_run(*args, **kwargs):
        result_file = tmp_path / "analysis_result.txt"

        result_file.write_text(
            "Green Compiler Analysis Report\n"
            "Line 1: 10\n"
            "Line 3: 25.75\n"
            "Line 5: 0.5\n",
            encoding="utf-8"
        )

        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="Analysis completed",
            stderr=""
        )

    monkeypatch.setattr(
        app_module.subprocess, "run", fake_run
    )

    response = client.post(
        "/analyze",
        data={
            "file": (
                io.BytesIO(b"int main() { return 0; }"),
                "sample.cpp"
            )
        },
        content_type="multipart/form-data"
    )

    result = response.get_json()

    assert response.status_code == 200
    assert result["success"] is True
    assert result["line_energy"] == [
        {"line": 1, "energy": 10.0},
        {"line": 3, "energy": 25.75},
        {"line": 5, "energy": 0.5}
    ]






