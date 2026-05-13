# Contributing to Anime Voice Forge

Thank you for considering contributing to this project.

---

## Getting Started

1. Fork the repository and clone your fork locally.
2. Create a new branch from `main` for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Set up the development environment:
   ```bash
   # Backend
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   source .venv/bin/activate # Linux/macOS
   pip install -r backend/requirements.txt
   pip install ruff pytest

   # Dashboard
   cd dashboard
   npm install
   ```

---

## Code Style

### Python (Backend)
- Follow PEP 8 conventions.
- Use type hints for function signatures.
- Keep functions focused — one responsibility per function.
- Use `ruff` for linting:
  ```bash
  ruff check backend/ tests/
  ```

### TypeScript (Dashboard)
- Use strict TypeScript — no `any` where avoidable.
- Components should be functional with typed props.
- Run type checking before committing:
  ```bash
  cd dashboard
  npx tsc --noEmit
  ```

---

## Testing

Run the full test suite before submitting a pull request:

```bash
# Backend unit and integration tests
python -m pytest tests/ -v

# Dashboard type check and build
cd dashboard
npx tsc --noEmit
npm run build
```

---

## Pull Request Guidelines

1. Write a clear title and description explaining the change.
2. Reference any related issues in the PR description.
3. Include tests for new functionality.
4. Ensure all existing tests pass.
5. Keep commits focused — one logical change per commit.

---

## Reporting Issues

When filing a bug report, include:
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Python version, Node.js version, and OS
- GPU model if the issue is related to inference

---

## Voice Samples and Copyright

Do not commit copyrighted audio files to the repository. Voice samples in `voice_samples/` are gitignored by default. If you need to share a voice sample for testing, use a reference to a publicly available source instead.

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
