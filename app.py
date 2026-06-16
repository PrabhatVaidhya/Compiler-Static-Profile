# app.py - Streamlit Developer Workspace
import streamlit as st
import os
import pandas as pd
from code_editor import code_editor
from analyzer import StaticDiagnosticEngine

# Configure layout and title
st.set_page_config(
    page_title="Compiler Static Profiler & Complexity Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cyberpunk & Dark Mode IDE Theme Injector
st.markdown("""
<style>
/* Global style adjustments */
.stApp {
    background-color: #0b0c10;
    color: #c5c6c7;
}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {
    background-color: #1f2833;
    border-right: 2px solid #66fcf1;
}

/* Cyberpunk Headers */
h1 {
    color: #66fcf1 !important;
    text-shadow: 0 0 10px rgba(102, 252, 241, 0.5);
    font-family: 'Courier New', monospace;
    font-weight: 700;
}
h2, h3, h4 {
    color: #45f3ff !important;
    font-family: 'Courier New', monospace;
}

/* Sidebar Title and Text */
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #66fcf1 !important;
    text-align: center;
}

/* Custom styled cards for findings list */
.issue-card {
    background-color: #152238;
    border-radius: 6px;
    padding: 15px;
    margin-bottom: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    transition: all 0.2s ease;
}
.issue-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 252, 241, 0.25);
}

.issue-card.critical {
    border-left: 5px solid #ff007f;
}
.issue-card.warning {
    border-left: 5px solid #ffaa00;
}
.issue-card.info {
    border-left: 5px solid #00ffcc;
}

.issue-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    font-family: monospace;
}

.issue-file {
    font-weight: bold;
    color: #e5e7eb;
    font-size: 13px;
    word-break: break-all;
}

.issue-badge {
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    font-weight: bold;
}
.issue-badge.critical {
    background-color: rgba(255, 0, 127, 0.2);
    color: #ff007f;
    border: 1px solid #ff007f;
}
.issue-badge.warning {
    background-color: rgba(255, 170, 0, 0.2);
    color: #ffaa00;
    border: 1px solid #ffaa00;
}
.issue-badge.info {
    background-color: rgba(0, 255, 204, 0.2);
    color: #00ffcc;
    border: 1px solid #00ffcc;
}

.issue-title {
    font-size: 15px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 6px;
}

.issue-lines {
    font-family: monospace;
    font-size: 12px;
    color: #8f94fb;
}

/* Custom dashboard metric cards */
.metric-container {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 20px;
}
.metric-box {
    flex: 1;
    background-color: #121c2c;
    border: 1px solid #23395d;
    border-radius: 6px;
    padding: 10px;
    text-align: center;
}
.metric-label {
    font-size: 11px;
    text-transform: uppercase;
    color: #8a9ba8;
    margin-bottom: 2px;
}
.metric-val {
    font-size: 22px;
    font-weight: bold;
    font-family: monospace;
}
.metric-val.crit {
    color: #ff007f;
}
.metric-val.warn {
    color: #ffaa00;
}
.metric-val.inf {
    color: #00ffcc;
}

/* Tab Overrides */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #152238;
    border: 1px solid #23395d;
    border-radius: 4px 4px 0 0;
    color: #8a9ba8;
    padding: 6px 12px;
}
.stTabs [aria-selected="true"] {
    background-color: #121c2c !important;
    color: #66fcf1 !important;
    border-top: 2px solid #66fcf1 !important;
}
</style>
""", unsafe_allow_html=True)

# Application Header
st.title("🛡️ Core-Engine: Static AST Analysis Workspace")
st.caption("Deterministic syntax node pattern interceptor & algorithmic complexity profiler for Python/C++ codebases.")
st.write("---")

# Initialize default scan state
if "findings" not in st.session_state:
    default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "demo_code"))
    st.session_state.scanned_dir = default_dir
    engine = StaticDiagnosticEngine(default_dir)
    st.session_state.findings = engine.scan_repository()

# Define engine dynamically for the current run to avoid NameError on reruns
engine = StaticDiagnosticEngine(st.session_state.scanned_dir)

# Sidebar Setup
with st.sidebar:
    st.header("⚙️ Diagnostics Panel")
    
    # Target directory scanning input
    target_dir = st.text_input(
        "Scan Target Repository Path:",
        value=st.session_state.scanned_dir
    )
    
    # Dynamic Optimization Review Engine selection (Checkbox to avoid laptop slow down)
    enable_ai = st.checkbox(
        "🧠 Enable Local AI Reviewer",
        value=False,
        help="Query deepseek-r1:1.5b via Ollama. Keep disabled by default for zero CPU/GPU overhead."
    )
    
    if st.button("🚀 Trigger Static Scan", use_container_width=True):
        if not os.path.exists(target_dir):
            st.error("Directory path does not exist!")
        else:
            with st.spinner("Parsing syntax trees..."):
                engine = StaticDiagnosticEngine(target_dir)
                st.session_state.findings = engine.scan_repository()
                st.session_state.scanned_dir = target_dir
            st.success(f"Scanning completed successfully!")

    st.write("---")
    
    # Rules Guide
    with st.expander("📖 Active Static Rules Catalog"):
        st.markdown("""
        **Python Rules:**
        * **Nested Loop (O(N^2)):** Catches multiple loops nested inside each other.
        * **Silent Exceptions:** Finds `except` blocks swallowing errors via `pass`.
        * **Mutable Defaults:** Detects default parameters initialized as list/dict (`[]`/`{}`).
        * **Global Modification:** Flags functions writing to global variables.
        
        **C++ Rules:**
        * **Nested Loop (O(N^2)):** Flags loops nested inside each other.
        * **Raw Heap Allocation:** Catches raw `new` operations.
        * **Unsafe Buffer Copies:** Flags dangerous legacy string methods (`strcpy`, `strcat`, etc.).
        """)

# Fetch findings from session state
findings = st.session_state.findings

# Compute stats
critical_count = sum(1 for f in findings if f["severity"] == "Critical")
warning_count = sum(1 for f in findings if f["severity"] == "Warning")
info_count = sum(1 for f in findings if f["severity"] == "Info")

# Main Metrics Row
st.markdown(f"""
<div class="metric-container">
    <div class="metric-box">
        <div class="metric-label">Files Analyzed</div>
        <div class="metric-val" style="color: #66fcf1;">{len(set(f['file'] for f in findings))}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">Critical Vulnerabilities</div>
        <div class="metric-val crit">{critical_count}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">Warnings / Smells</div>
        <div class="metric-val warn">{warning_count}</div>
    </div>
    <div class="metric-box">
        <div class="metric-label">Info Alerts</div>
        <div class="metric-val inf">{info_count}</div>
    </div>
</div>
""", unsafe_allow_html=True)

if not findings:
    st.info("✅ No structural vulnerabilities or performance bottlenecks detected in this directory.")
else:
    # Set up split-pane screen layout
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.subheader("⚠️ Syntactic Vulnerability Feed")
        
        # Interactive selector using a selectbox to drive the "Lab" detail panel
        selected_idx = st.selectbox(
            "🎯 Select Anomaly to Load in Lab:",
            range(len(findings)),
            format_func=lambda idx: f"#{idx+1}: [{findings[idx]['severity']}] {findings[idx]['file_rel']} ({findings[idx]['issue']})"
        )
        
        # Render the custom-styled feed of findings below the selector
        for i, f in enumerate(findings):
            sev_class = f["severity"].lower()
            highlight_border = "border: 2px solid #66fcf1;" if i == selected_idx else ""
            
            st.markdown(f"""
            <div class="issue-card {sev_class}" style="{highlight_border}">
                <div class="issue-header">
                    <span class="issue-file">#{i+1}: {f['file_rel']}</span>
                    <span class="issue-badge {sev_class}">{f['severity']}</span>
                </div>
                <div class="issue-title">{f['issue']}</div>
                <div class="issue-lines">Lines: {f['lines']} | {f['category']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.subheader("🤖 Active File & Code Transformation Lab")
        
        # Select active finding
        active_finding = findings[selected_idx]
        file_ext = os.path.splitext(active_finding["file"])[1].lower()
        editor_lang = "python" if file_ext == ".py" else "cpp"

        # Check and load report from cache or trigger inference engine
        inference_mode_str = "AI" if enable_ai else "Deterministic"
        cache_key = f"{selected_idx}_{inference_mode_str}"
        if "ai_reports" not in st.session_state:
            st.session_state.ai_reports = {}
            
        if cache_key not in st.session_state.ai_reports:
            if enable_ai:
                with st.spinner("🧠 Requesting Local AI Code Review (DeepSeek-R1)..."):
                    report = engine.request_ai_optimization(
                        active_finding["issue"],
                        active_finding["snippet"],
                        active_finding["file"]
                    )
            else:
                meta = engine.rules_db.get(active_finding["issue"], {})
                fallback_fix = active_finding["suggested_fix"]
                fallback_test = meta["python_tests"] if editor_lang == "python" else meta["cpp_tests"]
                report = {
                    "optimized_code": fallback_fix,
                    "explanation": active_finding["description"],
                    "unit_tests": fallback_test,
                    "source": "Deterministic AST Engine (Ollama Offline)"
                }
            st.session_state.ai_reports[cache_key] = report
        else:
            report = st.session_state.ai_reports[cache_key]

        # Tabbed panel inside the Code Transformation Lab
        lab_tabs = st.tabs([
            "📊 Dataset Analytics Hub",
            "✨ Code Transformation", 
            "🧪 Automated Unit-Tests",
            "🌳 AST Syntax Hierarchy", 
            "⚡ Live Benchmark Lab", 
            "💻 Full File Codebase Stream"
        ])
        
        with lab_tabs[0]:
            st.markdown("##### 📊 Corpus Dataset Analytics & Optimization Metrics")
            st.write("Extracts structural and algorithmic code patterns from the downloaded codebase folder.")
            
            # Compute stats
            total_scanned = len(set(f["file"] for f in findings))
            total_issues = len(findings)
            # Grade codebase out of 100 (5 points deducted per finding)
            code_grade = max(10, 100 - (total_issues * 5))
            
            # Display score card
            grade_color = "#ff007f" if code_grade < 70 else "#ffaa00" if code_grade < 90 else "#00ffcc"
            st.markdown(f"""
            <div style="background-color: #121c2c; border: 1px solid #23395d; padding: 15px; border-radius: 6px; margin-bottom: 20px; text-align: center;">
                <span style="font-size: 14px; text-transform: uppercase; color: #8a9ba8;">Scanned Corpus Health Index</span>
                <h2 style="margin: 5px 0; color: {grade_color} !important; font-size: 36px; font-family: monospace;">{code_grade} / 100</h2>
                <span style="font-size: 13px; color: #c5c6c7;">Density: {total_issues / total_scanned:.1f} issues per file across {total_scanned} script files.</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Plot charts
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("**Rule Detections Distribution**")
                cat_counts = {}
                for f in findings:
                    cat_counts[f["issue"]] = cat_counts.get(f["issue"], 0) + 1
                df_cat = pd.DataFrame(list(cat_counts.items()), columns=["Anomaly Category", "Counts"])
                st.bar_chart(df_cat, x="Anomaly Category", y="Counts")
                
            with col_chart2:
                st.markdown("**Corpus Files with Most Anomaly Hotspots**")
                file_counts = {}
                for f in findings:
                    file_counts[f["file_rel"]] = file_counts.get(f["file_rel"], 0) + 1
                df_files = pd.DataFrame(list(file_counts.items()), columns=["File", "Hotspots Count"])
                st.bar_chart(df_files, x="File", y="Hotspots Count")

        with lab_tabs[1]:
            st.markdown(f"""
            <div style="background-color: #121c2c; border: 1px solid #23395d; padding: 15px; border-radius: 6px; margin-bottom: 15px;">
                <h4 style="margin: 0 0 5px 0; color: #66fcf1;">{active_finding['issue']}</h4>
                <p style="font-size: 13px; color: #8a9ba8; margin: 0 0 8px 0;"><strong>Category:</strong> {active_finding['category']} | <strong>Lines:</strong> {active_finding['lines']}</p>
                <p style="font-size: 12px; color: #00ffcc; margin: 0 0 10px 0; font-family: monospace;">Review Source: {report['source']}</p>
                <p style="font-size: 14px; margin: 0; color: #e5e7eb;">{report['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Side-by-side original vs optimized code
            code_col1, code_col2 = st.columns(2)
            with code_col1:
                st.error("🚨 Isolated Code Bottleneck")
                st.code(active_finding["snippet"], language=editor_lang)
                
            with code_col2:
                st.success("🔧 Suggested Refactored Fix")
                if report["optimized_code"]:
                    st.code(report["optimized_code"], language=editor_lang)
                else:
                    st.info("N/A: Refactoring recommendation not defined for this profile.")

        with lab_tabs[2]:
            st.markdown("##### 🧪 Automated Unit-Test Suite")
            st.caption("Auto-generated unit tests verifying optimized code correctness and edge cases.")
            if report["unit_tests"]:
                st.code(report["unit_tests"], language=editor_lang)
            else:
                st.info("No test cases generated for this rule.")

        with lab_tabs[3]:
            st.markdown("##### 🌳 Abstract Syntax Tree (Subtree Node Hierarchy)")
            st.caption("This visualization maps out the exact syntactic node tree resolved by compiler-level language grammars.")
            
            with st.spinner("Generating AST branch..."):
                ast_tree = engine.generate_ast_tree_string(
                    active_finding["file"],
                    active_finding["start_point"],
                    active_finding["end_point"]
                )
            st.code(ast_tree, language="text")

        with lab_tabs[4]:
            st.markdown("##### ⚡ Active Profiler & Complexity Simulator")
            st.caption("Measure live execution speedups or analyze asymptotic scaling curves.")
            
            bench_col1, bench_col2 = st.columns([1, 1])
            
            with bench_col1:
                st.markdown("**1. Asymptotic Complexity Scaling**")
                st.write("Visualizes how problem size ($N$) impacts computational resource scaling.")
                
                n_vals = list(range(1, 41))
                df_scale = pd.DataFrame({
                    "N (Size)": n_vals,
                    "Linear: O(N)": n_vals,
                    "Quadratic: O(N^2)": [x**2 for x in n_vals],
                    "Cubic: O(N^3)": [x**3 for x in n_vals]
                }).set_index("N (Size)")
                
                st.line_chart(df_scale)
                st.caption("Comparison curve of linear vs quadratic vs cubic executions.")
                
            with bench_col2:
                st.markdown("**2. Environment Micro-Benchmarker**")
                
                if editor_lang == "python":
                    st.write("Execute comparative timing cycles for this specific Python structure.")
                    
                    if st.button("⏱️ Run Live Benchmarking Test", key=f"run_bench_{selected_idx}", use_container_width=True):
                        with st.spinner("Running high-speed loop cycles..."):
                            bench_engine = StaticDiagnosticEngine(st.session_state.scanned_dir)
                            res = bench_engine.run_micro_benchmark(active_finding["issue"])
                        
                        if res["original_time"] > 0:
                            st.success("Benchmark completed successfully!")
                            
                            delta_text = f"{res['speedup']-1:.2f}x faster" if res['speedup'] > 1 else "no speedup"
                            st.metric(
                                label="🚀 Measured Execution Speedup",
                                value=f"{res['speedup']}x",
                                delta=delta_text
                            )
                            
                            chart_df = pd.DataFrame({
                                "Implementation": ["Original Code", "Optimized Code"],
                                "Time (seconds)": [res["original_time"], res["optimized_time"]]
                            })
                            st.bar_chart(chart_df, x="Implementation", y="Time (seconds)")
                            st.caption(f"*Time represents cumulative duration of execution iterations.*")
                            
                            st.info(f"**Methodology:** {res['notes']}")
                        else:
                            st.warning("Could not execute benchmark test for this finding.")
                else:
                    st.warning("⚠️ Live Benchmarking is supported for Python AST rules. For C++, local compiler bindings (g++) are required.")
                    st.info("You can still use the Complexity Scaling Simulator on the left to review loop behavior.")

        with lab_tabs[5]:
            st.markdown(f"💡 **Displaying File:** `{active_finding['file']}` (Bottleneck located at lines `{active_finding['lines']}`)")
            
            try:
                with open(active_finding["file"], "r", encoding="utf-8", errors="ignore") as f_full:
                    full_code_content = f_full.read()
            except Exception as e:
                full_code_content = f"Error reading file content: {e}"

            editor_options = {
                "props": {
                    "disabled": True,
                    "style": {
                        "borderRadius": "6px",
                        "border": "1px solid #23395d",
                        "fontFamily": "monospace"
                    }
                }
            }
            code_editor(
                full_code_content,
                lang=editor_lang,
                theme="monokai",
                options=editor_options,
                key=f"editor_{selected_idx}"
            )
