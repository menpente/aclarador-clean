from typing import Dict, List, Any
from .base_agent import BaseAgent

class SEOAgent(BaseAgent):
    """Agent for SEO optimization while maintaining clarity"""
    
    def __init__(self):
        super().__init__("SEO")
    
    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze SEO aspects while preserving clarity"""
        return {
            "seo_recommendations": self._analyze_seo_elements(text),
            "clarity_balance": self._assess_clarity_balance(text),
            "agent": self.name
        }
    
    def get_capabilities(self) -> List[str]:
        return [
            "keyword_optimization",
            "meta_description_review",
            "clarity_seo_balance",
            "search_intent_preservation"
        ]
    
    def _analyze_seo_elements(self, text: str) -> List[Dict[str, str]]:
        """Analyze SEO elements"""
        recommendations = []
        
        # Check for title-like content (first sentence)
        first_sentence = text.split('.')[0] if '.' in text else text
        if len(first_sentence.split()) > 10:
            recommendations.append({
                "type": "seo",
                "element": "title",
                "recommendation": "Considerar acortar el título para SEO (máximo 60 caracteres)",
                "reason": "Los títulos largos pueden cortarse en resultados de búsqueda",
                "pdf_reference": "Escritura en internet - Optimización para buscadores"
            })
        
        # Check for keyword repetition
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Only consider longer words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        repeated_words = [word for word, freq in word_freq.items() if freq > 3]
        if repeated_words:
            recommendations.append({
                "type": "seo",
                "element": "keywords",
                "recommendation": f"Palabras repetidas frecuentemente: {', '.join(repeated_words[:3])}",
                "reason": "Equilibrar densidad de palabras clave con variedad de vocabulario",
                "pdf_reference": "Balance SEO-claridad"
            })
        
        return recommendations
    
    def _assess_clarity_balance(self, text: str) -> Dict[str, float]:
        """Assess balance between SEO and clarity"""
        # Simple metrics for demonstration
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        return {
            "seo_score": 0.7,  # Placeholder
            "clarity_score": max(0, 1 - (avg_length - 15) / 30),  # Decreases with length
            "balance_score": 0.65  # Placeholder
        }