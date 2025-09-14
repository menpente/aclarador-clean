import re
from typing import Dict, List, Any
from .base_agent import BaseAgent

class GrammarAgent(BaseAgent):
    """Agent for grammar and syntax corrections"""
    
    def __init__(self):
        super().__init__("Grammar")
    
    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze grammar and suggest corrections"""
        corrections = self._find_grammar_issues(text)
        
        # Add knowledge base guidelines if available
        kb_guidelines = []
        if context and context.get("knowledge_retrieval"):
            try:
                kb_guidelines = context["knowledge_retrieval"].get_relevant_guidelines(
                    text=text,
                    agent_type="grammar",
                    issues=["grammar_error"],
                    n_results=2
                )
            except Exception as e:
                print(f"Error retrieving grammar guidelines: {e}")
        
        return {
            "corrections": corrections,
            "confidence": 0.85,
            "agent": self.name,
            "kb_guidelines": kb_guidelines
        }
    
    def get_capabilities(self) -> List[str]:
        return [
            "grammar_correction",
            "punctuation_fixing",
            "sentence_structure",
            "agreement_checking"
        ]
    
    def _find_grammar_issues(self, text: str) -> List[Dict[str, str]]:
        """Find grammar issues (placeholder implementation)"""
        corrections = []
        
        # Basic checks for demonstration
        if "que que" in text.lower():
            corrections.append({
                "type": "grammar",
                "original": "que que",
                "corrected": "que",
                "reason": "Repetición innecesaria de 'que'",
                "pdf_reference": "Sección de conectores"
            })
        
        # Check for missing accents with context checking
        
        # Only suggest "él" when "el" is likely a pronoun (before verbs)
        if re.search(r'\bel\s+(es|está|tiene|hace|dice|va|fue|será|puede|debe)\b', text.lower()):
            corrections.append({
                "type": "grammar",
                "original": "el",
                "corrected": "él",
                "reason": "Posible pronombre personal que requiere acento",
                "pdf_reference": "Sección de acentuación"
            })
        
        # For other accent cases, be more conservative with context
        accent_context_pairs = [
            ("mas", "más", r'\bmas\s+(que|de|bien|mal|o|menos)\b'),  # "más que", "más de", etc.
            ("si", "sí", r'\bsi\s+(quiere|puede|es|está)\b'),  # "sí quiere", "sí puede", etc.
            ("tu", "tú", r'\btu\s+(eres|estás|tienes|haces|dices|vas)\b')  # "tú eres", "tú estás", etc.
        ]
        
        for original, corrected, context_pattern in accent_context_pairs:
            if re.search(context_pattern, text.lower()):
                corrections.append({
                    "type": "grammar",
                    "original": original,
                    "corrected": corrected,
                    "reason": f"Posible falta de acento en '{original}' (contexto: pronombre/adverbio)",
                    "pdf_reference": "Sección de acentuación"
                })
        
        return corrections