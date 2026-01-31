"""Utility functions for text manipulation."""


def split_by_postfix(text: str, postfixes: list[str]) -> tuple[str, str]:
    """Split text by matching postfix.
    
    Args:
        text: The string to check for postfixes
        postfixes: List of postfixes to check for
        
    Returns:
        Tuple of (text without postfix, matched postfix) or (text, '') if no match
    """
    for postfix in postfixes:
        if text.endswith(postfix):
            return text[:-len(postfix)].strip(), postfix
    return text, ''
