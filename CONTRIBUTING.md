# 🤝 Contributing to DataSentry

Thank you for your interest in contributing to **DataSentry**! We welcome contributions from developers, data scientists, and students of all experience levels—especially participants in open-source programs like **SWOC (Social Winter of Code)**.

---

## 🛠️ Tech Stack Overview

DataSentry combines two primary domains:
- **Machine Learning & Data Science**: Pandas, NumPy, Scikit-Learn (Isolation Forest), PyOD, SciPy.
- **Full-Stack Web & CLI**: Python (FastAPI), React 18 (TypeScript, Tailwind CSS, Recharts), Typer CLI.

---

## 🚀 Setting Up Your Local Environment

### 1. Fork & Clone
```bash
git clone https://github.com/<your-username>/datasentry.git
cd datasentry
```

### 2. Set Up Python Core Engine
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

### 3. Verify Tests
```bash
pytest tests/
```

### 4. Test the CLI
```bash
datasentry profile data/sample.csv
datasentry detect-anomalies data/sample.csv
```

### 5. Start the React Frontend (Optional, for UI work)
```bash
cd frontend
npm install
npm run dev
```

---

## 🏷️ Issue Labels & SWOC Tracks

We organize issues to help you find the best match for your skills:
* `good first issue`: Beginner-friendly tasks (documentation, regex patterns, small UI tweaks).
* `track:ml`: Machine learning, anomaly detection algorithms, statistical tests, data drift.
* `track:backend`: FastAPI endpoints, Pydantic schemas, file ingestion, database models.
* `track:frontend`: React components, Recharts visualizations, Tailwind styling, state management.
* `track:cli`: Typer commands, Rich terminal output, command-line arguments.

---

## 📝 Pull Request Guidelines

1. **Branch Naming**: Use descriptive prefixes:
   - `feat/ml-lof-detector`
   - `fix/profiler-null-handling`
   - `docs/update-readme`
2. **Commit Messages**: Follow standard conventional commits:
   - `feat(ml): implement Local Outlier Factor detector`
   - `fix(validator): handle empty string in regex check`
3. **Tests**: Ensure existing tests pass (`pytest`) and add tests for newly introduced functionality.

---

## 💬 Community & Support

Join our discussion board on GitHub Issues / Discord for questions and mentorship during SWOC. Happy hacking!
