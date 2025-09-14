from typing import Dict, List, Any
from .base_agent import BaseAgent

class ValidatorAgent(BaseAgent):
    """Agent for final review and quality assurance"""
    
    def __init__(self):
        super().__init__("Validator")
    
    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform final validation and quality check"""
        return {
            "validation_results": self._validate_improvements(text, context),
            "quality_score": self._calculate_quality_score(text),
            "compliance_check": self._check_compliance(text),
            "agent": self.name
        }
    
    def get_capabilities(self) -> List[str]:
        return [
            "quality_assurance",
            "compliance_verification", 
            "meaning_preservation",
            "final_review"
        ]
    
    def _validate_improvements(self, text: str, context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Validate that improvements maintain meaning and quality"""
        validations = []
        
        # Check basic text quality
        if not text.strip():
            validations.append({
                "type": "validation",
                "status": "error",
                "message": "Texto vacío después del procesamiento",
                "recommendation": "Revisar procesamiento de agentes anteriores"
            })
            return validations
        
        # Check sentence structure
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            validations.append({
                "type": "validation",
                "status": "warning", 
                "message": "No se detectaron oraciones completas",
                "recommendation": "Verificar puntuación y estructura"
            })
        
        # Validate against lenguaje claro principles
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        if long_sentences:
            validations.append({
                "type": "validation",
                "status": "warning",
                "message": f"{len(long_sentences)} oraciones exceden 30 palabras",
                "recommendation": "Considerar división en oraciones más cortas",
                "pdf_reference": "Principio de oraciones cortas"
            })
        
        validations.append({
            "type": "validation",
            "status": "success",
            "message": "Texto validado correctamente",
            "recommendation": "Listo para presentar al usuario"
        })
        
        return validations
    
    def _calculate_quality_score(self, text: str) -> float:
        """Calculate overall quality score"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return 0.0
        
        # Calculate average sentence length
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Score based on sentence length (optimal: 15-25 words)
        if 15 <= avg_length <= 25:
            length_score = 1.0
        elif 10 <= avg_length < 15 or 25 < avg_length <= 30:
            length_score = 0.8
        elif avg_length < 10 or avg_length > 30:
            length_score = 0.6
        else:
            length_score = 0.4
        
        # Basic completeness check
        completeness_score = 1.0 if all(len(s.split()) > 3 for s in sentences) else 0.7
        
        return (length_score + completeness_score) / 2
    
    def _check_compliance(self, text: str) -> Dict[str, bool]:
        """Check compliance with lenguaje claro principles"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        return {
            "has_complete_sentences": len(sentences) > 0,
            "appropriate_length": all(len(s.split()) <= 30 for s in sentences),
            "proper_punctuation": text.count('.') > 0 or text.count('!') > 0 or text.count('?') > 0,
            "non_empty": bool(text.strip())
        }