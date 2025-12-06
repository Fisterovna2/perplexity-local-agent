# Contributing to Perplexity Local Agent

First of all, **thank you for your interest!** We love community contributions.

## Code of Conduct

Be respectful, inclusive, and professional. This project is for everyone.

## How to Contribute

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR-USERNAME/perplexity-local-agent.git
cd perplexity-local-agent
git remote add upstream https://github.com/Fisterovna2/perplexity-local-agent.git
```

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Development Setup
```bash
pip install -r backend/requirements.txt
python backend/agent.py
```

### 4. Make Changes
- Write clean, documented code
- Follow PEP 8 style guide
- Add comments for complex logic
- Test your changes locally

### 5. Commit
```bash
git commit -m "type: description"
# Types: feat, fix, docs, style, refactor, test, chore, devops
```

### 6. Push & PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request with:
- Clear title
- Description of changes
- Reference to any related issues

## Ideas for Contributions

### Easy (Good for Beginners)
- [ ] Add new tool module
- [ ] Improve documentation
- [ ] Fix typos/grammar
- [ ] Update README with examples

### Medium
- [ ] Add unit tests
- [ ] Improve error handling
- [ ] Add API rate limiting
- [ ] Create CLI tool

### Advanced
- [ ] LLM integration (Ollama/LM Studio)
- [ ] Database support (SQLite/PostgreSQL)
- [ ] WebSocket real-time updates
- [ ] Advanced security features
- [ ] Multi-user authentication

## Code Style

```python
# ✅ Good
def execute_command(command: str, params: Dict) -> Dict:
    """Execute command with validation."""
    if not validate(command):
        return {"error": "Invalid"}
    return run(command, params)

# ❌ Bad
def execute(cmd, p):
    if cmd:
        return run(cmd, p)
```

## Testing

```bash
# Run tests
python -m pytest tests/

# Check coverage
pytest --cov=backend tests/
```

## Documentation

- Update README.md for user-facing changes
- Update API_DOCUMENTATION.md for API changes
- Add docstrings to all functions
- Update RELEASE_NOTES.md

## Questions?

- Open an Issue
- Start a Discussion
- Contact maintainer

## License

By contributing, you agree your work will be licensed under the MIT License.

---

**Thanks for making Perplexity Local Agent better!** 🚀
