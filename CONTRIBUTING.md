# Contributing to Advanced Speedtest CLI

Thank you for your interest in contributing! Please follow these guidelines.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/shakilofficial0/adv-speedtest-cli.git
cd adv-speedtest-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Code Standards

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write descriptive commit messages
- Include docstrings for all functions and classes

## Testing

Before submitting, ensure:
- Code passes all existing tests
- No new warnings are introduced
- Documentation is updated

## Submission Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open Pull Request

## Reporting Issues

Include:
- Python version
- Operating system
- Reproduction steps
- Error message (if applicable)

Thank you for contributing!
