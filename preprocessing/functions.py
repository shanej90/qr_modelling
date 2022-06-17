#function to tidy up column names########################################
def tidy_columns(c):
    """Tidies columns headings into 'machine-readable' format
    Args:
        c (str): Column heading to tidy.

    Returns:
        str: Tidied column heading.
    """    
    stripped = c.strip()
    lower = stripped.lower()
    nospace = lower.replace(" ", "_")
    nopct = nospace.replace("%", "pct")
    nochr = nopct.translate ({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=+"})
    return nochr