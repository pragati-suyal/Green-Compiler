#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <regex>
#include <iomanip>
#include <algorithm>
#include <cmath>
#include <set>

using namespace std;

class EnergyAnalyzer
{
private:

    string code;

    // ==========================================
    // ENERGY COST MODEL
    // ==========================================

    const double LOOP_COST = 10.0;
    const double NESTED_LOOP_COST = 25.0;
    const double IO_COST = 50.0;
    const double RECURSION_COST = 30.0;
    const double CONDITION_COST = 5.0;


    // ==========================================
    // HELPER: CONTROL KEYWORDS
    // ==========================================

    bool isControlKeyword(const string& name)
    {
        return
            name == "if" ||
            name == "for" ||
            name == "while" ||
            name == "switch" ||
            name == "catch";
    }


    // ==========================================
    // HELPER: CHECK IF CHARACTER IS IDENTIFIER
    // ==========================================

    bool isIdentifierCharacter(char c)
    {
        return
            isalnum(static_cast<unsigned char>(c)) ||
            c == '_';
    }


    // ==========================================
    // GET RECURSIVE FUNCTION NAMES
    // ==========================================

    set<string> getRecursiveFunctions()
    {
        set<string> recursiveFunctions;

        /*
            This pattern searches for function definitions.

            Example:

            int factorial(int n) {
            void test() {
            double calculate(int x) {
        */

        regex functionPattern(
            R"((?:[a-zA-Z_][a-zA-Z0-9_:<>*&\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^;{}]*\)\s*\{)"
        );

        auto begin =
            sregex_iterator(
                code.begin(),
                code.end(),
                functionPattern
            );

        auto end = sregex_iterator();


        for (auto it = begin; it != end; ++it)
        {
            string functionName =
                (*it)[1].str();


            if (isControlKeyword(functionName))
            {
                continue;
            }


            size_t functionStart =
                static_cast<size_t>(
                    it->position()
                );


            size_t bracePosition =
                code.find(
                    '{',
                    functionStart
                );


            if (bracePosition == string::npos)
            {
                continue;
            }


            // ==================================
            // FIND MATCHING CLOSING BRACE
            // ==================================

            int braceDepth = 0;

            size_t bodyEnd =
                string::npos;


            for (
                size_t i = bracePosition;
                i < code.length();
                i++
            )
            {
                if (code[i] == '{')
                {
                    braceDepth++;
                }
                else if (code[i] == '}')
                {
                    braceDepth--;

                    if (braceDepth == 0)
                    {
                        bodyEnd = i;
                        break;
                    }
                }
            }


            if (bodyEnd == string::npos)
            {
                continue;
            }


            string functionBody =
                code.substr(
                    bracePosition + 1,
                    bodyEnd - bracePosition - 1
                );


            // ==================================
            // SEARCH FUNCTION CALL INSIDE BODY
            // ==================================

            string callPattern =
                "\\b" +
                functionName +
                R"(\s*\()";

            regex recursiveCall(
                callPattern
            );


            if (
                regex_search(
                    functionBody,
                    recursiveCall
                )
            )
            {
                recursiveFunctions.insert(
                    functionName
                );
            }
        }


        return recursiveFunctions;
    }


public:

    // ==========================================
    // CONSTRUCTOR
    // ==========================================

    EnergyAnalyzer(string sourceCode)
    {
        code = sourceCode;
    }


    // ==========================================
    // COUNT REGEX PATTERN
    // ==========================================

    int countPattern(
        const string& pattern
    )
    {
        try
        {
            regex r(pattern);

            auto begin =
                sregex_iterator(
                    code.begin(),
                    code.end(),
                    r
                );

            auto end =
                sregex_iterator();

            return static_cast<int>(
                distance(begin, end)
            );
        }
        catch (...)
        {
            return 0;
        }
    }


    // ==========================================
    // REMOVE COMMENTS
    // ==========================================

    string removeComments(string source)
    {
        /*
            Important improvement:

            We preserve newline characters.

            This prevents line-number mismatch
            between source code and heatmap.
        */


        // Remove // comments but keep newline

        source =
            regex_replace(
                source,
                regex(R"(//[^\r\n]*)"),
                ""
            );


        // Remove /* ... */ comments
        // while preserving newlines

        regex blockComment(
            R"(/\*[\s\S]*?\*/)"
        );


        string result;

        size_t last = 0;

        auto begin =
            sregex_iterator(
                source.begin(),
                source.end(),
                blockComment
            );

        auto end =
            sregex_iterator();


        for (auto it = begin; it != end; ++it)
        {
            size_t start =
                static_cast<size_t>(
                    it->position()
                );

            size_t length =
                static_cast<size_t>(
                    it->length()
                );


            result +=
                source.substr(
                    last,
                    start - last
                );


            string comment =
                source.substr(
                    start,
                    length
                );


            // Keep newlines

            for (char c : comment)
            {
                if (c == '\n')
                {
                    result += '\n';
                }
            }


            last =
                start + length;
        }


        result +=
            source.substr(last);


        return result;
    }


    // ==========================================
    // COUNT LOOPS
    // ==========================================

    int countLoops()
    {
        return countPattern(
            R"(\b(for|while|do)\b)"
        );
    }


    // ==========================================
    // COUNT CONDITIONS
    // ==========================================

    int countConditions()
    {
        int ifCount =
            countPattern(
                R"(\bif\s*\()"
            );


        int switchCount =
            countPattern(
                R"(\bswitch\s*\()"
            );


        int caseCount =
            countPattern(
                R"(\bcase\b)"
            );


        return
            ifCount +
            switchCount +
            caseCount;
    }


    // ==========================================
    // COUNT I/O
    // ==========================================

    int countIO()
    {
        int cinCount =
            countPattern(
                R"(\bcin\b)"
            );


        int coutCount =
            countPattern(
                R"(\bcout\b)"
            );


        int printfCount =
            countPattern(
                R"(\bprintf\s*\()"
            );


        int scanfCount =
            countPattern(
                R"(\bscanf\s*\()"
            );


        return
            cinCount +
            coutCount +
            printfCount +
            scanfCount;
    }


    // ==========================================
    // GENERAL RECURSION DETECTION
    // ==========================================

    bool detectRecursion()
    {
        set<string> recursiveFunctions =
            getRecursiveFunctions();


        return
            !recursiveFunctions.empty();
    }


    // ==========================================
    // NESTED LOOP DETECTION
    // ==========================================

    int estimateNestedLoops()
    {
        stringstream ss(code);

        string line;

        int loopDepth = 0;

        int nestedLoops = 0;


        while (getline(ss, line))
        {
            bool hasLoop =
                regex_search(
                    line,
                    regex(
                        R"(\b(for|while|do)\b)"
                    )
                );


            /*
                A loop found while another loop
                is already active is considered
                a nested loop.
            */

            if (hasLoop)
            {
                if (loopDepth > 0)
                {
                    nestedLoops++;
                }

                loopDepth++;
            }


            // Count opening braces

            int openingBraces =
                static_cast<int>(
                    count(
                        line.begin(),
                        line.end(),
                        '{'
                    )
                );


            // Count closing braces

            int closingBraces =
                static_cast<int>(
                    count(
                        line.begin(),
                        line.end(),
                        '}'
                    )
                );


            /*
                Adjust depth carefully.

                Opening braces increase depth.
                Closing braces decrease depth.
            */

            if (openingBraces > 0)
            {
                /*
                    Do not increase again for the
                    loop brace itself because loopDepth
                    already represents the active loop.
                */
            }


            if (closingBraces > 0)
            {
                loopDepth =
                    max(
                        0,
                        loopDepth - closingBraces
                    );
            }
        }


        return nestedLoops;
    }


    // ==========================================
    // CYCLOMATIC COMPLEXITY
    // ==========================================

    int calculateCyclomaticComplexity()
    {
        int complexity = 1;


        complexity +=
            countPattern(
                R"(\bif\s*\()"
            );


        complexity +=
            countPattern(
                R"(\bfor\s*\()"
            );


        complexity +=
            countPattern(
                R"(\bwhile\s*\()"
            );


        complexity +=
            countPattern(
                R"(\bcase\b)"
            );


        complexity +=
            countPattern(
                R"(&&)"
            );


        complexity +=
            countPattern(
                R"(\|\|)"
            );


        return complexity;
    }


    // ==========================================
    // COUNT OPERATORS
    // ==========================================

    int countOperators()
    {
        /*
            Operators are checked from longest
            to shortest to reduce double counting.

            Example:
            ++ is counted as one operator,
            not as two + operators.
        */

        regex operatorPattern(
            R"(\+\+|--|==|!=|<=|>=|&&|\|\||\+=|-=|\*=|/=|%=|<<|>>|\+|-|\*|/|%|=|<|>)"
        );


        auto begin =
            sregex_iterator(
                code.begin(),
                code.end(),
                operatorPattern
            );


        auto end =
            sregex_iterator();


        return static_cast<int>(
            distance(begin, end)
        );
    }


    // ==========================================
    // COUNT OPERANDS
    // ==========================================

    int countOperands()
    {
        regex operandPattern(
            R"(\b[a-zA-Z_][a-zA-Z0-9_]*\b|\b[0-9]+(?:\.[0-9]+)?\b)"
        );


        set<string> keywords =
        {
            "alignas",
            "alignof",
            "and",
            "and_eq",
            "asm",
            "auto",
            "bitand",
            "bitor",
            "bool",
            "break",
            "case",
            "catch",
            "char",
            "class",
            "compl",
            "const",
            "constexpr",
            "continue",
            "default",
            "delete",
            "do",
            "double",
            "else",
            "enum",
            "explicit",
            "export",
            "extern",
            "false",
            "float",
            "for",
            "friend",
            "goto",
            "if",
            "inline",
            "int",
            "long",
            "mutable",
            "namespace",
            "new",
            "noexcept",
            "not",
            "not_eq",
            "nullptr",
            "operator",
            "or",
            "or_eq",
            "private",
            "protected",
            "public",
            "register",
            "reinterpret_cast",
            "return",
            "short",
            "signed",
            "sizeof",
            "static",
            "static_cast",
            "struct",
            "switch",
            "template",
            "this",
            "throw",
            "true",
            "try",
            "typedef",
            "typeid",
            "typename",
            "union",
            "unsigned",
            "using",
            "virtual",
            "void",
            "volatile",
            "wchar_t",
            "while",
            "xor",
            "xor_eq",
            "include",
            "std"
        };


        int total = 0;


        auto begin =
            sregex_iterator(
                code.begin(),
                code.end(),
                operandPattern
            );


        auto end =
            sregex_iterator();


        for (
            auto it = begin;
            it != end;
            ++it
        )
        {
            string token =
                (*it)[0].str();


            if (
                keywords.find(token)
                ==
                keywords.end()
            )
            {
                total++;
            }
        }


        return total;
    }


    // ==========================================
    // HALSTEAD VOLUME
    // ==========================================

    double calculateHalsteadVolume()
    {
        int operators =
            countOperators();


        int operands =
            countOperands();


        int length =
            operators +
            operands;


        int vocabulary =
            operators +
            operands;


        if (
            length == 0 ||
            vocabulary == 0
        )
        {
            return 0;
        }


        return
            length *
            log2(
                static_cast<double>(
                    vocabulary
                )
            );
    }


    // ==========================================
    // ENERGY SCORE
    // ==========================================

    double calculateEnergyScore()
    {
        int loops =
            countLoops();


        int nestedLoops =
            estimateNestedLoops();


        int io =
            countIO();


        int conditions =
            countConditions();


        bool recursion =
            detectRecursion();


        double score = 0;


        score +=
            loops *
            LOOP_COST;


        score +=
            nestedLoops *
            NESTED_LOOP_COST;


        score +=
            io *
            IO_COST;


        score +=
            conditions *
            CONDITION_COST;


        if (recursion)
        {
            score +=
                RECURSION_COST;
        }


        // Base processing cost

        score += 5;


        return score;
    }


    // ==========================================
    // ENERGY LEVEL
    // ==========================================

    string getEnergyLevel(
        double score
    )
    {
        if (score < 50)
        {
            return "LOW";
        }


        if (score < 120)
        {
            return "MEDIUM";
        }


        return "HIGH";
    }


    // ==========================================
    // LINE-BY-LINE ENERGY
    // ==========================================

    vector<double> calculateLineEnergy()
    {
        vector<double> lineScores;


        stringstream ss(code);

        string line;


        int loopDepth = 0;


        set<string> recursiveFunctions =
            getRecursiveFunctions();


        while (getline(ss, line))
        {
            double score = 0;


            // ==================================
            // LOOP
            // ==================================

            bool hasLoop =
                regex_search(
                    line,
                    regex(
                        R"(\b(for|while|do)\b)"
                    )
                );


            if (hasLoop)
            {
                score +=
                    LOOP_COST;


                if (loopDepth > 0)
                {
                    score +=
                        NESTED_LOOP_COST;
                }
            }


            // ==================================
            // I/O
            // ==================================

            bool hasIO =
                regex_search(
                    line,
                    regex(
                        R"(\b(cin|cout|printf|scanf)\b)"
                    )
                );


            if (hasIO)
            {
                score +=
                    IO_COST;
            }


            // ==================================
            // CONDITION
            // ==================================

            bool hasCondition =
                regex_search(
                    line,
                    regex(
                        R"(\b(if|switch|case)\b)"
                    )
                );


            if (hasCondition)
            {
                score +=
                    CONDITION_COST;
            }


            // ==================================
            // RECURSION
            // ==================================

            bool hasRecursion = false;


            for (
                const string& functionName :
                recursiveFunctions
            )
            {
                string pattern =
                    "\\b" +
                    functionName +
                    R"(\s*\()";


                if (
                    regex_search(
                        line,
                        regex(pattern)
                    )
                )
                {
                    hasRecursion = true;
                    break;
                }
            }


            if (hasRecursion)
            {
                score +=
                    RECURSION_COST;
            }


            // ==================================
            // UPDATE LOOP DEPTH
            // ==================================

            if (hasLoop)
            {
                loopDepth++;
            }


            int closingBraces =
                static_cast<int>(
                    count(
                        line.begin(),
                        line.end(),
                        '}'
                    )
                );


            if (closingBraces > 0)
            {
                loopDepth =
                    max(
                        0,
                        loopDepth -
                        closingBraces
                    );
            }


            lineScores.push_back(score);
        }


        return lineScores;
    }


    // ==========================================
    // COMPLETE ANALYSIS
    // ==========================================

    void analyze()
    {
        /*
            Remove comments while preserving
            line numbers.
        */

        code =
            removeComments(code);


        int loops =
            countLoops();


        int nestedLoops =
            estimateNestedLoops();


        int conditions =
            countConditions();


        int io =
            countIO();


        bool recursion =
            detectRecursion();


        int complexity =
            calculateCyclomaticComplexity();


        double halstead =
            calculateHalsteadVolume();


        double energy =
            calculateEnergyScore();


        string energyLevel =
            getEnergyLevel(
                energy
            );


        cout << "\n";

        cout <<
            "========================================\n";

        cout <<
            "          GREEN COMPILER\n";

        cout <<
            "       ENERGY ANALYZER\n";

        cout <<
            "========================================\n";


        // ======================================
        // CODE ANALYSIS
        // ======================================

        cout << "\n";

        cout <<
            "----------- CODE ANALYSIS --------------\n";


        cout <<
            "Loops                  : "
            << loops
            << endl;


        cout <<
            "Nested Loops           : "
            << nestedLoops
            << endl;


        cout <<
            "Conditions             : "
            << conditions
            << endl;


        cout <<
            "Input/Output Operations: "
            << io
            << endl;


        cout <<
            "Recursion              : "
            << (
                recursion
                ? "YES"
                : "NO"
            )
            << endl;


        // ======================================
        // SOFTWARE METRICS
        // ======================================

        cout << "\n";

        cout <<
            "----------- SOFTWARE METRICS -----------\n";


        cout <<
            "Cyclomatic Complexity  : "
            << complexity
            << endl;


        cout <<
            fixed
            << setprecision(2);


        cout <<
            "Halstead Volume        : "
            << halstead
            << endl;


        // ======================================
        // ENERGY
        // ======================================

        cout << "\n";

        cout <<
            "----------- ENERGY ANALYSIS ------------\n";


        cout <<
            "Energy Consumption Score: "
            << energy
            << endl;


        cout <<
            "Energy Level            : "
            << energyLevel
            << endl;


        // ======================================
        // LINE ENERGY
        // ======================================

        cout << "\n";

        cout <<
            "----------- LINE ENERGY ANALYSIS -------\n";


        vector<double> lineScores =
            calculateLineEnergy();


        for (
            size_t i = 0;
            i < lineScores.size();
            i++
        )
        {
            cout <<
                "Line "
                << i + 1
                << " : "
                << lineScores[i]
                << endl;
        }


        // ======================================
        // RECOMMENDATIONS
        // ======================================

        cout << "\n";

        cout <<
            "----------- RECOMMENDATION -------------\n";


        if (loops > 0)
        {
            cout <<
                "- Optimize loop iterations to reduce computational energy."
                << endl;
        }


        if (nestedLoops > 0)
        {
            cout <<
                "- Avoid unnecessary nested loops."
                << endl;
        }


        if (io > 0)
        {
            cout <<
                "- Reduce unnecessary input/output operations."
                << endl;
        }


        if (conditions > 0)
        {
            cout <<
                "- Simplify complex conditions where possible."
                << endl;
        }


        if (recursion)
        {
            cout <<
                "- Optimize recursive calls or consider an iterative approach."
                << endl;
        }


        if (
            loops == 0 &&
            nestedLoops == 0 &&
            io == 0 &&
            conditions == 0 &&
            !recursion
        )
        {
            cout <<
                "- Code is relatively energy efficient."
                << endl;
        }


        cout << "\n";

        cout <<
            "========================================\n";
    }
};
