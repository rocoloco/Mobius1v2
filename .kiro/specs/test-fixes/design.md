# Design Document: Test Suite Fixes

## Overview

This design addresses three critical issues in the Mobius Phase 2 test suite:
1. **40 failing unit tests** due to unmocked Supabase client dependencies
2. **Slow property-based tests** taking 3+ minutes to complete
3. **Deprecation warnings** from datetime.utcnow() usage

The solution involves proper dependency mocking, environment-based test configuration, and modernizing datetime usage.

## Architecture

### Current Test Structure

```
tests/
├── unit/                    # 10 test files, 113 tests (73 pass, 40 fail)
│   ├── test_system_endpoints.py  # 8 failures - Supabase not mocked
│   ├── test_template_routes.py   # 2 failures - Supabase not mocked
│   └── ...                        # 30 other failures
├── integration/             # 4 test files, ~15 tests
│   └── ...
└── property/                # 24 test files, 24 tests (100 examples each)
    └── ...                  # Takes 3+ minutes to run
```

### Root Causes

#### Issue 1: Unmocked Supabase Client
```python
# Current code in routes.py
def health_check_handler():
    client = get_supabase_client()  # Requires env vars
    result = client.table("brands").select("brand_id").limit(1).execute()
```

**Problem**: Tests call real `get_supabase_client()` which fails without SUPABASE_URL/SUPABASE_KEY.

#### Issue 2: Slow Property Tests
```python
# Current configuration
@given(...)
@settings(max_examples=100, deadline=None)  # Always 100 examples
async def test_something():
    ...
```

**Problem**: 24 tests × 100 examples = 2,400+ test executions.

#### Issue 3: Deprecated Datetime
```python
# Current code
from datetime import datetime
timestamp = datetime.utcnow()  # Deprecated in Python 3.12
```

**Problem**: Generates deprecation warnings that clutter test output.

## Components and Interfaces

### 1. Supabase Client Mocking Strategy

**Approach**: Mock at the import level, not the instance level.

```python
# In test files
from unittest.mock import patch, Mock

@patch("mobius.api.routes.get_supabase_client")
async def test_health_check_all_healthy(mock_get_client):
    """Test health check with all services healthy."""
    
    # Create mock client
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    
    # Mock database query
    mock_result = Mock()
    mock_result.data = [{"brand_id": "test-123"}]
    mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_result
    
    # Mock storage access
    mock_client.storage.from_.return_value.list.return_value = []
    
    # Run test
    response = await health_check_handler()
    
    # Verify
    assert response["status"] == "healthy"
    assert response["database"] == "healthy"
    assert response["storage"] == "healthy"
```

**Key Points**:
- Mock `get_supabase_client()` at module level
- Return a Mock object with chained method calls
- Configure mock to return expected data structures
- Verify behavior without requiring real database

### 2. Hypothesis Configuration

**Approach**: Use environment-based profiles.

```python
# In conftest.py
import os
from hypothesis import settings, Verbosity

# Register profiles
settings.register_profile(
    "ci",
    max_examples=10,
    deadline=None,
    verbosity=Verbosity.normal
)

settings.register_profile(
    "dev",
    max_examples=100,
    deadline=None,
    verbosity=Verbosity.normal
)

# Load profile based on environment
if os.getenv("CI") or os.getenv("QUICK_TESTS"):
    settings.load_profile("ci")
else:
    settings.load_profile("dev")
```

**Usage**:
```bash
# Quick tests (10 examples per property)
QUICK_TESTS=1 pytest tests/property/

# Full tests (100 examples per property)
pytest tests/property/
```

**Performance Impact**:
- Quick mode: ~1-2 minutes (24 tests × 10 examples = 240 executions)
- Full mode: ~3-5 minutes (24 tests × 100 examples = 2,400 executions)

### 3. Datetime Modernization

**Approach**: Replace all `datetime.utcnow()` with `datetime.now(timezone.utc)`.

```python
# Old (deprecated)
from datetime import datetime
timestamp = datetime.utcnow()

# New (timezone-aware)
from datetime import datetime, timezone
timestamp = datetime.now(timezone.utc)
```

**Files to Update**:
- `src/mobius/api/routes.py` - Multiple locations
- `tests/unit/test_system_endpoints.py` - Multiple locations
- Any other files using `utcnow()`

**Benefits**:
- No deprecation warnings
- Timezone-aware datetimes (best practice)
- Future-proof for Python 3.13+

## Implementation Strategy

### Phase 1: Fix System Endpoint Tests (8 failures)

1. Add `@patch("mobius.api.routes.get_supabase_client")` to each test
2. Configure mock client with proper return values
3. Mock database queries: `client.table().select().limit().execute()`
4. Mock storage access: `client.storage.from_().list()`
5. Verify tests pass

### Phase 2: Fix Template Route Tests (2 failures)

1. Add `@patch("mobius.api.routes.get_supabase_client")` to failing tests
2. Ensure BrandStorage and JobStorage mocks are configured
3. Mock job creation and brand retrieval
4. Verify tests pass

### Phase 3: Fix Remaining Unit Tests (30 failures)

1. Identify failure patterns
2. Apply appropriate mocking strategy
3. Verify all unit tests pass

### Phase 4: Optimize Property Tests

1. Add Hypothesis configuration to `conftest.py`
2. Test with `QUICK_TESTS=1` to verify 10 examples work
3. Test without `QUICK_TESTS` to verify 100 examples work
4. Measure performance improvement

### Phase 5: Fix Datetime Deprecations

1. Search for all `datetime.utcnow()` usage
2. Replace with `datetime.now(timezone.utc)`
3. Add `timezone` import where needed
4. Verify no deprecation warnings

### Phase 6: Update Documentation

1. Update README.md with test execution strategies
2. Update docs/testing-notes.md with configuration details
3. Add CI/CD workflow examples
4. Document QUICK_TESTS environment variable

## Testing Strategy

### Verification Steps

1. **Unit Tests**: `pytest tests/unit/ -v`
   - Expected: 0 failures, ~113 tests pass
   - Time: < 1 second

2. **Integration Tests**: `pytest tests/integration/ -v`
   - Expected: 0 failures, ~15 tests pass
   - Time: < 30 seconds

3. **Property Tests (Quick)**: `QUICK_TESTS=1 pytest tests/property/ -v`
   - Expected: 0 failures, 24 tests pass
   - Time: < 2 minutes

4. **Property Tests (Full)**: `pytest tests/property/ -v`
   - Expected: 0 failures, 24 tests pass
   - Time: < 5 minutes

5. **Full Suite (Quick)**: `QUICK_TESTS=1 pytest -v`
   - Expected: 0 failures, ~152 tests pass
   - Time: < 3 minutes

### Success Criteria

- ✅ All unit tests pass (0 failures)
- ✅ All integration tests pass (0 failures)
- ✅ All property tests pass (0 failures)
- ✅ Quick mode completes in < 2 minutes
- ✅ No deprecation warnings
- ✅ Clear documentation for test execution

## Error Handling

### Mock Configuration Errors

If mocks are not properly configured, tests may fail with:
- `AttributeError: Mock object has no attribute 'X'`
- `TypeError: 'Mock' object is not callable`

**Solution**: Ensure mock chains are complete:
```python
mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_result
```

### Hypothesis Configuration Errors

If Hypothesis profiles are not loaded correctly:
- Tests may still run 100 examples in quick mode
- Environment variable may not be detected

**Solution**: Add debug logging to conftest.py:
```python
import logging
logger = logging.getLogger(__name__)

if os.getenv("QUICK_TESTS"):
    logger.info("Loading Hypothesis 'ci' profile (10 examples)")
    settings.load_profile("ci")
else:
    logger.info("Loading Hypothesis 'dev' profile (100 examples)")
    settings.load_profile("dev")
```

## Performance Metrics

### Before Fixes

- Unit tests: 73 pass, 40 fail (0.86s)
- Integration tests: Mostly passing (~30s)
- Property tests: Timeout after 3+ minutes
- **Total**: Cannot complete full suite

### After Fixes (Expected)

- Unit tests: 113 pass, 0 fail (< 1s)
- Integration tests: 15 pass, 0 fail (< 30s)
- Property tests (quick): 24 pass, 0 fail (< 2 min)
- Property tests (full): 24 pass, 0 fail (< 5 min)
- **Total (quick mode)**: 152 pass, 0 fail (< 3 min)

### Performance Improvement

- **Quick mode**: 10x faster property tests (10 vs 100 examples)
- **Reliability**: 100% pass rate (vs 64% before)
- **CI/CD ready**: < 3 minute test suite (vs timeout before)

## Conclusion

These fixes will transform the test suite from unreliable and slow to fast and dependable. The key improvements are:

1. **Proper mocking** eliminates configuration dependencies
2. **Environment-based configuration** enables fast feedback loops
3. **Modern datetime usage** eliminates deprecation warnings
4. **Clear documentation** helps developers choose the right test strategy

The result is a CI/CD-ready test suite that provides confidence without sacrificing speed.
