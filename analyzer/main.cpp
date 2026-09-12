#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include "energy_analyzer.cpp"

using namespace std;

int main()
{
    cout << "========================================\n";
    cout << "          GREEN COMPILER\n";
    cout << "       THE SILENT ENERGY CRISIS\n";
    cout << "========================================\n\n";

    string fileName;

    cout << "Enter C++ source file name: ";
    cin >> fileName;

    ifstream inputFile(fileName);

    if (!inputFile.is_open())
    {
        cout << "\nError: Could not open file.\n";
        cout << "Make sure the file is inside analyzer folder.\n";
        return 1;
    }

    string sourceCode;
    string line;

    while (getline(inputFile, line))
    {
        sourceCode += line;
        sourceCode += "\n";
    }

    inputFile.close();

    if (sourceCode.empty())
    {
        cout << "\nError: Source file is empty.\n";
        return 1;
    }

    EnergyAnalyzer analyzer(sourceCode);

    analyzer.analyze();

    int loops = analyzer.countLoops();
    int nestedLoops = analyzer.estimateNestedLoops();
    int conditions = analyzer.countConditions();
    int io = analyzer.countIO();

    bool recursion = analyzer.detectRecursion();

    int complexity =
        analyzer.calculateCyclomaticComplexity();

    double halstead =
        analyzer.calculateHalsteadVolume();

    double energy =
        analyzer.calculateEnergyScore();

    string energyLevel =
        analyzer.getEnergyLevel(energy);

    // LINE ENERGY
    vector<double> lineEnergy =
        analyzer.calculateLineEnergy();


    // RESULT FILE
    ofstream resultFile("analysis_result.txt");

    if (!resultFile.is_open())
    {
        cout << "\nError: Could not create result file.\n";
        return 1;
    }


    resultFile << "========================================\n";
    resultFile << "          GREEN COMPILER\n";
    resultFile << "       ENERGY ANALYSIS REPORT\n";
    resultFile << "========================================\n\n";

    resultFile << "Source File: "
               << fileName << "\n\n";


    // CODE ANALYSIS
    resultFile << "----------- CODE ANALYSIS --------------\n";

    resultFile << "Loops                  : "
               << loops << "\n";

    resultFile << "Nested Loops           : "
               << nestedLoops << "\n";

    resultFile << "Conditions             : "
               << conditions << "\n";

    resultFile << "Input/Output Operations: "
               << io << "\n";

    resultFile << "Recursion              : "
               << (recursion ? "YES" : "NO")
               << "\n\n";


    // SOFTWARE METRICS
    resultFile << "----------- SOFTWARE METRICS -----------\n";

    resultFile << "Cyclomatic Complexity  : "
               << complexity << "\n";

    resultFile << "Halstead Volume        : "
               << halstead << "\n\n";


    // ENERGY
    resultFile << "----------- ENERGY ANALYSIS ------------\n";

    resultFile << "Energy Consumption Score: "
               << energy << "\n";

    resultFile << "Energy Level            : "
               << energyLevel << "\n\n";


    // LINE ENERGY
    resultFile << "----------- LINE ENERGY ANALYSIS -------\n";

    for (int i = 0; i < lineEnergy.size(); i++)
    {
        resultFile << "Line "
                   << i + 1
                   << " : "
                   << lineEnergy[i]
                   << "\n";
    }

    resultFile << "\n";


    // RECOMMENDATIONS
    resultFile << "----------- RECOMMENDATION -------------\n";

    if (loops > 0)
    {
        resultFile
            << "- Optimize loop iterations.\n";
    }

    if (nestedLoops > 0)
    {
        resultFile
            << "- Avoid unnecessary nested loops.\n";
    }

    if (io > 0)
    {
        resultFile
            << "- Reduce unnecessary I/O operations.\n";
    }

    if (conditions > 0)
    {
        resultFile
            << "- Simplify complex conditions.\n";
    }

    if (recursion)
    {
        resultFile
            << "- Optimize recursive calls.\n";
    }

    if (
        loops == 0 &&
        nestedLoops == 0 &&
        io == 0 &&
        conditions == 0 &&
        !recursion
    )
    {
        resultFile
            << "- Code is relatively energy efficient.\n";
    }


    resultFile << "\n========================================\n";

    resultFile.close();


    cout << "\n========================================\n";
    cout << "Analysis completed successfully!\n";
    cout << "Result saved in analysis_result.txt\n";
    cout << "========================================\n";

    return 0;
}
