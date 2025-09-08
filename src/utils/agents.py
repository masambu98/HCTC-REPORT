"""
Agent utilities: initials extraction and display formatting
Signature: 8598
"""

import re
from typing import Optional, Tuple


INITIALS_PATTERN_START = re.compile(r"^\s*\^([A-Za-z]{2,5})\b[:\-\s]*", re.UNICODE)
INITIALS_PATTERN_END = re.compile(r"[:\-\s]*\^([A-Za-z]{2,5})\s*$", re.UNICODE)


def extract_initials_and_strip(content: str) -> Tuple[str, Optional[str]]:
    """Extract leading or trailing caret-based initials (e.g., ^BM) and strip from content.

    Supports formats like:
    - "^BM Hello there"
    - "Hello there ^BM"
    - "^BM: Hello there" or "^BM - Hello there"

    Returns a tuple of (clean_content, initials or None).
    """
    if not isinstance(content, str) or not content:
        return content or "", None

    text = content.strip()

    match = INITIALS_PATTERN_START.match(text)
    if match:
        initials = match.group(1).upper()
        cleaned = INITIALS_PATTERN_START.sub("", text, count=1).strip()
        return cleaned, initials

    match = INITIALS_PATTERN_END.search(text)
    if match:
        initials = match.group(1).upper()
        cleaned = INITIALS_PATTERN_END.sub("", text, count=1).strip()
        return cleaned, initials

    return text, None


def format_agent_display(agent_name: str, initials: Optional[str]) -> str:
    """Format agent display as "BM AgentName" when initials exist, else agent name only."""
    agent_name = (agent_name or "").strip()
    if initials:
        return f"{initials} {agent_name}" if agent_name else initials
    return agent_name

