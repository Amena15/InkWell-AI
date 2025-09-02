import language_tool_python
from typing import List, Dict, Any

class GrammarService:
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('en-US')
    
    def check_grammar(self, text: str) -> List[Dict[str, Any]]:
        """
        Check grammar and style issues in the given text.
        
        Args:
            text: The text to check
            
        Returns:
            List of grammar/style issues with suggestions
        """
        if not text:
            return []
            
        matches = self.tool.check(text)
        
        issues = []
        for match in matches:
            issue = {
                'message': match.message,
                'context': match.context,
                'offset': match.offset,
                'length': match.errorLength,
                'replacements': match.replacements[:5],  # Limit to top 5 suggestions
                'rule_id': match.ruleId,
                'category': match.category,
                'severity': self._get_severity(match.ruleIssueType)
            }
            issues.append(issue)
            
        return issues
    
    def _get_severity(self, issue_type: str) -> str:
        """Map language-tool issue types to our severity levels"""
        if issue_type in ['misspelling', 'grammar']:
            return 'error'
        elif issue_type in ['typographical', 'style']:
            return 'warning'
        return 'info'
