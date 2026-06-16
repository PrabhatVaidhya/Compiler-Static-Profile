# Compiler-Static-Profile: Hybrid AST Analyzer & Applied ML Classifier

A production-grade, developer workspace combining **deterministic compiler-level AST profiling**, an **Applied Machine Learning Classifier**, and a **hybrid/toggleable local AI refactoring lab** to analyze, profile, and optimize Python and C++ codebases.

---

## 🚀 Key Features

*   **Zero-Overhead Compiler AST Engine**: Parses abstract syntax trees recursively using native `tree-sitter-python` and `tree-sitter-cpp` grammars.
*   **Static Diagnostics**: Intercepts 7 critical performance bottlenecks, design smells, and vulnerabilities:
    *   *Python*: $O(N^2)$ Nested Loops, Silent Exceptions (`pass` handlers), Mutable Defaults (`[]`/`{}`), and Global Variable Modifications.
    *   *C++*: $O(N^2)$ Nested Loops, Memory Leak Risks (Raw `new` operator), and Unsafe Buffer Copies (`strcpy`, etc.).
*   **Applied Machine Learning Pipeline**: 
    *   `data_harvester.py` downloads full source code zip archives (Requests, Flask, Google Benchmark) from the internet, compiles AST metrics across 219+ files, and saves `code_features.csv`.
    *   `train_model.py` standardizes feature scales and trains a `RandomForestClassifier` with stratified splits to predict if a file is vulnerable/smelly. Saves the model to `complexity_classifier.pkl`.
*   **Cyberpunk Streamlit Dashboard**: A stunning, custom-styled dark IDE including:
    *   **Vulnerability Feed**: Interactive dropdown navigation of scanned alerts.
    *   **Code Transformation**: Side-by-side original bottleneck vs. suggested optimized fix.
    *   **Unit-Test Lab**: Generates runnable testing suites (`pytest` for Python, `Google Test` for C++).
    *   **AST Syntax Hierarchy**: Renders visual ASCII compiler subtree structures.
    *   **Live Benchmark Lab**: Runs runtime timing cycles and compares scaling curves ($O(N)$ vs $O(N^2)$ vs $O(N^3)$).
    *   **Dataset Analytics**: Renders health scores, rule detection distributions, and hotspot files.
*   **Hybrid Local AI Reviewer**: Sidebar checkbox toggles on-demand local LLM reviews via Ollama (`deepseek-r1:1.5b`) with a Pydantic schema validator and regex `<think>` reasoning chain tag cleaning.

---

## 📂 Project Structure

```text
c:/Users/prabh/Desktop/project1/
├── README.md                     # Technical Overview & Setup guide
├── app.py                        # Streamlit Dashboard & Cyberpunk UI
├── analyzer.py                   # Tree-sitter AST Diagnostic Engine & AI Optimizer
├── data_harvester.py             # Harvester downloading GitHub ZIPs & extracting CSV features
├── train_model.py                # Preprocessing, Train/Val/Test splitting, & Random Forest training
├── demo_code/                    # High-vulnerability targets to verify rules
│   ├── matrix_ops.py             # Demo Python targets
│   └── memory_pool.cpp           # Demo C++ targets
└── project_dataset/              # Datasets & Serialized Models
    ├── raw_files/                # Unzipped public repositories
    ├── code_features.csv         # Generated feature rows dataset
    └── complexity_classifier.pkl # Saved StandardScaler + RandomForest pipeline
```

---

## 🛠️ Prerequisites & Installation

Ensure you have **Python 3.10+** installed.

### 1. Install Dependencies
Run the following command in your terminal to install the required libraries:
```bash
pip install tree-sitter tree-sitter-python tree-sitter-cpp streamlit streamlit-code-editor pandas numpy scikit-learn
```

*(Optional: Install `ollama` and download `deepseek-r1:1.5b` if you wish to toggle the Local AI Reviewer)*
```bash
pip install ollama
# In a separate command prompt:
ollama run deepseek-r1:1.5b
```

---

## ⚙️ Running the Pipelines

### 1. Execute Dataset Harvesting
Downloads Flask and Google Benchmark repositories, extracts them, and runs the AST feature analyzer recursively:
```bash
python data_harvester.py
```
*Creates: `project_dataset/code_features.csv` (219 rows).*

### 2. Execute ML Training Pipeline
Loads code features, standardizes scales, performs stratified 70/15/15 splits, trains a Random Forest model, and serializes the pipeline:
```bash
python train_model.py
```
*Creates: `project_dataset/complexity_classifier.pkl`.*

### 3. Verify ML Model Predictions
Runs the scratch folder validation script to test classifier inference on mock metrics:
```bash
python -c "import pickle, pandas as pd; pipeline = pickle.load(open('project_dataset/complexity_classifier.pkl', 'rb')); print(pipeline.predict(pd.DataFrame([[150.0, 2.0, 0.0, 0.0, 0.0, 1.0, 0.0]], columns=['loc', 'nested_loops', 'silent_exceptions', 'mutable_defaults', 'global_vars', 'raw_new_count', 'unsafe_copies'])))"
```
*Outputs: `[1]` (Vulnerable).*

### 4. Run the Cyberpunk IDE Workspace
Trigger the Streamlit app locally:
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.
