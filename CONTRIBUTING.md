# Contributing to Femicide Data Tracker Pipeline

Thank you for your interest in contributing. This project supports the
[We Will Stop Femicide Platform](https://www.kadincinayetlerinidurduracagiz.net/)
and all contributions are reviewed and approved by the project maintainer before merging.

---

## Ground Rules

- No one may push directly to `main`. All changes go through a Pull Request.
- All Pull Requests require approval from the maintainer (@ztatli) before merging.
- Keep contributions focused: one topic per PR (e.g. new keywords, new city sources, a bug fix).
- This project is licensed under GPL v3. By contributing, you agree your code is also GPL v3.

---

## How to Contribute

### 1. Fork the repository
Click **Fork** on the top right of the GitHub page. This creates your own copy.

### 2. Create a feature branch
In your fork, create a new branch from `main`:
```bash
git checkout -b feature/your-branch-name
```

Use a descriptive name, for example:
- `feature/add-ankara-sources`
- `fix/keyword-false-positives`
- `feature/extend-keywords`

### 3. Make your changes
Edit the relevant files. Common contribution types:

| What | File |
|------|------|
| Add/update keywords | `config.py` → `CATEGORY_KEYWORDS` |
| Add a new city source list | `sources/` → new CSV file |
| Fix a scraping bug | `01_build_sources.py` or `02_scrape_news.py` |
| Improve documentation | `README.md` |

### 4. Commit and push
```bash
git add .
git commit -m "Short description of what you changed"
git push origin feature/your-branch-name
```

### 5. Open a Pull Request
Go to the original repository on GitHub and click **New Pull Request**.
- Set base branch: `main`
- Describe what you changed and why

The maintainer will review and either approve, request changes, or close the PR.

---

## What NOT to do

- Do not push directly to `main`
- Do not submit PRs that add unrelated features or refactor working code without discussion
- Do not include real victim data or personal information in any file tracked by git

---

## Questions?

Open a GitHub Issue to start a discussion before making large changes.
