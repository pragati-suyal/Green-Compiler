 🌱 Green Compiler — The Silent Energy Crisis

A static C++ code analysis tool that detects energy-intensive programming patterns and provides optimization recommendations.

 🚀 Project Overview

Green Compiler analyzes C++ source code without executing it.

It identifies patterns that may increase computational energy usage, calculates software metrics, estimates an energy consumption score, and provides optimization suggestions.

✨ Features

- 🔍 Static analysis of C++ source code
- 🔄 Loop detection
- 🔁 Nested loop detection
- 📥📤 Input/Output operation detection
- 🧠 Recursion detection
- 📊 Cyclomatic Complexity
- 📐 Halstead Volume
- ⚡ Energy Consumption Score
- 🟢🟡🔴 Energy classification: LOW / MEDIUM / HIGH
- 💡 Optimization recommendations
- 🌡️ Line-by-line energy heatmap
- 🌐 Flask-based web interface

 🛠️ Tech Stack

- C++
- Python
- Flask
- HTML
- CSS
- JavaScript
- Regular Expressions
- MSYS2 / MinGW

🏗️ Project Structure


Green-Compiler/
│
├── analyzer/
│   ├── energy_analyzer.cpp
│   ├── main.cpp
│   ├── green_compiler.exe
│   ├── low_test.cpp
│   ├── medium_test.cpp
│   └── recursion_test.cpp
│
└── backend/

⚙️ How It Works

C++ Source Code
       ↓
Static Code Analysis
       ↓
Pattern Detection
       ↓
Software Metrics
       ↓
Energy Score Calculation
       ↓
Energy Level
       ↓
Optimization Recommendations
       ↓
Visual Heatmap

⚡ Energy Analysis

The project uses a static heuristic scoring model.

Different code patterns are assigned estimated energy-cost weights:

1. Loops
2. Nested loops
3. Input/Output operations
4. Conditions
5. Recursion

The final score is used to classify code as:

Score	  Energy Level
< 50	    LOW
50–119	  MEDIUM
≥ 120	     HIGH

Note: The energy score is a static heuristic estimate. It does not represent measured electricity consumption, joules, or actual hardware power usage.

📊 Software Metrics

Cyclomatic Complexity

Measures the logical complexity of the program based on control-flow constructs such as:

1. if
2. for
3. while
4. case
5. logical operators

Halstead Volume

Estimates program size and complexity using operators and operands..

🧪 Testing

The project was tested using:

(i) LOW energy test
(ii) MEDIUM energy test
(iii) HIGH energy test
(iv) Recursive function test

Example results:

Test	           Energy Score      	Level
Low Test	           5	             LOW
Medium Test        	70	             MEDIUM
Complex Test	      240            	  HIGH

🌐 Web Interface

The Flask backend connects the C++ analyzer with the web interface.

Users can upload a .cpp file and receive:

1. Energy score
2. Energy level
3. Code metrics
4. Recommendations
5. Line-by-line energy analysis


🔮 Future Enhancements
(i) More accurate energy estimation
(ii) AST-based C++ analysis
(iii) Machine-learning-based energy prediction
(iv) Support for additional programming languages
(v) Cloud deployment
(vi) Interactive charts and analytics
(vii) Real hardware energy measurement integration

👩‍💻 Author

Pragati Suyal
B.Tech Computer Science & Engineering
    ├── app.py
    └── templates/
        └── index.html
