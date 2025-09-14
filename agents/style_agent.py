from typing import Dict, List, Any
from .base_agent import BaseAgent

class StyleAgent(BaseAgent):
    """Agent for style improvements and coherence"""
    
    def __init__(self):
        super().__init__("Style")
    
    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze style and suggest improvements"""
        improvements = self._find_style_issues(text)
        
        # Add knowledge base guidelines if available
        kb_guidelines = []
        if context and context.get("knowledge_retrieval"):
            try:
                issues = ["long_sentence"] if any(len(s.split()) > 30 for s in text.split('.')) else []
                if any(indicator in text.lower() for indicator in ["fue", "fueron", "es", "son"]):
                    issues.append("passive_voice")
                
                kb_guidelines = context["knowledge_retrieval"].get_relevant_guidelines(
                    text=text,
                    agent_type="style", 
                    issues=issues,
                    n_results=3
                )
            except Exception as e:
                print(f"Error retrieving style guidelines: {e}")
        
        return {
            "improvements": improvements,
            "readability_score": self._calculate_readability(text),
            "agent": self.name,
            "kb_guidelines": kb_guidelines
        }
    
    def get_capabilities(self) -> List[str]:
        return [
            "sentence_simplification",
            "jargon_removal",
            "flow_improvement",
            "readability_enhancement"
        ]
    
    def _find_style_issues(self, text: str) -> List[Dict[str, str]]:
        """Find style issues and suggest improvements"""
        improvements = []
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        for sentence in sentences:
            word_count = len(sentence.split())
            
            # Check sentence length
            if word_count > 30:
                improvements.append({
                    "type": "style",
                    "original": sentence,
                    "corrected": f"[Dividir en oraciones más cortas]",
                    "reason": f"Oración muy larga ({word_count} palabras). Máximo recomendado: 30 palabras.",
                    "pdf_reference": "Principios de lenguaje claro - Una idea por oración"
                })
            
            # Check for passive voice (basic detection)
            passive_indicators = ["fue", "fueron", "es", "son", "está siendo", "han sido"]
            if any(indicator in sentence.lower() for indicator in passive_indicators):
                improvements.append({
                    "type": "style",
                    "original": sentence,
                    "corrected": "[Convertir a voz activa]",
                    "reason": "Posible uso de voz pasiva. Preferir voz activa para mayor claridad.",
                    "pdf_reference": "Estructura clara - Sujeto, verbo, predicado"
                })
        
        return improvements
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate basic readability score"""
        sentences = len([s for s in text.split('.') if s.strip()])
        words = len(text.split())
        
        if sentences == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        
        # Simple readability score (inverse of complexity)
        if avg_sentence_length <= 15:
            return 0.9
        elif avg_sentence_length <= 25:
            return 0.7
        elif avg_sentence_length <= 35:
            return 0.5
        else:
            return 0.3