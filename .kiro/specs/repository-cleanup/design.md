# Repository Cleanup Design

## Overview

This design outlines a systematic approach to cleaning up the Mobius repository while preserving all essential functionality. The cleanup will focus on removing obsolete documentation, consolidating related files, streamlining test suites, and organizing utility scripts based on the current system architecture.

## Architecture

The cleanup will follow a dependency-first approach:

1. **Dependency Analysis**: Identify all files required by the main application (`app_consolidated.py`)
2. **Test Coverage Mapping**: Ensure essential functionality remains tested
3. **Documentation Consolidation**: Merge related documents and remove temporary files
4. **Script Rationalization**: Keep only essential utilities for deployment and maintenance

## Components and Interfaces

### Core System Files (PRESERVE)
- `src/mobius/` - All source code modules
- `app_consolidated.py` - Main FastAPI application
- Configuration files: `pyproject.toml`, `.env.example`
- Database migrations: `supabase/migrations/`
- Frontend application: `frontend/` directory

### Documentation Files (CONSOLIDATE)
- Keep: `MOBIUS-ARCHITECTURE.md`, `README.md`
- Consolidate insights from: `MOAT.md`, `BRAND-GRAPH-API.md`
- Remove: Temporary fix documents (`*_FIX.md`, `*_ANALYSIS.md`)

### Test Suites (OPTIMIZE)
- Keep: All property tests (core business logic validation)
- Keep: Essential unit tests for API routes and storage
- Keep: Integration tests for end-to-end workflows
- Remove: Redundant or obsolete test files

### Utility Scripts (STREAMLINE)
- Keep: Deployment (`deploy.py`), setup (`setup_*.py`), database operations
- Keep: Neo4j graph operations (`*neo4j*`, `*moat*`)
- Remove: Temporary testing and verification scripts

## Data Models

### File Classification System

```python
class FileCategory(Enum):
    ESSENTIAL = "essential"      # Required for system operation
    CONSOLIDATE = "consolidate"  # Merge with other files
    REMOVE = "remove"           # Safe to delete
    REVIEW = "review"           # Manual review needed

class FileAction:
    path: str
    category: FileCategory
    reason: str
    dependencies: List[str] = []
    consolidate_into: Optional[str] = None
```

### Cleanup Plan Structure

```python
class CleanupPlan:
    preserve_files: List[str]
    remove_files: List[str]
    consolidate_actions: List[ConsolidateAction]
    
class ConsolidateAction:
    source_files: List[str]
    target_file: str
    merge_strategy: str  # "append", "merge_sections", "extract_insights"
```

## Error Handling

- **Dependency Validation**: Verify no essential imports are broken before removing files
- **Backup Strategy**: Create git branch before cleanup for rollback capability
- **Test Validation**: Run test suite after cleanup to ensure functionality preserved
- **Incremental Approach**: Clean up in stages with validation between each stage

## Testing Strategy

### Unit Tests
- Test file classification logic
- Validate dependency analysis accuracy
- Test consolidation merge strategies

### Property-Based Tests
- **Property 1: Dependency Preservation**: For any file marked as essential, all its dependencies must also be preserved
- **Property 2: Test Coverage Maintenance**: After cleanup, test coverage for core functionality must remain above 80%
- **Property 3: Documentation Completeness**: Consolidated documentation must contain all essential architectural information
- **Property 4: Script Functionality**: Remaining scripts must execute successfully in clean environment

### Integration Tests
- Verify main application starts after cleanup
- Validate all API endpoints remain functional
- Test deployment process with cleaned repository
- Confirm database operations work with remaining scripts

## Implementation Phases

### Phase 1: Analysis and Planning
1. Scan all files and categorize by importance
2. Analyze import dependencies from main application
3. Map test coverage to source modules
4. Create detailed cleanup plan with file-by-file actions

### Phase 2: Documentation Consolidation
1. Extract key insights from temporary analysis documents
2. Merge MOAT and Brand Graph API documentation into architecture
3. Update README with current setup instructions
4. Remove obsolete documentation files

### Phase 3: Test Suite Optimization
1. Remove redundant test files
2. Consolidate related test cases
3. Ensure core functionality remains covered
4. Update test configuration if needed

### Phase 4: Script Rationalization
1. Remove temporary testing scripts
2. Keep essential deployment and setup utilities
3. Consolidate related database operation scripts
4. Update script documentation

### Phase 5: Final Cleanup
1. Remove build artifacts and cache files
2. Clean up empty directories
3. Update .gitignore if necessary
4. Validate system functionality

## Specific File Actions

### Root Directory Files
- **Keep**: `pyproject.toml`, `README.md`, `.env.example`, `.gitignore`
- **Consolidate**: Merge `MOAT.md` insights into `MOBIUS-ARCHITECTURE.md`
- **Remove**: `*_FIX.md`, `*_ANALYSIS.md`, `FIXES_SUMMARY.md`, temporary HTML files

### Scripts Directory
- **Keep**: `deploy.py`, `setup_*.py`, `*neo4j*`, `*moat*`, `backfill_graph_database.py`
- **Remove**: `test_*.py`, `verify_*.py`, `check_*.py`, `fix_*.py`

### Test Directory
- **Keep**: All property tests, essential unit tests, integration tests
- **Review**: Remove tests for deprecated functionality
- **Consolidate**: Merge related test cases where appropriate

### Source Directory
- **Keep**: All modules (required by main application)
- **Clean**: Remove `__pycache__` directories
- **Organize**: Ensure consistent module structure

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

**Property 1: Dependency Preservation**
*For any* module imported by app_consolidated.py, that module file must still exist after cleanup
**Validates: Requirements 1.4, 2.1**

**Property 2: Test Coverage Maintenance**
*For any* core module in the source directory, at least one test file must exist that covers its functionality
**Validates: Requirements 2.2, 3.2**

**Property 3: Documentation Content Preservation**
*For any* architectural insight or setup instruction from temporary documents, that content must appear in the consolidated architecture document or README
**Validates: Requirements 2.3, 4.1, 4.3**

**Property 4: Essential Configuration Preservation**
*For any* configuration file required for deployment (pyproject.toml, .env.example, supabase migrations), that file must remain after cleanup
**Validates: Requirements 2.5, 4.4**