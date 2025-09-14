from typing import Dict, List, Any
from .base_agent import BaseAgent

class AnalyzerAgent(BaseAgent):
    """Agent for initial text analysis and classification"""
    
    def __init__(self):
        super().__init__("Analyzer")
    
    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze text and classify for routing to other agents"""
        # Placeholder implementation
        return {
            "text_type": self._classify_text_type(text),
            "issues_detected": self._detect_issues(text),
            "recommended_agents": self._recommend_agents(text),
            "severity_level": self._assess_severity(text)
        }
    
    def get_capabilities(self) -> List[str]:
        return [
            "text_classification",
            "issue_detection", 
            "agent_routing",
            "severity_assessment"
        ]
    
    def _classify_text_type(self, text: str) -> str:
        """Classify text type for appropriate processing"""
        # Simple heuristics for now
        if len(text.split()) < 50:
            return "short"
        elif "SEO" in text or "www." in text:
            return "web"
        else:
            return "document"
    
    def _detect_issues(self, text: str) -> List[str]:
        """Detect clarity issues in text"""
        issues = []
        sentences = text.split('.')
        
        # Check sentence length
        for sentence in sentences:
            if len(sentence.split()) > 30:
                issues.append("long_sentence")
        
        # Check for complex words (placeholder)
        if any(len(word) > 12 for word in text.split()):
            issues.append("complex_vocabulary")
            
        return list(set(issues))
    
    def _recommend_agents(self, text: str) -> List[str]:
        """Recommend which agents should process this text"""
        agents = ["grammar"]  # Always check grammar
        
        issues = self._detect_issues(text)
        if "long_sentence" in issues or "complex_vocabulary" in issues:
            agents.append("style")
        
        if self._classify_text_type(text) == "web":
            agents.append("seo")
            
        agents.append("validator")  # Always validate
        return agents
    
    def _assess_severity(self, text: str) -> str:
        """Assess severity level of issues"""
        issues = self._detect_issues(text)
        if len(issues) > 3:
            return "high"
        elif len(issues) > 1:
            return "medium"
        else:
            return "low"