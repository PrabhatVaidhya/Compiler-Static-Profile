# analyzer.py - Core Static Analysis & Hybrid AI Optimizer Engine
import os
import re
import json
from typing import List, Dict, Any
import tree_sitter_python as tspython
import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser, Query, QueryCursor
from pydantic import BaseModel, Field
from ollama import chat

class AIReport(BaseModel):
    optimized_code: str = Field(description="Syntax-compliant refactored optimized code block matching the language context")
    explanation: str = Field(description="Clear explanation of the performance bottleneck or design flaw and how the fix resolves it")
    unit_tests: str = Field(description="Comprehensive unit test suite verifying the refactored code correctness and edge cases")

class StaticDiagnosticEngine:
    def __init__(self, directory_path: str):
        self.directory_path = directory_path
        
        # Natively load tree-sitter grammars
        self.py_lang = Language(tspython.language())
        self.cpp_lang = Language(tscpp.language())

        # Define rule specifications including description, severity, fixes, and unit-test templates
        self.rules_db = {
            "O(N^2) Nested Loop": {
                "severity": "Critical",
                "category": "Performance Bottleneck",
                "description": "Nested loop sequence detected. Execution cost scales quadratically or cubically (O(N^2) or O(N^3)). Consider vectorization, set lookups, or matrix math libraries.",
                "python_fix": (
                    "# Optimized Fix: Use list comprehension, set lookup, or numpy vectorized operations.\n"
                    "# Example: Replace loops with dict/set operations for O(1) lookups.\n"
                    "seen = set(items)\n"
                    "results = [x for x in matrix_row if x in seen]"
                ),
                "cpp_fix": (
                    "// Optimized Fix: Use cache blocking, loop unrolling, or parallelized omp loops.\n"
                    "// Example using OpenMP:\n"
                    "#pragma omp parallel for\n"
                    "for (int i = 0; i < N; ++i) {\n"
                    "    // inner logic...\n"
                    "}"
                ),
                "python_tests": (
                    "def test_compute_matrix_product():\n"
                    "    # Verify matrix multiplication correct results\n"
                    "    A = [[1, 2], [3, 4]]\n"
                    "    B = [[5, 6], [7, 8]]\n"
                    "    # Expected product result: [[19, 22], [43, 50]]\n"
                    "    res = compute_matrix_product_optimized(A, B)\n"
                    "    assert res == [[19, 22], [43, 50]]"
                ),
                "cpp_tests": (
                    "#include <gtest/gtest.h>\n"
                    "#include <vector>\n\n"
                    "TEST(MatrixTest, MultiplyCorrectness) {\n"
                    "    std::vector<std::vector<int>> A = {{1, 2}, {3, 4}};\n"
                    "    std::vector<std::vector<int>> B = {{5, 6}, {7, 8}};\n"
                    "    auto C = process_matrices_optimized(A, B);\n"
                    "    EXPECT_EQ(C[0][0], 19);\n"
                    "    EXPECT_EQ(C[1][1], 50);\n"
                    "}"
                )
            },
            "Silent Exception Handling": {
                "severity": "Warning",
                "category": "Code Quality / Smell",
                "description": "Silent exception handling detected. An empty handler block containing only 'pass' swallows errors, making debugging difficult and masking critical runtime issues.",
                "python_fix": (
                    "# Optimized Fix: Log exceptions and re-raise them or handle them gracefully.\n"
                    "import logging\n"
                    "try:\n"
                    "    # execute block\n"
                    "except Exception as e:\n"
                    "    logging.exception(\"Operation failed: %s\", e)\n"
                    "    raise  # or fallback logic"
                ),
                "cpp_fix": "",
                "python_tests": (
                    "import pytest\n"
                    "import logging\n\n"
                    "def test_silent_exception_not_swallowed(caplog):\n"
                    "    with pytest.raises(ZeroDivisionError):\n"
                    "        # Ensure the exception is raised and logged rather than swallowed\n"
                    "        with caplog.at_level(logging.ERROR):\n"
                    "            # Code blocks trigger exceptions here\n"
                    "            pass"
                ),
                "cpp_tests": ""
            },
            "Mutable Default Argument": {
                "severity": "Warning",
                "category": "Architectural Design Smell",
                "description": "Function default parameter is a mutable object (list or dictionary). In Python, defaults are evaluated only once at definition time, meaning all invocations share the exact same reference.",
                "python_fix": (
                    "# Optimized Fix: Use None as default and initialize container inside function.\n"
                    "def function_name(parameter=None):\n"
                    "    if parameter is None:\n"
                    "        parameter = []\n"
                    "    # logic using parameter"
                ),
                "cpp_fix": "",
                "python_tests": (
                    "def test_mutable_default_isolation():\n"
                    "    # Verify that multiple calls do not contaminate the default state\n"
                    "    state1_len = cache_matrix_state([[1]])\n"
                    "    state2_len = cache_matrix_state([[2]])\n"
                    "    # With None default, each calls should isolate the cache state\n"
                    "    assert state1_len == 1\n"
                    "    assert state2_len == 1"
                ),
                "cpp_tests": ""
            },
            "Global Variable Modification": {
                "severity": "Info",
                "category": "Maintainability Smell",
                "description": "Function modifies a global variable. This creates hidden side-effects, hurts code reusability, and makes unit testing or concurrent executions fragile.",
                "python_fix": (
                    "# Optimized Fix: Pass variables as parameters and return the computed state.\n"
                    "def update_state(current_state, delta):\n"
                    "    return current_state + delta"
                ),
                "cpp_fix": "",
                "python_tests": (
                    "def test_global_scope_isolation():\n"
                    "    # Verify code modifications are local and don't leak to global matrix state\n"
                    "    initial_global = active_matrix\n"
                    "    # Run update on a local variable state\n"
                    "    assert initial_global is None"
                ),
                "cpp_tests": ""
            },
            "Memory Leak Risk (Raw New)": {
                "severity": "Critical",
                "category": "Memory Safety Vulnerability",
                "description": "Raw heap allocation using 'new' operator. If delete is omitted or an exception is thrown before deletion, a memory leak occurs. Use smart pointers (unique_ptr/shared_ptr) or container classes.",
                "python_fix": "",
                "cpp_fix": (
                    "// Optimized Fix: Avoid raw new. Use std::unique_ptr or std::vector.\n"
                    "#include <memory>\n"
                    "// Replace: int* arr = new int[size];\n"
                    "auto arr = std::make_unique<int[]>(size);"
                ),
                "python_tests": "",
                "cpp_tests": (
                    "#include <gtest/gtest.h>\n"
                    "#include <memory>\n\n"
                    "TEST(MemoryPoolTest, SmartPointerLeakPrevention) {\n"
                    "    // Verify RAII allocations are automatically managed and freed\n"
                    "    {\n"
                    "        auto pool = std::make_unique<MemoryPool>(512);\n"
                    "        EXPECT_NE(pool, nullptr);\n"
                    "    } // Automatically deallocates raw_buffer heap safely here\n"
                    "}"
                )
            },
            "Unsafe Buffer Copy": {
                "severity": "Warning",
                "category": "Buffer Safety Vulnerability",
                "description": "Unsafe legacy buffer copy function detected (e.g. strcpy, strcat, gets, sprintf). These do not verify bound limits and can trigger buffer overflows. Use safe boundary variants (strncpy, snprintf) or std::string.",
                "python_fix": "",
                "cpp_fix": (
                    "// Optimized Fix: Use boundary checks (strncpy/snprintf) or std::string.\n"
                    "// Example:\n"
                    "strncpy(destination, source, sizeof(destination) - 1);\n"
                    "destination[sizeof(destination) - 1] = '\\0';"
                ),
                "python_tests": "",
                "cpp_tests": (
                    "#include <gtest/gtest.h>\n"
                    "#include <cstring>\n\n"
                    "TEST(BufferTest, BoundaryChecksSafeguard) {\n"
                    "    char destination[10];\n"
                    "    const char* source = \"A very long tag that overflows\";\n"
                    "    // Expect safe truncation or correct boundary copy\n"
                    "    strncpy(destination, source, sizeof(destination) - 1);\n"
                    "    destination[sizeof(destination) - 1] = '\\0';\n"
                    "    EXPECT_EQ(std::strlen(destination), 9);\n"
                    "}"
                )
            }
        }

    def get_rules_for_language(self, ext: str) -> Dict[str, Any]:
        """Maps file extensions to tree-sitter language objects and queries."""
        rules = {
            ".py": {
                "lang_obj": self.py_lang,
                "queries": {
                    "O(N^2) Nested Loop": """
                        (for_statement body: (block (for_statement) @match))
                        (for_statement body: (block (while_statement) @match))
                        (while_statement body: (block (for_statement) @match))
                        (while_statement body: (block (while_statement) @match))
                    """,
                    "Silent Exception Handling": """
                        (except_clause (block (pass_statement) @match))
                    """,
                    "Mutable Default Argument": """
                        (default_parameter (list) @match)
                        (default_parameter (dictionary) @match)
                    """,
                    "Global Variable Modification": """
                        (global_statement) @match
                    """
                }
            },
            ".cpp": {
                "lang_obj": self.cpp_lang,
                "queries": {
                    "O(N^2) Nested Loop": """
                        (for_statement body: (compound_statement (for_statement) @match))
                        (for_statement body: (for_statement) @match)
                        (for_statement body: (compound_statement (while_statement) @match))
                        (for_statement body: (while_statement) @match)
                        (while_statement body: (compound_statement (for_statement) @match))
                        (while_statement body: (for_statement) @match)
                        (while_statement body: (compound_statement (while_statement) @match))
                        (while_statement body: (while_statement) @match)
                    """,
                    "Memory Leak Risk (Raw New)": """
                        (new_expression) @match
                    """,
                    "Unsafe Buffer Copy": """
                        (call_expression
                          function: [
                            (identifier) @func_name
                            (qualified_identifier name: (identifier) @func_name)
                            (qualified_identifier (identifier) @func_name)
                          ]
                          (#match? @func_name "^(strcpy|strcat|gets|sprintf|vsprintf)$")) @match
                    """
                }
            }
        }
        if ext in [".cpp", ".cc", ".cxx", ".h", ".hpp"]:
            return rules[".cpp"]
        elif ext == ".py":
            return rules[".py"]
        return None

    def scan_repository(self) -> List[Dict[str, Any]]:
        """Scans the designated folder recursively and parses AST structures."""
        findings = []
        
        if not os.path.exists(self.directory_path):
            return findings

        for root, _, files in os.walk(self.directory_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                rule_spec = self.get_rules_for_language(ext)
                if not rule_spec:
                    continue

                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        source_code = f.read()
                except Exception:
                    continue

                # Initialize Parser
                parser = Parser(rule_spec["lang_obj"])
                tree = parser.parse(bytes(source_code, "utf8"))

                # Evaluate rules
                for issue_name, query_string in rule_spec["queries"].items():
                    try:
                        ts_query = Query(rule_spec["lang_obj"], query_string)
                        cursor = QueryCursor(ts_query)
                        captures = cursor.captures(tree.root_node)
                    except Exception:
                        continue

                    match_nodes = captures.get("match", [])
                    for node in match_nodes:
                        start_line = node.start_point[0] + 1
                        end_line = node.end_point[0] + 1
                        
                        code_lines = source_code.splitlines()
                        snippet = ""
                        if 0 <= node.start_point[0] < len(code_lines):
                            snippet = "\n".join(code_lines[node.start_point[0]:node.end_point[0]+1])

                        meta = self.rules_db.get(issue_name, {
                            "severity": "Warning",
                            "category": "Code Quality Smell",
                            "description": "Syntactic anomaly detected.",
                            "python_fix": "",
                            "cpp_fix": "",
                            "python_tests": "",
                            "cpp_tests": ""
                        })

                        suggested_fix = meta["python_fix"] if ext == ".py" else meta["cpp_fix"]
                        display_lines = f"L{start_line} - L{end_line}"

                        findings.append({
                            "file": os.path.abspath(file_path),
                            "file_rel": os.path.relpath(file_path, self.directory_path),
                            "issue": issue_name,
                            "lines": display_lines,
                            "start_line": start_line,
                            "end_line": end_line,
                            "start_point": (node.start_point[0], node.start_point[1]),
                            "end_point": (node.end_point[0], node.end_point[1]),
                            "severity": meta["severity"],
                            "category": meta["category"],
                            "description": meta["description"],
                            "snippet": snippet,
                            "suggested_fix": suggested_fix
                        })
                        
        findings.sort(key=lambda x: (x["file"], x["start_line"]))
        return findings

    def generate_ast_tree_string(self, file_path: str, start_point: tuple, end_point: tuple) -> str:
        try:
            ext = os.path.splitext(file_path)[1].lower()
            lang_obj = self.py_lang if ext == ".py" else self.cpp_lang
            
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source_code = f.read()
            
            parser = Parser(lang_obj)
            tree = parser.parse(bytes(source_code, "utf8"))
            
            target_node = self._find_node_by_points(tree.root_node, start_point, end_point)
            if target_node:
                # Upcast to parents for richer context
                if target_node.type in ["list", "dictionary"] and target_node.parent and target_node.parent.type == "default_parameter":
                    target_node = target_node.parent
                elif target_node.type == "pass_statement" and target_node.parent and target_node.parent.parent and target_node.parent.parent.type == "except_clause":
                    target_node = target_node.parent.parent
            else:
                target_node = tree.root_node
                
            return self._build_ast_ascii_tree(target_node)
        except Exception as e:
            return f"Failed to generate AST: {e}"
            
    def _find_node_by_points(self, node, start_point, end_point):
        if node.start_point == start_point and node.end_point == end_point:
            return node
            
        for child in node.children:
            if child.start_point <= start_point and child.end_point >= end_point:
                match = self._find_node_by_points(child, start_point, end_point)
                if match:
                    return match
        return None
        
    def _build_ast_ascii_tree(self, node, depth=0, max_depth=6) -> str:
        indent = "  " * depth
        text_val = node.text.decode("utf-8", errors="ignore").replace("\n", " ").strip()
        if len(text_val) > 40:
            text_val = text_val[:37] + "..."
            
        line_str = f"L{node.start_point[0]+1}:{node.start_point[1]}"
        node_info = f"{node.type} ({line_str}) - '{text_val}'" if text_val else f"{node.type} ({line_str})"
        
        result = f"{indent}├── {node_info}\n"
        
        if depth < max_depth:
            for child in node.children:
                result += self._build_ast_ascii_tree(child, depth + 1, max_depth)
        return result

    def run_micro_benchmark(self, issue_name: str) -> Dict[str, Any]:
        import timeit
        
        results = {
            "original_time": 0.0,
            "optimized_time": 0.0,
            "speedup": 1.0,
            "notes": ""
        }
        
        if issue_name == "O(N^2) Nested Loop":
            setup_orig = "matrix_a = [[i for i in range(15)] for _ in range(15)]; matrix_b = [[j for j in range(15)] for _ in range(15)]"
            code_orig = """
n = len(matrix_a)
m = len(matrix_a[0])
p = len(matrix_b[0])
result = [[0 for _ in range(p)] for _ in range(n)]
for i in range(n):
    for j in range(p):
        for k in range(m):
            result[i][j] += matrix_a[i][k] * matrix_b[k][j]
"""
            setup_opt = "import numpy as np; matrix_a = np.arange(225).reshape(15, 15); matrix_b = np.arange(225).reshape(15, 15)"
            code_opt = "np.dot(matrix_a, matrix_b)"
            
            t_orig = timeit.timeit(code_orig, setup=setup_orig, number=100)
            t_opt = timeit.timeit(code_opt, setup=setup_opt, number=100)
            
            results["original_time"] = t_orig
            results["optimized_time"] = t_opt
            results["speedup"] = round(t_orig / t_opt, 2)
            results["notes"] = "Compares standard Python list multiplication loops against vector operations in NumPy (15x15 arrays, 100 runs)."
            
        elif issue_name == "Silent Exception Handling":
            code_orig = """
for _ in range(1000):
    try:
        x = 1 / 0
    except Exception:
        pass
"""
            code_opt = """
y = 0
for _ in range(1000):
    if y != 0:
        x = 1 / y
"""
            t_orig = timeit.timeit(code_orig, number=100)
            t_opt = timeit.timeit(code_opt, number=100)
            
            results["original_time"] = t_orig
            results["optimized_time"] = t_opt
            results["speedup"] = round(t_orig / t_opt, 2)
            results["notes"] = "Compares raising/catching ZeroDivisionError exceptions inside a loop against avoiding the exception with a conditional check (100 runs of 1,000 iterations)."
            
        elif issue_name == "Global Variable Modification":
            setup_orig = "global_val = 0"
            code_orig = """
global global_val
for _ in range(1000):
    global_val += 1
"""
            code_opt = """
local_val = 0
for _ in range(1000):
    local_val += 1
"""
            t_orig = timeit.timeit(code_orig, setup=setup_orig, number=500)
            t_opt = timeit.timeit(code_opt, number=500)
            
            results["original_time"] = t_orig
            results["optimized_time"] = t_opt
            results["speedup"] = round(t_orig / t_opt, 2)
            results["notes"] = "Compares writing to global variables vs. writing to local scoped stack variables inside a loop (500 runs of 1,000 iterations)."
            
        else:
            results["notes"] = "Benchmarking is supported for Python AST rules. C++ rule profiling is not supported."
            
        return results

    def get_optimization_report(self, issue_name: str, snippet: str, file_path: str) -> Dict[str, str]:
        """Loads deterministic optimization fixes, explanations, and unit tests instantly from rules_db."""
        ext = os.path.splitext(file_path)[1].lower()
        is_py = (ext == ".py")
        
        meta = self.rules_db.get(issue_name, {
            "description": "Syntactic anomaly isolated.",
            "python_fix": "",
            "cpp_fix": "",
            "python_tests": "",
            "cpp_tests": ""
        })
        
        fix_code = meta["python_fix"] if is_py else meta["cpp_fix"]
        test_code = meta["python_tests"] if is_py else meta["cpp_tests"]
        
        return {
            "optimized_code": fix_code,
            "explanation": meta["description"],
            "unit_tests": test_code,
            "source": "Deterministic Compiler AST Engine"
        }

    def request_ai_optimization(self, issue_name: str, snippet: str, file_path: str) -> Dict[str, str]:
        """Requests optimization from local deepseek-r1:1.5b via Ollama. Falls back to get_optimization_report on error."""
        ext = os.path.splitext(file_path)[1].lower()
        lang_name = "Python" if ext == ".py" else "C++"
        
        prompt = f"""
Analyze and optimize the following {lang_name} code block:
Issue category: {issue_name}

Snippet:
```
{snippet}
```

Provide:
1. Syntax-compliant optimized code.
2. Technical explanation of why it is better.
3. Unit tests verifying the fix (pytest style for Python, Google Test framework for C++).
"""
        try:
            # Query Ollama
            response = chat(
                model="deepseek-r1:1.5b",
                messages=[{"role": "user", "content": prompt}],
                format=AIReport.model_json_schema(),
                options={"temperature": 0.0}
            )
            
            content = response.message.content
            # Remove reasoning think block
            content_clean = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            
            # Load and validate
            data = json.loads(content_clean)
            validated = AIReport.model_validate(data)
            
            return {
                "optimized_code": validated.optimized_code,
                "explanation": validated.explanation,
                "unit_tests": validated.unit_tests,
                "source": "Local AI (deepseek-r1:1.5b)"
            }
        except Exception as e:
            # Fallback to local rule template mappings
            fallback = self.get_optimization_report(issue_name, snippet, file_path)
            fallback["explanation"] = f"{fallback['explanation']} (Local LLM Offline Fallback active: {e})"
            fallback["source"] = "Deterministic Compiler AST Fallback"
            return fallback
