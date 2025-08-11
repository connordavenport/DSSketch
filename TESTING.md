# DSSketch Testing Guide

Comprehensive guide for testing DSSketch in VSCode, Cursor, and other IDEs.

## Quick Start

### Prerequisites
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Or install manually
pip install pytest pytest-cov black ruff mypy
```

### Running Tests

**In VSCode/Cursor:**
- `Ctrl+Shift+P` → "Tasks: Run Test Task" → "Run All Tests"
- `F5` → "Run Current Test File" (for open test files)  
- Test Explorer: Auto-discovers tests in sidebar

**Command Line:**
```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_parsers/test_dss_parser.py -v

# Single test method
python -m pytest tests/test_utils/test_patterns.py::TestPatternMatcher::test_exact_pattern_matching -v

# With coverage
python -m pytest tests/ -v --cov=dssketch --cov-report=html
```

## Test Structure

```
tests/
├── conftest.py                     # Shared fixtures and configuration
├── fixtures/                      # Test data and UFO files
│   ├── ufo_masters/               # 18 comprehensive UFO files
│   ├── designspace/               # Test DesignSpace files
│   ├── TestFont-*.dssketch        # Test DSSketch files
│   └── test_fixtures.py           # Fixture validation tests
├── test_parsers/                  # DSSketch parser tests
├── test_converters/               # DesignSpace ↔ DSSketch conversion
├── test_utils/                    # Utility function tests
└── test_integration/              # Round-trip and integration tests
```

## Available Test Tasks

### VSCode/Cursor Tasks (Ctrl+Shift+P → Tasks)

**Testing:**
- `Run All Tests` - Full test suite with verbose output
- `Run Tests with Coverage` - Tests + HTML coverage report
- `Run Current Test File` - Test currently open file
- `Test DSSketch Fixtures` - Validate comprehensive test fixtures

**Development:**
- `Lint Code (Ruff)` - Check code style and potential issues
- `Format Code (Black)` - Auto-format all Python files  
- `Type Check (MyPy)` - Static type checking
- `Install Dev Dependencies` - Setup development environment

**DSSketch Specific:**
- `DSSketch: Convert Current File` - Convert open .designspace or .dssketch
- `DSSketch: Round-trip Test` - Test bidirectional conversion
- `DSSketch: Test with Examples` - Quick conversion test

### Debug Configurations (F5)

**Test Debugging:**
- `Run Current Test File` - Debug open test file
- `Run All Tests` - Debug entire test suite
- `Run Specific Test Method` - Debug single test (with prompt)

**DSSketch Debugging:**
- `Debug DSSketch CLI` - Step through CLI conversion
- `Debug Test Fixtures` - Debug fixture validation

## Test Categories

### 1. Parser Tests (`test_parsers/`)
Tests DSSketch format parsing:
- ✅ Basic structure (family, axes, masters)
- ✅ Wildcard rules (`A*`, `dol* cen*`)
- ✅ Compound conditions (`weight >= 600 && italic == 1`)
- ✅ Discrete axes (`ital discrete`)
- ✅ Comments and edge cases

### 2. Converter Tests (`test_converters/`)  
Tests DesignSpace ↔ DSSketch conversion:
- ✅ Axis mapping preservation
- ✅ Master source handling
- ✅ Rule conversion and grouping
- ✅ Discrete axis detection
- ✅ Instance generation

### 3. Utility Tests (`test_utils/`)
Tests wildcard pattern matching:
- ✅ Exact glyph matching
- ✅ Prefix wildcards (`A*`, `dollar*`)
- ✅ Grouped patterns (`dol* cen*`)
- ✅ Universal wildcards (`*`)
- ✅ Pattern validation and edge cases

### 4. Integration Tests (`test_integration/`)
Tests end-to-end functionality:
- ✅ Round-trip conversion (DesignSpace → DSSketch → DesignSpace)
- ✅ Rule preservation and semantic consistency  
- ✅ File I/O with real examples
- ✅ Complex wildcard expansion

## Test Fixtures

### Comprehensive UFO Masters
- **18 UFO files**: 9 Roman (Thin-Black) + 9 Italic  
- **38+ glyphs each**: A-Z variants, currency symbols, digits
- **7 variant types**: .alt, .rvrn, .heavy, .light, .small, .tabular, .swash
- **Realistic scaling**: Proper weight/stem progression

### DesignSpace Test Files
- `TestFont-Weight.designspace` - Weight-only axis
- `TestFont-WeightItalic.designspace` - Weight + discrete italic

### DSSketch Test Files  
- `TestFont-WeightItalic-Comprehensive.dssketch` - All rule types
- Covers exact, wildcard, grouped, and compound rules

### Rule Coverage
✅ All DSSketch rule types tested:
- Exact: `dollar > dollar.rvrn (weight >= 480)`
- Prefix wildcards: `A* > .alt (weight <= 500)`
- Grouped wildcards: `dol* cen* > .rvrn (weight >= 480)`
- Compound conditions: `ampersand > ampersand.alt (weight >= 600 && italic == 1)`
- Range conditions: `zero* > .tabular (400 <= weight <= 700)`
- Exact values: `euro > euro.small (weight == 400)`

## IDE Integration

### VSCode Settings
- **Auto-discovery**: Tests appear in Test Explorer
- **Auto-formatting**: Black formats on save
- **Auto-linting**: Ruff shows issues inline
- **Type checking**: MyPy integrated
- **File associations**: .dssketch/.dss syntax highlighting

### Test Execution
- **F5**: Debug current test file
- **Ctrl+Shift+P**: Run any test task
- **Right-click**: Run/debug individual tests
- **Status bar**: Test results and coverage

### Coverage Reports
- **Terminal**: Inline coverage percentages
- **HTML**: `htmlcov/index.html` (after coverage task)
- **VSCode**: Coverage highlights in editor (with extensions)

## Test Markers

```python
@pytest.mark.slow          # Long-running tests
@pytest.mark.integration   # Integration tests
@pytest.mark.requires_ufo  # Tests needing UFO files
```

**Run specific markers:**
```bash
# Skip slow tests
python -m pytest -m "not slow"

# Only integration tests  
python -m pytest -m integration

# Only unit tests
python -m pytest -m "not integration"
```

## Troubleshooting

### Common Issues

**"command not found: python"**
- Solution: Tasks updated to use `${workspaceFolder}/.venv/bin/python`
- Ensure virtual environment is activated

**Import errors:**
- Check `PYTHONPATH` includes `src/` directory
- Verify `pip install -e .` was run

**Missing test files:**
- Run `python tests/fixtures/test_fixtures.py` to validate fixtures
- Check UFO masters exist in `tests/fixtures/ufo_masters/`

**Test failures:**
- Use `pytest -v -s` for verbose output
- Use `pytest --tb=short` for concise tracebacks  
- Debug with F5 in VSCode for breakpoint debugging

### Performance
- **Parallel tests**: `pytest -n auto` (requires pytest-xdist)
- **Test selection**: Use markers to run subset
- **Fixture caching**: Session-scoped fixtures reduce setup time

## Writing New Tests

### Test Structure
```python
class TestNewFeature:
    """Test new DSSketch feature"""
    
    @pytest.fixture
    def sample_data(self):
        """Create test data"""
        return TestDataProvider.get_sample_data()
    
    def test_basic_functionality(self, sample_data):
        """Test basic feature behavior"""
        result = new_feature_function(sample_data)
        assert result.is_valid()
        assert len(result.items) > 0
    
    def test_edge_cases(self, sample_data):
        """Test edge cases and error handling"""
        with pytest.raises(ValueError):
            new_feature_function(None)
```

### Best Practices
- **Descriptive names**: `test_wildcard_expansion_with_missing_targets`
- **Clear assertions**: Test one concept per method
- **Use fixtures**: Reuse test data and setup
- **Mark appropriately**: Add `@pytest.mark.slow` for long tests
- **Document intent**: Clear docstrings explaining what's tested

The testing infrastructure is now fully configured and ready for comprehensive DSSketch development and validation in any modern IDE!