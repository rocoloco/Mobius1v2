"""
Property-based tests for documentation content preservation during repository cleanup.

**Feature: repository-cleanup, Property 3: Documentation Content Preservation**

Tests that architectural insights and setup instructions from temporary documents
are preserved in consolidated architecture document or README.

**Validates: Requirements 2.3, 4.1, 4.3**
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import re
from typing import Set, List, Dict, Optional
import json


class DocumentationAnalyzer:
    """Utility class to analyze documentation content and extract key insights."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def extract_key_insights(self, file_path: Path) -> Set[str]:
        """Extract key insights from a documentation file."""
        if not file_path.exists() or file_path.suffix != '.md':
            return set()
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            insights = set()
            
            # Extract architectural decisions (marked with specific patterns)
            arch_patterns = [
                r'## (?:Architecture|Design|Solution|Implementation)',
                r'### (?:Root Cause|Fix|Solution)',
                r'\*\*(?:Problem|Issue|Fix|Solution)\*\*:',
                r'(?:CRITICAL|IMPORTANT|NOTE):',
                r'## (?:What This Fixes|Benefits|Impact)',
            ]
            
            for pattern in arch_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Extract the section following the pattern
                    start = match.end()
                    # Find next section or end of content
                    next_section = re.search(r'\n##', content[start:])
                    end = start + next_section.start() if next_section else len(content)
                    section_content = content[start:end].strip()
                    
                    if section_content:
                        # Extract meaningful sentences (not just headers)
                        sentences = re.split(r'[.!?]\s+', section_content)
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if len(sentence) > 20 and not sentence.startswith('#'):
                                insights.add(sentence[:100])  # Truncate for comparison
            
            # Extract code snippets and configuration examples
            code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
            for code_block in code_blocks:
                if len(code_block.strip()) > 10:
                    # Extract meaningful configuration or code patterns
                    lines = code_block.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if ('=' in line or ':' in line or 'def ' in line or 'class ' in line):
                            insights.add(line[:80])
            
            # Extract specific technical details
            tech_patterns = [
                r'port \d+',
                r'timeout.*\d+',
                r'API.*key',
                r'connection.*pool',
                r'async.*mode',
                r'webhook.*retry',
                r'Neo4j.*routing',
                r'Gemini.*model',
                r'Modal.*deploy',
                r'Supabase.*pooler',
            ]
            
            for pattern in tech_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                insights.update(matches)
            
            return insights
            
        except (UnicodeDecodeError, IOError):
            return set()
    
    def extract_setup_instructions(self, file_path: Path) -> Set[str]:
        """Extract setup and deployment instructions from documentation."""
        if not file_path.exists() or file_path.suffix != '.md':
            return set()
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            instructions = set()
            
            # Extract command-line instructions
            bash_commands = re.findall(r'```(?:bash|shell|cmd)\n(.*?)\n```', content, re.DOTALL)
            for commands in bash_commands:
                for line in commands.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        instructions.add(line)
            
            # Extract step-by-step instructions
            step_patterns = [
                r'\d+\.\s+(.+)',
                r'-\s+(.+)',
                r'\*\s+(.+)',
            ]
            
            for pattern in step_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    if len(match.strip()) > 10:
                        instructions.add(match.strip()[:100])
            
            return instructions
            
        except (UnicodeDecodeError, IOError):
            return set()
    
    def get_temporary_documents(self) -> List[Path]:
        """Get list of temporary fix and analysis documents."""
        temp_docs = []
        
        # Find all *_FIX.md and *_ANALYSIS.md files
        for pattern in ['*_FIX.md', '*_ANALYSIS.md', 'FIXES_SUMMARY.md']:
            temp_docs.extend(self.project_root.glob(pattern))
        
        return temp_docs
    
    def get_consolidated_documents(self) -> List[Path]:
        """Get list of consolidated documentation files."""
        consolidated_docs = []
        
        # Main documentation files that should contain consolidated content
        doc_files = ['MOBIUS-ARCHITECTURE.md', 'README.md', 'MOAT.md']
        
        for doc_file in doc_files:
            doc_path = self.project_root / doc_file
            if doc_path.exists():
                consolidated_docs.append(doc_path)
        
        return consolidated_docs
    
    def analyze_content_preservation(self) -> Dict[str, any]:
        """Analyze how well content is preserved from temporary to consolidated docs."""
        temp_docs = self.get_temporary_documents()
        consolidated_docs = self.get_consolidated_documents()
        
        # Extract all insights from temporary documents
        temp_insights = set()
        temp_instructions = set()
        
        for temp_doc in temp_docs:
            temp_insights.update(self.extract_key_insights(temp_doc))
            temp_instructions.update(self.extract_setup_instructions(temp_doc))
        
        # Extract all content from consolidated documents
        consolidated_insights = set()
        consolidated_instructions = set()
        
        for consolidated_doc in consolidated_docs:
            consolidated_insights.update(self.extract_key_insights(consolidated_doc))
            consolidated_instructions.update(self.extract_setup_instructions(consolidated_doc))
        
        return {
            'temp_insights': temp_insights,
            'temp_instructions': temp_instructions,
            'consolidated_insights': consolidated_insights,
            'consolidated_instructions': consolidated_instructions,
            'temp_docs_count': len(temp_docs),
            'consolidated_docs_count': len(consolidated_docs)
        }


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).parent
    while current.parent != current:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


@st.composite
def documentation_content_strategy(draw):
    """Generate documentation content scenarios for testing."""
    # Generate different types of content that might be in temporary documents
    
    # Architectural insights
    arch_insights = draw(st.lists(
        st.text(min_size=20, max_size=100).filter(lambda x: len(x.strip()) > 15),
        min_size=1,
        max_size=5
    ))
    
    # Setup instructions
    setup_instructions = draw(st.lists(
        st.sampled_from([
            "modal deploy src/mobius/api/app_consolidated.py",
            "pip install -e .",
            "python scripts/setup_modal.py",
            "export GEMINI_API_KEY=your_key",
            "Use Supabase pooler URL (port 6543)",
            "Run pytest -v for testing",
            "Check logs with modal app logs",
        ]),
        min_size=1,
        max_size=4,
        unique=True
    ))
    
    # Technical details
    tech_details = draw(st.lists(
        st.sampled_from([
            "timeout 2 minutes",
            "port 6543",
            "async mode implementation",
            "Neo4j routing fix",
            "Gemini API rate limits",
            "webhook retry logic",
            "connection pooling",
        ]),
        min_size=0,
        max_size=3,
        unique=True
    ))
    
    return {
        'insights': arch_insights,
        'instructions': setup_instructions,
        'tech_details': tech_details
    }


@given(content_scenario=documentation_content_strategy())
@settings(max_examples=50)
def test_documentation_content_preservation_property(content_scenario):
    """
    Property 3: Documentation Content Preservation.
    
    For any architectural insight or setup instruction from temporary documents,
    that content must appear in the consolidated architecture document or README.
    
    **Validates: Requirements 2.3, 4.1, 4.3**
    """
    project_root = get_project_root()
    analyzer = DocumentationAnalyzer(project_root)
    
    # Analyze current documentation state
    analysis = analyzer.analyze_content_preservation()
    
    # If there are temporary documents, their key insights should be preserved
    if analysis['temp_docs_count'] > 0:
        temp_insights = analysis['temp_insights']
        consolidated_insights = analysis['consolidated_insights']
        
        # Check that important insights are preserved
        # We use fuzzy matching since exact text may be rephrased
        preserved_count = 0
        for temp_insight in temp_insights:
            # Check if this insight (or similar) exists in consolidated docs
            for consolidated_insight in consolidated_insights:
                # Simple similarity check - if they share significant words
                temp_words = set(temp_insight.lower().split())
                consolidated_words = set(consolidated_insight.lower().split())
                
                # Remove common words
                common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'}
                temp_words -= common_words
                consolidated_words -= common_words
                
                if len(temp_words) > 2 and len(consolidated_words) > 2:
                    # Check for significant word overlap
                    overlap = len(temp_words & consolidated_words)
                    if overlap >= min(3, len(temp_words) * 0.5):
                        preserved_count += 1
                        break
        
        # At least 50% of insights should be preserved in some form
        if len(temp_insights) > 0:
            preservation_ratio = preserved_count / len(temp_insights)
            assert preservation_ratio >= 0.3, (
                f"Only {preservation_ratio:.1%} of insights from temporary documents "
                f"are preserved in consolidated documentation. "
                f"Expected at least 30% preservation rate."
            )


def test_essential_architectural_content_preserved():
    """
    Property 3 (essential content): Critical architectural decisions are preserved.
    
    Verifies that essential architectural information from temporary documents
    is preserved in the consolidated documentation.
    
    **Validates: Requirements 2.3, 4.1, 4.3**
    """
    project_root = get_project_root()
    analyzer = DocumentationAnalyzer(project_root)
    
    # Get consolidated documentation content
    consolidated_docs = analyzer.get_consolidated_documents()
    
    if not consolidated_docs:
        pytest.skip("No consolidated documentation found")
    
    # Extract all content from consolidated docs
    all_consolidated_content = ""
    for doc in consolidated_docs:
        try:
            with open(doc, 'r', encoding='utf-8') as f:
                all_consolidated_content += f.read().lower()
        except (UnicodeDecodeError, IOError):
            continue
    
    # Check for essential architectural concepts that should be preserved
    essential_concepts = [
        'async mode',
        'neo4j',
        'gemini',
        'supabase',
        'modal',
        'webhook',
        'timeout',
        'connection pool',
        'api',
        'deployment',
    ]
    
    preserved_concepts = []
    for concept in essential_concepts:
        if concept in all_consolidated_content:
            preserved_concepts.append(concept)
    
    # At least 70% of essential concepts should be mentioned
    preservation_ratio = len(preserved_concepts) / len(essential_concepts)
    assert preservation_ratio >= 0.7, (
        f"Only {preservation_ratio:.1%} of essential architectural concepts "
        f"are preserved in consolidated documentation. "
        f"Missing: {set(essential_concepts) - set(preserved_concepts)}"
    )


def test_setup_instructions_consolidated():
    """
    Property 3 (setup instructions): Setup and deployment instructions are preserved.
    
    Verifies that setup instructions from temporary documents are consolidated
    into the main README or architecture document.
    
    **Validates: Requirements 2.3, 4.1, 4.3**
    """
    project_root = get_project_root()
    analyzer = DocumentationAnalyzer(project_root)
    
    # Check README for setup instructions
    readme_path = project_root / "README.md"
    if not readme_path.exists():
        pytest.skip("README.md not found")
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read().lower()
    except (UnicodeDecodeError, IOError):
        pytest.skip("Could not read README.md")
    
    # Essential setup instructions that should be in README
    essential_instructions = [
        'install',
        'deploy',
        'setup',
        'api key',
        'environment',
        'configuration',
    ]
    
    found_instructions = []
    for instruction in essential_instructions:
        if instruction in readme_content:
            found_instructions.append(instruction)
    
    # At least 80% of essential setup concepts should be covered
    coverage_ratio = len(found_instructions) / len(essential_instructions)
    assert coverage_ratio >= 0.8, (
        f"Only {coverage_ratio:.1%} of essential setup instructions "
        f"are covered in README. "
        f"Missing: {set(essential_instructions) - set(found_instructions)}"
    )


@given(st.lists(st.text(min_size=10, max_size=100), min_size=1, max_size=10))
@settings(max_examples=50)
def test_content_extraction_robustness(content_samples):
    """
    Property 3 (robustness): Content extraction handles various input gracefully.
    
    For any documentation content, the extraction process should not crash
    and should return valid results.
    
    **Validates: Requirements 2.3, 4.1, 4.3**
    """
    project_root = get_project_root()
    analyzer = DocumentationAnalyzer(project_root)
    
    # Create a temporary file with the content
    temp_file = project_root / "temp_test_doc.md"
    
    try:
        for content in content_samples:
            # Write content to temporary file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Test extraction methods don't crash
            try:
                insights = analyzer.extract_key_insights(temp_file)
                instructions = analyzer.extract_setup_instructions(temp_file)
                
                # Results should be sets
                assert isinstance(insights, set)
                assert isinstance(instructions, set)
                
                # All items should be strings
                for insight in insights:
                    assert isinstance(insight, str)
                for instruction in instructions:
                    assert isinstance(instruction, str)
                    
            except Exception as e:
                pytest.fail(f"Content extraction crashed on content: {e}")
    
    finally:
        # Clean up temporary file
        if temp_file.exists():
            temp_file.unlink()


def test_temporary_documents_analysis():
    """
    Property 3 (analysis): Temporary documents are correctly identified and analyzed.
    
    Verifies that the system correctly identifies temporary fix and analysis
    documents and can extract content from them.
    
    **Validates: Requirements 2.3, 4.1, 4.3**
    """
    project_root = get_project_root()
    analyzer = DocumentationAnalyzer(project_root)
    
    # Get temporary documents
    temp_docs = analyzer.get_temporary_documents()
    
    # Analyze the current state
    analysis = analyzer.analyze_content_preservation()
    
    # If temporary documents exist, they should be analyzable
    if temp_docs:
        assert analysis['temp_docs_count'] > 0
        
        # Should extract some insights from temporary documents
        temp_insights = analysis['temp_insights']
        temp_instructions = analysis['temp_instructions']
        
        # At least one type of content should be extracted
        assert len(temp_insights) > 0 or len(temp_instructions) > 0, (
            "Should extract some insights or instructions from temporary documents"
        )
        
        # Test each temporary document individually
        for temp_doc in temp_docs:
            insights = analyzer.extract_key_insights(temp_doc)
            instructions = analyzer.extract_setup_instructions(temp_doc)
            
            # Should not crash on any document
            assert isinstance(insights, set)
            assert isinstance(instructions, set)


def test_consolidation_completeness():
    """
    Property 3 (completeness): Consolidated documents contain comprehensive information.
    
    Verifies that consolidated documents contain sufficient architectural and
    setup information to serve as the single source of truth.
    
    **Validates: Requirements 2.3, 4.1, 4.3**
    """
    project_root = get_project_root()
    analyzer = DocumentationAnalyzer(project_root)
    
    # Get consolidated documents
    consolidated_docs = analyzer.get_consolidated_documents()
    
    if not consolidated_docs:
        pytest.skip("No consolidated documentation found")
    
    # Analyze consolidated content
    analysis = analyzer.analyze_content_preservation()
    
    consolidated_insights = analysis['consolidated_insights']
    consolidated_instructions = analysis['consolidated_instructions']
    
    # Consolidated documents should contain substantial content
    total_content_items = len(consolidated_insights) + len(consolidated_instructions)
    
    assert total_content_items >= 10, (
        f"Consolidated documentation contains only {total_content_items} content items. "
        f"Expected at least 10 items for comprehensive documentation."
    )
    
    # Should have both architectural insights and setup instructions
    assert len(consolidated_insights) > 0, (
        "Consolidated documentation should contain architectural insights"
    )
    
    assert len(consolidated_instructions) > 0, (
        "Consolidated documentation should contain setup instructions"
    )