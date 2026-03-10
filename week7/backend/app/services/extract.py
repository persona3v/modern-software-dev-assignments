"""
Action Item Extraction Service

Enhanced pattern recognition for extracting action items from text.
Supports multiple patterns, priority detection, and categorization.
"""

import re
from typing import Optional


# Priority patterns
HIGH_PRIORITY = re.compile(r"\b(urgent|critical|asap|immediately|important|high)\b", re.IGNORECASE)
LOW_PRIORITY = re.compile(r"\b(low|minor|eventually|someday)\b", re.IGNORECASE)

# Category patterns
CATEGORY_PATTERNS = {
    "bug": re.compile(r"\b(bug|fix|broken|error|issue|null)\b", re.IGNORECASE),
    "feature": re.compile(r"\b(feature|add|implement|new|create)\b", re.IGNORECASE),
    "refactor": re.compile(r"\b(refactor|cleanup|optimize|improve)\b", re.IGNORECASE),
    "security": re.compile(r"\b(security|vulnerable|secure|auth|password)\b", re.IGNORECASE),
    "performance": re.compile(r"\b(performance|slow|bottleneck|optimize)\b", re.IGNORECASE),
    "docs": re.compile(r"\b(doc|documentation|readme)\b", re.IGNORECASE),
    "test": re.compile(r"\b(test|spec|coverage)\b", re.IGNORECASE),
    "question": re.compile(r"\b(question|how|why|what)\b", re.IGNORECASE),
}

# Action item prefixes
ACTION_PREFIXES = [
    "todo:", "action:", "task:", "fixme:", "hack:", "note:", "question:",
    "urgent:", "important:", "high:", "medium:", "low:", "bug:", "fix:",
    "feature:", "security:", "performance:", "test:", "refactor:", "docs:",
]


def _detect_priority(line: str) -> str:
    """Detect priority from the line."""
    line_lower = line.lower()
    # Remove prefix for detection
    for prefix in ACTION_PREFIXES:
        if line_lower.startswith(prefix):
            line_lower = line_lower[len(prefix):].strip()
            break
    if HIGH_PRIORITY.search(line_lower):
        return "high"
    elif LOW_PRIORITY.search(line_lower):
        return "low"
    return "medium"


def _detect_category(line: str) -> str:
    """Detect category from the line."""
    line_lower = line.lower()
    # Remove prefix for detection
    for prefix in ACTION_PREFIXES:
        if line_lower.startswith(prefix):
            line_lower = line_lower[len(prefix):].strip()
            break
    for category, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(line_lower):
            return category
    return "todo"


def _is_action_item(line: str) -> bool:
    """Check if line is an action item."""
    line_lower = line.strip().lower()
    
    # Check prefixes
    for prefix in ACTION_PREFIXES:
        if line_lower.startswith(prefix):
            return True
    
    # Check suffixes
    if line.strip().endswith("!"):
        return True
    
    return False


def extract_action_items(text: str) -> list[str]:
    """
    Extract action items from text (simple interface).
    
    Returns a list of action item strings.
    """
    results = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = line.lstrip("- ").strip()
        if _is_action_item(line):
            results.append(line)
    return results


def extract_action_items_advanced(text: str) -> list[dict]:
    """
    Extract action items with priority and category detection.
    
    Returns a list of dictionaries with metadata.
    """
    results = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        normalized = line.lstrip("- ").strip()
        if _is_action_item(normalized):
            # Extract the content after the prefix
            content = normalized
            for prefix in ACTION_PREFIXES:
                if normalized.lower().startswith(prefix):
                    content = normalized[len(prefix):].strip()
                    break
            
            results.append({
                "text": normalized,
                "content": content,
                "priority": _detect_priority(normalized),
                "category": _detect_category(normalized),
            })
    return results


def extract_action_items_with_context(text: str, context_lines: int = 2) -> list[dict]:
    """
    Extract action items with surrounding context.
    
    Returns a list of dictionaries with context.
    """
    lines = text.splitlines()
    results = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        normalized = line.lstrip("- ").strip()
        if _is_action_item(normalized):
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            results.append({
                "item": normalized,
                "priority": _detect_priority(normalized),
                "category": _detect_category(normalized),
                "context": lines[start:end],
            })
    return results
