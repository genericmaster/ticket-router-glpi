import re
import html
def clean(content: str)->str:
    """cleans incoming html tags for glpi content parameter so that they are parsable to  the llm"""
    content= re.sub(r'<[^>]+>', '', html.unescape(content))
    return content