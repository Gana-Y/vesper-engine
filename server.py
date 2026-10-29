"""
Vesper Execution Engine - REST API & World-Class Interactive Playground
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
from src import VesperEngine, Verdict

app = FastAPI(
    title="Vesper Execution Engine",
    description="Isolated, High-Performance Code Execution Engine & Sandboxed Arbiter",
    version="1.0.0"
)

engine = VesperEngine(mode="auto")


class EvaluationRequest(BaseModel):
    language: str = Field(..., description="Programming language ('py', 'cpp', 'java')")
    src_code: str = Field(...)
    std_in: Optional[str] = Field(default="")
    expected_out: Optional[str] = Field(default="")
    time_limit: float = Field(default=1.0, ge=0.1, le=10.0)
    memory_limit: int = Field(default=128, ge=16, le=1024)


class CustomRunRequest(BaseModel):
    language: str = Field(...)
    src_code: str = Field(...)
    std_in: Optional[str] = Field(default="")
    time_limit: float = Field(default=1.0, ge=0.1, le=10.0)
    memory_limit: int = Field(default=128, ge=16, le=1024)


@app.get("/api/health")
def health_check():
    use_docker = engine._resolve_backend(1, 128, ".")[1]
    return {
        "status": "healthy",
        "engine": "Vesper",
        "version": "1.0.0",
        "supported_languages": ["py", "cpp", "java"],
        "backend": "Docker cgroups Sandbox" if use_docker else "Microsecond Local Supervisor"
    }


@app.post("/api/evaluate")
def evaluate_submission(req: EvaluationRequest):
    try:
        res = engine.evaluate(
            language=req.language,
            time_limit=req.time_limit,
            memory_limit=req.memory_limit,
            src_code=req.src_code,
            std_in=req.std_in,
            expected_out=req.expected_out
        )
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/run-custom")
def run_custom(req: CustomRunRequest):
    try:
        res = engine.run_custom(
            language=req.language,
            time_limit=req.time_limit,
            memory_limit=req.memory_limit,
            src_code=req.src_code,
            std_in=req.std_in
        )
        return res.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
def interactive_playground():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vesper — Sandboxed Code Arbiter</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #08090d;
            --bg-surface: #0f1118;
            --bg-card: #151824;
            --bg-card-hover: #1c2030;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-focus: #38bdf8;
            --accent-primary: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.25);
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --ac-color: #10b981;
            --ac-glow: rgba(16, 185, 129, 0.2);
            --wa-color: #f43f5e;
            --wa-glow: rgba(244, 63, 94, 0.2);
            --tle-color: #f59e0b;
            --tle-glow: rgba(245, 158, 11, 0.2);
            --re-color: #a855f7;
            --re-glow: rgba(168, 85, 247, 0.2);
            --font-ui: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, sans-serif;
            --font-code: "Fira Code", monospace;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: var(--font-ui);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 15% 10%, rgba(56, 189, 248, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 85% 80%, rgba(168, 85, 247, 0.04) 0%, transparent 40%);
        }

        /* Top Navigation Header */
        header {
            height: 64px;
            border-bottom: 1px solid var(--border-subtle);
            background: rgba(15, 17, 24, 0.75);
            backdrop-filter: blur(16px);
            position: sticky;
            top: 0;
            z-index: 50;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 32px;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .brand-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: linear-gradient(135deg, #0284c7, #6366f1);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 16px var(--accent-glow);
        }
        .brand-icon svg { width: 18px; height: 18px; fill: white; }
        .brand-title {
            font-weight: 800;
            font-size: 18px;
            letter-spacing: -0.02em;
            background: linear-gradient(180deg, #ffffff, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #34d399;
            padding: 5px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
        }
        .pulse-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10b981;
            box-shadow: 0 0 8px #10b981;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.4); opacity: 0.5; }
        }
        .header-links a {
            color: var(--text-muted);
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
            transition: color 0.15s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .header-links a:hover { color: var(--accent-primary); }

        /* Main Workspace Container */
        main {
            flex: 1;
            max-width: 1560px;
            width: 100%;
            margin: 0 auto;
            padding: 24px 32px 32px 32px;
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 24px;
        }

        /* Workstation Panels */
        .panel {
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        }

        /* Editor Control Header */
        .panel-header {
            padding: 12px 18px;
            background: rgba(21, 24, 36, 0.6);
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
        }
        .lang-tabs {
            display: flex;
            background: rgba(0, 0, 0, 0.3);
            padding: 3px;
            border-radius: 8px;
            border: 1px solid var(--border-subtle);
        }
        .lang-tab {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.15s;
        }
        .lang-tab.active {
            background: var(--accent-primary);
            color: #04101e;
            box-shadow: 0 0 12px var(--accent-glow);
        }
        .preset-group {
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .preset-btn {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-subtle);
            color: var(--text-muted);
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }
        .preset-btn:hover {
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-main);
            border-color: rgba(255, 255, 255, 0.2);
        }

        /* Constraint Dials Bar */
        .controls-bar {
            display: flex;
            align-items: center;
            gap: 20px;
            padding: 10px 18px;
            background: rgba(0, 0, 0, 0.2);
            border-bottom: 1px solid var(--border-subtle);
            font-size: 12px;
            color: var(--text-muted);
        }
        .control-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .control-input {
            width: 72px;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            padding: 4px 8px;
            border-radius: 6px;
            font-family: var(--font-code);
            font-size: 12px;
            outline: none;
        }
        .control-input:focus { border-color: var(--border-focus); }

        /* Code Editor Area */
        .editor-wrapper {
            flex: 1;
            position: relative;
            min-height: 380px;
            background: #090a0f;
        }
        textarea.code-editor {
            width: 100%;
            height: 100%;
            background: transparent;
            border: none;
            color: #e2e8f0;
            padding: 16px 20px;
            font-family: var(--font-code);
            font-size: 13.5px;
            line-height: 1.6;
            resize: none;
            outline: none;
            tab-size: 4;
            white-space: pre;
        }

        /* I/O Drawers */
        .io-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            border-top: 1px solid var(--border-subtle);
            background: #0b0d13;
        }
        .io-box {
            padding: 12px 16px;
            display: flex;
            flex-direction: column;
        }
        .io-box:first-child { border-right: 1px solid var(--border-subtle); }
        .io-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-dim);
            font-weight: 700;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
        }
        .io-input {
            width: 100%;
            height: 72px;
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            color: #f1f5f9;
            padding: 8px 10px;
            font-family: var(--font-code);
            font-size: 12px;
            resize: none;
            outline: none;
        }
        .io-input:focus { border-color: var(--border-focus); }

        /* Action Bar */
        .action-bar {
            padding: 12px 18px;
            background: rgba(21, 24, 36, 0.7);
            border-top: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .btn-primary {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 22px;
            font-size: 13.5px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(2, 132, 199, 0.3);
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.2s;
        }
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45);
        }
        .btn-primary:active { transform: translateY(0); }
        .btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
        .kbd-badge {
            background: rgba(0, 0, 0, 0.25);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10.5px;
            font-family: var(--font-code);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-subtle);
            color: var(--text-muted);
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
        }
        .btn-secondary:hover { background: rgba(255, 255, 255, 0.1); color: var(--text-main); }

        /* Telemetry & Mission Control Panel (Right Column) */
        .verdict-hero {
            padding: 24px;
            background: linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, transparent 100%);
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }
        .verdict-title-box h3 {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-dim);
            font-weight: 700;
            margin-bottom: 4px;
        }
        .verdict-display {
            font-size: 32px;
            font-weight: 900;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .verdict-tag {
            font-size: 14px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 9999px;
            background: rgba(255, 255, 255, 0.08);
        }

        /* Metric Tiles Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            padding: 18px;
            border-bottom: 1px solid var(--border-subtle);
        }
        .metric-card {
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            padding: 14px;
            position: relative;
        }
        .metric-card-label {
            font-size: 11px;
            color: var(--text-dim);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .metric-card-val {
            font-size: 20px;
            font-weight: 800;
            font-family: var(--font-code);
            color: var(--text-main);
        }
        .metric-card-sub {
            font-size: 10.5px;
            color: var(--text-dim);
            margin-top: 4px;
        }

        /* Terminal Displays */
        .terminal-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #090a0f;
            overflow: hidden;
        }
        .terminal-header {
            padding: 10px 18px;
            background: rgba(21, 24, 36, 0.4);
            border-bottom: 1px solid var(--border-subtle);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-dim);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .terminal-body {
            padding: 14px 18px;
            font-family: var(--font-code);
            font-size: 12.5px;
            line-height: 1.6;
            overflow-y: auto;
            flex: 1;
            white-space: pre-wrap;
            color: #cbd5e1;
        }
        .terminal-stdout { color: #34d399; }
        .terminal-stderr { color: #f87171; }
        .copy-pill {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-subtle);
            color: var(--text-dim);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .copy-pill:hover { color: var(--text-main); background: rgba(255, 255, 255, 0.1); }

        /* Dynamic Verdict Color Classes */
        .is-AC { color: var(--ac-color); text-shadow: 0 0 20px var(--ac-glow); }
        .is-WA { color: var(--wa-color); text-shadow: 0 0 20px var(--wa-glow); }
        .is-TLE { color: var(--tle-color); text-shadow: 0 0 20px var(--tle-glow); }
        .is-RE { color: var(--re-color); text-shadow: 0 0 20px var(--re-glow); }
        .is-CE { color: var(--wa-color); text-shadow: 0 0 20px var(--wa-glow); }
        .is-IDLE { color: var(--text-dim); }

        @media (max-width: 1024px) {
            main { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <!-- Header Navigation -->
    <header>
        <div class="brand">
            <div class="brand-icon">
                <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
            </div>
            <span class="brand-title">VESPER</span>
            <div class="status-badge">
                <div class="pulse-dot"></div>
                <span id="backendStatus">Dual Engine Active</span>
            </div>
        </div>
        <div class="header-links">
            <a href="/docs" target="_blank">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                REST API Docs
            </a>
        </div>
    </header>

    <!-- Main Studio Workspace -->
    <main>
        <!-- Left Panel: Code & Constraints -->
        <section class="panel">
            <div class="panel-header">
                <div class="lang-tabs">
                    <button class="lang-tab active" onclick="switchLang('py')">Python 3</button>
                    <button class="lang-tab" onclick="switchLang('cpp')">C++ 17</button>
                    <button class="lang-tab" onclick="switchLang('java')">Java 17+</button>
                </div>
                <div class="preset-group">
                    <span style="font-size: 11px; color: var(--text-dim); font-weight: 700; text-transform: uppercase;">Presets:</span>
                    <button class="preset-btn" onclick="applyPreset('ac')">AC</button>
                    <button class="preset-btn" onclick="applyPreset('tle')">TLE</button>
                    <button class="preset-btn" onclick="applyPreset('re')">RE</button>
                    <button class="preset-btn" onclick="applyPreset('ce')">CE</button>
                </div>
            </div>

            <div class="controls-bar">
                <div class="control-item">
                    <span>Timeout:</span>
                    <input type="number" id="time_limit" class="control-input" value="1.0" step="0.1" min="0.1" max="10.0">
                    <span>sec</span>
                </div>
                <div class="control-item">
                    <span>Memory:</span>
                    <input type="number" id="memory_limit" class="control-input" value="128" step="16" min="16" max="1024">
                    <span>MB</span>
                </div>
                <div class="control-item" style="margin-left: auto;">
                    <span style="color: var(--text-dim);">PID Cap:</span>
                    <span style="font-family: var(--font-code); color: var(--accent-primary);">64</span>
                </div>
            </div>

            <div class="editor-wrapper">
                <textarea id="src_code" class="code-editor" spellcheck="false"></textarea>
            </div>

            <div class="io-container">
                <div class="io-box">
                    <div class="io-label">
                        <span>Standard Input (stdin)</span>
                    </div>
                    <textarea id="std_in" class="io-input" placeholder="Inputs fed to program..."></textarea>
                </div>
                <div class="io-box">
                    <div class="io-label">
                        <span>Expected Output (for AC check)</span>
                    </div>
                    <textarea id="expected_out" class="io-input" placeholder="Expected ground truth..."></textarea>
                </div>
            </div>

            <div class="action-bar">
                <div style="display: flex; gap: 10px;">
                    <button id="runBtn" class="btn-primary" onclick="executeSubmission()">
                        <span>Execute & Arbitrate</span>
                        <span class="kbd-badge">Ctrl + ↵</span>
                    </button>
                    <button class="btn-secondary" onclick="executeCustom()">Custom Run</button>
                </div>
                <button class="btn-secondary" onclick="clearEditor()" style="padding: 10px 12px;">Reset</button>
            </div>
        </section>

        <!-- Right Panel: Telemetry & Terminal -->
        <section class="panel">
            <div class="verdict-hero">
                <div class="verdict-title-box">
                    <h3>Verdict State</h3>
                    <div id="verdictText" class="verdict-display is-IDLE">
                        READY
                        <span id="verdictBadge" class="verdict-tag" style="display: none;">—</span>
                    </div>
                </div>
                <div id="verdictIndicator" style="width: 14px; height: 14px; border-radius: 50%; background: var(--text-dim);"></div>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-card-label">Execution Time</div>
                    <div id="metricLatency" class="metric-card-val">—</div>
                    <div class="metric-card-sub">Wall-Clock Latency</div>
                </div>
                <div class="metric-card">
                    <div class="metric-card-label">Peak Memory</div>
                    <div id="metricMemory" class="metric-card-val">—</div>
                    <div class="metric-card-sub">Resident Set Size</div>
                </div>
                <div class="metric-card">
                    <div class="metric-card-label">Exit Status</div>
                    <div id="metricExitCode" class="metric-card-val">—</div>
                    <div class="metric-card-sub">POSIX Signal / Exit</div>
                </div>
            </div>

            <div class="terminal-container">
                <div class="terminal-header">
                    <span>Program Output (stdout)</span>
                    <button class="copy-pill" onclick="copyStdout()">Copy Output</button>
                </div>
                <div id="stdoutConsole" class="terminal-body terminal-stdout">// Output will appear here upon evaluation...</div>

                <div class="terminal-header" style="border-top: 1px solid var(--border-subtle);">
                    <span>Diagnostics & Error Stream (stderr)</span>
                </div>
                <div id="stderrConsole" class="terminal-body terminal-stderr" style="min-height: 90px; max-height: 150px;">// Clean state. Zero runtime errors.</div>
            </div>
        </section>
    </main>

    <script>
        let currentLang = 'py';

        const PRESETS = {
            py: {
                ac: {
                    src: '# Python 3: Precision Mathematical Sum\\na = int(input())\\nb = int(input())\\nprint(f"Computed Sum: {a + b}")',
                    stdin: '45\\n55',
                    expected: 'Computed Sum: 100'
                },
                tle: {
                    src: '# Triggering Sandboxed Time Limit Exceeded (TLE)\\nimport time\\nprint("Starting heavy loop...")\\nwhile True:\\n    time.sleep(0.05)',
                    stdin: '',
                    expected: 'Done'
                },
                re: {
                    src: '# Triggering Sandboxed Runtime Error (RE)\\narray = [10, 20, 30]\\nprint(array[99]) # IndexError: list index out of range',
                    stdin: '',
                    expected: '10'
                },
                ce: {
                    src: '# Triggering Compilation & Syntax Error (CE)\\ndef invalid_syntax(:\\n    return True',
                    stdin: '',
                    expected: '0'
                }
            },
            cpp: {
                ac: {
                    src: '// C++17 High-Throughput I/O\\n#include <iostream>\\nusing namespace std;\\n\\nint main() {\\n    ios_base::sync_with_stdio(false);\\n    cin.tie(NULL);\\n    long long a, b;\\n    if (cin >> a >> b) {\\n        cout << "Computed Sum: " << (a + b) << "\\n";\\n    }\\n    return 0;\\n}',
                    stdin: '45\\n55',
                    expected: 'Computed Sum: 100'
                },
                tle: {
                    src: '// Infinite Loop Containment\\n#include <iostream>\\nusing namespace std;\\n\\nint main() {\\n    while(true) {\\n        // Consuming clock ticks\\n    }\\n    return 0;\\n}',
                    stdin: '',
                    expected: 'Never'
                },
                re: {
                    src: '// Triggering SIGSEGV (Segmentation Fault - Code 139)\\n#include <iostream>\\nusing namespace std;\\n\\nint main() {\\n    int* ptr = nullptr;\\n    *ptr = 1337;\\n    return 0;\\n}',
                    stdin: '',
                    expected: '1337'
                },
                ce: {
                    src: '// Missing closing bracket (CE)\\n#include <iostream>\\nint main() {\\n    std::cout << "Missing bracket"',
                    stdin: '',
                    expected: '0'
                }
            },
            java: {
                ac: {
                    src: 'import java.util.Scanner;\\n\\npublic class UserProgram {\\n    public static void main(String[] args) {\\n        Scanner sc = new Scanner(System.in);\\n        if (sc.hasNextLong()) {\\n            long a = sc.nextLong();\\n            long b = sc.nextLong();\\n            System.out.println("Computed Sum: " + (a + b));\\n        }\\n    }\\n}',
                    stdin: '45\\n55',
                    expected: 'Computed Sum: 100'
                },
                tle: {
                    src: 'public class UserProgram {\\n    public static void main(String[] args) {\\n        while(true) {}\\n    }\\n}',
                    stdin: '',
                    expected: 'Done'
                },
                re: {
                    src: 'public class UserProgram {\\n    public static void main(String[] args) {\\n        int val = 100 / 0; // ArithmeticException\\n    }\\n}',
                    stdin: '',
                    expected: 'Done'
                },
                ce: {
                    src: 'public class UserProgram {\\n    public static void main(String[] args) {\\n        broken syntax here;\\n    }\\n}',
                    stdin: '',
                    expected: '0'
                }
            }
        };

        function switchLang(lang) {
            currentLang = lang;
            document.querySelectorAll('.lang-tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            applyPreset('ac');
        }

        function applyPreset(type) {
            const data = PRESETS[currentLang][type];
            document.getElementById('src_code').value = data.src;
            document.getElementById('std_in').value = data.stdin;
            document.getElementById('expected_out').value = data.expected;
        }

        function clearEditor() {
            document.getElementById('src_code').value = '';
            document.getElementById('std_in').value = '';
            document.getElementById('expected_out').value = '';
        }

        async function executeSubmission() {
            const btn = document.getElementById('runBtn');
            btn.disabled = true;
            btn.innerHTML = '<span>Arbitrating...</span>';

            const payload = {
                language: currentLang,
                src_code: document.getElementById('src_code').value,
                std_in: document.getElementById('std_in').value,
                expected_out: document.getElementById('expected_out').value,
                time_limit: parseFloat(document.getElementById('time_limit').value),
                memory_limit: parseInt(document.getElementById('memory_limit').value)
            };

            try {
                const res = await fetch('/api/evaluate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                renderTelemetry(result);
            } catch (err) {
                alert('Connection failure: ' + err);
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<span>Execute & Arbitrate</span><span class="kbd-badge">Ctrl + ↵</span>';
            }
        }

        async function executeCustom() {
            const payload = {
                language: currentLang,
                src_code: document.getElementById('src_code').value,
                std_in: document.getElementById('std_in').value,
                time_limit: parseFloat(document.getElementById('time_limit').value),
                memory_limit: parseInt(document.getElementById('memory_limit').value)
            };

            try {
                const res = await fetch('/api/run-custom', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                renderTelemetry(result);
            } catch (err) {
                alert('Connection failure: ' + err);
            }
        }

        function renderTelemetry(data) {
            const vText = document.getElementById('verdictText');
            const vBadge = document.getElementById('verdictBadge');
            const vDot = document.getElementById('verdictIndicator');

            vText.className = 'verdict-display is-' + data.verdict;
            vText.childNodes[0].nodeValue = data.verdict + ' ';
            vBadge.style.display = 'inline-block';
            vBadge.innerText = data.verdict_desc ? data.verdict_desc.split(' - ')[0] : data.verdict;

            const colorMap = {
                'AC': '#10b981',
                'WA': '#f43f5e',
                'TLE': '#f59e0b',
                'RE': '#a855f7',
                'CE': '#f43f5e',
                'OLE': '#f59e0b'
            };
            vDot.style.background = colorMap[data.verdict] || '#64748b';
            vDot.style.boxShadow = '0 0 12px ' + (colorMap[data.verdict] || 'transparent');

            document.getElementById('metricLatency').innerText = data.execution_time_ms.toFixed(2) + ' ms';
            document.getElementById('metricMemory').innerText = data.memory_kb > 0 ? (data.memory_kb / 1024).toFixed(2) + ' MB' : '< 1 MB';
            document.getElementById('metricExitCode').innerText = data.exit_code === 0 ? '0 (SUCCESS)' : data.exit_code;

            document.getElementById('stdoutConsole').innerText = data.output || '// Process exited with zero stdout bytes.';
            document.getElementById('stderrConsole').innerText = data.error || data.compile_output || '// Zero errors or stderr detected.';
        }

        function copyStdout() {
            const text = document.getElementById('stdoutConsole').innerText;
            navigator.clipboard.writeText(text);
        }

        // Keyboard Shortcut: Ctrl + Enter / Cmd + Enter to run
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                executeSubmission();
            }
        });

        // Load Initial State
        window.onload = () => {
            applyPreset('ac');
            fetch('/api/health')
                .then(r => r.json())
                .then(h => {
                    document.getElementById('backendStatus').innerText = h.backend;
                })
                .catch(() => {});
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
