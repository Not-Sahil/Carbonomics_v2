# Contributing to Carbonomics v3

Thank you for contributing to Carbonomics v3! This project is maintained collaboratively by four core developers.

---

## 1. Feature Branch Workflow

Always create a dedicated feature branch from `v3-development` or `main`:
```bash
git checkout -b feature/your-feature-name
```

Before committing:
1. Verify Python unit tests pass:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```
2. Verify Next.js build passes:
   ```bash
   cd frontend
   npm run build
   ```
3. Never commit `__pycache__`, `.venv`, or `.env` files.

---

## 2. Coding Standards
- **Backend:** PEP 8 compliance, explicit type hints in function signatures.
- **Frontend:** TypeScript strict mode, functional React components with Tailwind CSS.
- **Physics & Math:** All carbon equations must follow the Green Software Foundation SCI specification.

