# Contributing to Vesper ⚡

Thank you for your interest in contributing to **Vesper**! We welcome contributions that maintain our high standards of systems security, deterministic arbitration, and sub-millisecond execution performance.

---

## 📜 Code of Conduct

We are committed to providing a welcoming, inclusive, and professional environment. All contributors are expected to uphold respectful, evidence-driven collaboration.

---

## 🛠️ Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Gana-Y/vesper-engine.git
   cd vesper-engine
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies & development tools:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov ruff mypy
   ```

4. **Verify test suite:**
   ```bash
   pytest -v
   ```

---

## 🌿 Branching & Semantic Commits

We enforce the **Conventional Commits** specification. Every commit message must follow this structure:

```
<type>(<scope>): <short imperative summary>
```

### Allowed Types:
* `feat`: A new user-facing feature or language runtime
* `fix`: A bug fix or arbiter edge-case resolution
* `perf`: Performance or latency optimizations
* `refactor`: Code reorganization with zero functional changes
* `docs`: Documentation updates, specs, or architecture diagrams
* `test`: Adding missing tests or refactoring test suites
* `ci`: GitHub Actions or automation changes

### Examples:
* `feat(sandbox): add Go 1.22 runtime to container execution pool`
* `fix(arbiter): handle SIGKILL edge case during swap memory exhaustion`
* `perf(telemetry): reduce process startup overhead using warm process pools`

---

## 🧪 Testing Guidelines

* **100% Pass Rate:** All new features or bug fixes must include unit/integration tests under `tests/`.
* **Zero Host Contamination:** Never write tests that execute arbitrary host commands without proper sandboxing or mocking.
* **Deterministic Output:** Tests must not rely on flaky wall-clock timings; always allow sufficient margin for CI runners.

---

## 🚀 Pull Request Checklist

Before opening a PR, ensure:
- [ ] Code passes linting: `ruff check src/`
- [ ] Pytest suite passes 100%: `pytest -v`
- [ ] Commit history is clean with semantic commit messages.
- [ ] Documentation has been updated if new endpoints or parameters were introduced.
