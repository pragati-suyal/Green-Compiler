# 🌱 Green Compiler
### The Silent Energy Crisis — Analyze Code, Think Green

Green Compiler is a static code analysis project that estimates the potential energy cost of C++ programs using heuristic rules. It helps developers identify potentially expensive coding patterns and explore ways to write more efficient code.

**Note:** Green Compiler generates a heuristic score. It does not directly measure electricity consumption, power usage, or energy in joules.

## 🚀 Features

- **Energy Consumption Score:** Estimates code cost using predefined heuristic rules.
- **Loop Detection:** Identifies loops and potentially expensive nested-loop patterns.
- **Input/Output Analysis:** Detects common I/O operations such as `cin`, `cout`, `printf`, and `scanf`.
- **Condition Analysis:** Identifies conditional constructs.
- **Recursion Detection:** Uses heuristic checks to identify possible recursion.
- **Code Metrics:** Displays metrics such as cyclomatic complexity and Halstead volume.
- **Line Energy Analysis:** Shows estimated energy-cost contributions by source-code line.
- **Before vs. After Comparison:** Compares heuristic scores for original and optimized C++ programs.
- **Optimization Recommendations:** Highlights code patterns that may benefit from optimization.
- **Visual Analysis:** Presents analysis results through a web interface.

## 🛠️ Tech Stack

- **C++** — Static code analysis and heuristic scoring
- **Python (Flask)** — Backend and web application
- **HTML, CSS, JavaScript** — User interface
- **Git and GitHub** — Version control and project hosting

## ⚙️ How It Works

1. The user uploads a C++ source file.
2. The backend processes the file using the C++ analysis engine.
3. The analyzer identifies selected code patterns and calculates a heuristic score.
4. The application displays the score, code metrics, line-level analysis, and recommendations.
5. Users can compare the scores of original and optimized versions of their code.

## 📊 Energy Scoring Model

The current heuristic model uses the following formula:

`Score = 10L + 25N + 50I + 5C + 30R + 5`

Where:

- `L` = Number of detected loops
- `N` = Estimated nested-loop count
- `I` = Detected input/output operations
- `C` = Detected conditional constructs
- `R` = Recursion indicator (1 if detected, otherwise 0)
- `5` = Base score

The score represents the project's rule-based estimate, not actual energy consumption. Results depend on the analyzer's detection rules and may not reflect runtime execution frequency or hardware behavior.

## 📈 Example: Before vs. After Optimization

An example comparison from the application:

| Metric | Before | After |
|---|---:|---:|
| Heuristic score | 100 | 65 |
| Score reduction | — | 35% |

The percentage reduction is calculated as:

`Reduction (%) = ((Before Score - After Score) / Before Score) × 100`

This example represents a reduction in the estimated heuristic score only. It does not establish a 35% reduction in real electricity consumption. The comparison is meaningful when both programs preserve the required behavior and are analyzed using the same scoring model.

## 💻 Getting Started

### Prerequisites

Install the following:

- Python 3
- A C++ compiler, such as GCC or MinGW on Windows
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/pragati-suyal/Green-Compiler.git
cd Green-Compiler
```

### 2. Create and Activate a Virtual Environment

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Python Dependencies

If the project contains a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Otherwise, install the dependencies listed in the project's backend code.

### 4. Compile the C++ Analyzer

Use the actual source path from your repository. For example, if the analyzer source is `analyzer/energy_analyzer.cpp`:

```bash
g++ analyzer/energy_analyzer.cpp -o green_compiler.exe
```

If your project uses multiple C++ source files, include all required source files in the compilation command.

### 5. Run the Flask Application

Run the following command from your project root:

```bash
python backend/app.py
```

Once the Flask server starts, open the application in your browser:

**Local URL:** http://127.0.0.1:5000

You can also access it at:

http://localhost:5000

Make sure the C++ analyzer executable and required dependencies are available before running the application.

## 📁 Project Structure

The following is an illustrative structure; adjust it to match the files actually present in your repository.

```text
Green-Compiler/
├── analyzer/
│   └── energy_analyzer.cpp
├── backend/
│   ├── app.py
│   └── templates/
│       └── index.html
├── .gitignore
└── README.md
```

## 🎯 Project Objective

The goal of Green Compiler is to encourage energy-conscious programming by highlighting potentially expensive code patterns and making code optimization easier to explore.

The project demonstrates how static analysis, heuristic scoring, C++, and a Flask-based interface can be combined into an educational software-analysis tool.

## 🔮 Future Improvements

- More robust C++ parsing using an Abstract Syntax Tree (AST)
- Improved detection of nested loops and recursion
- More accurate estimates based on execution paths and operation frequency
- Runtime benchmarking and hardware-based energy measurement
- Additional optimization suggestions with behavior-preserving examples
- Automated testing of original and optimized program outputs

## 👩‍💻 Author

**Pragati Suyal**

- GitHub: [pragati-suyal](https://github.com/pragati-suyal)
- LinkedIn: [Pragati Suyal](https://www.linkedin.com/in/pragati-suyal-8510ab296)

## 📄 Disclaimer

Green Compiler is an educational and experimental software-analysis project. Its heuristic scores are intended to support code analysis and optimization discussions. They should not be interpreted as verified measurements of real-world energy consumption.
