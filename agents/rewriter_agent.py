import os
from typing import Dict, List, Any
from groq import Groq
from .base_agent import BaseAgent

class RewriterAgent(BaseAgent):
    """Agent for comprehensive text rewriting using LLM"""

    def __init__(self):
        super().__init__("Rewriter")
        # Initialize Groq client
        try:
            self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        except:
            self.client = None

    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Rewrite text for clarity using LLM"""
        if not self.client:
            return {
                "rewritten_text": text,
                "improvements": [],
                "error": "GROQ_API_KEY no configurado",
                "agent": self.name
            }

        # Get analysis context
        analysis = context.get("text_analysis", {}) if context else {}
        issues = analysis.get("issues_detected", [])

        # Build prompt based on detected issues
        prompt = self._build_rewrite_prompt(text, issues)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3
            )

            response = chat_completion.choices[0].message.content
            rewritten_text = self._extract_rewritten_text(response)
            improvements = self._identify_improvements(text, rewritten_text)

            return {
                "rewritten_text": rewritten_text,
                "improvements": improvements,
                "full_response": response,
                "confidence": 0.9,
                "agent": self.name
            }

        except Exception as e:
            return {
                "rewritten_text": text,
                "improvements": [],
                "error": f"Error procesando con Groq: {e}",
                "agent": self.name
            }

    def get_capabilities(self) -> List[str]:
        return [
            "comprehensive_rewriting",
            "sentence_restructuring",
            "clarity_enhancement",
            "jargon_simplification"
        ]

    def _build_rewrite_prompt(self, text: str, issues: List[str]) -> str:
        """Build rewrite prompt based on detected issues"""
        base_prompt = """Eres un experto en lenguaje claro. Tu tarea es reescribir el siguiente texto aplicando los principios de lenguaje claro:

- Expresar una idea por oración
- Utilizar oraciones de treinta palabras o menos
- Evitar la jerga y tecnicismos
- Seguir el orden sujeto, verbo y predicado
- Utilizar una estructura lógica y coherente
- Usar voz activa cuando sea posible
- Elegir palabras simples y precisas

"""

        # Add specific instructions based on detected issues
        if "long_sentences" in issues:
            base_prompt += "- IMPORTANTE: Dividir oraciones largas en oraciones más cortas\n"
        if "passive_voice" in issues:
            base_prompt += "- IMPORTANTE: Convertir voz pasiva a voz activa cuando sea apropiado\n"
        if "jargon" in issues:
            base_prompt += "- IMPORTANTE: Simplificar términos técnicos y jerga\n"

        base_prompt += f"""
Reescribe ÚNICAMENTE el texto mejorado, sin explicaciones adicionales.

TEXTO A REESCRIBIR:
{text}

TEXTO REESCRITO:"""

        return base_prompt

    def _extract_rewritten_text(self, response: str) -> str:
        """Extract just the rewritten text from the response"""
        # Try to find the rewritten text after common markers
        markers = ["TEXTO REESCRITO:", "texto reescrito:", "REESCRITO:", "RESULTADO:"]

        for marker in markers:
            if marker in response:
                parts = response.split(marker, 1)
                if len(parts) > 1:
                    return parts[1].strip()

        # If no marker found, assume the entire response is the rewritten text
        # Remove common prefixes
        lines = response.strip().split('\n')
        clean_lines = []

        for line in lines:
            line = line.strip()
            # Skip empty lines and common headers
            if line and not any(skip in line.lower() for skip in [
                "texto reescrito", "resultado", "versión mejorada", "aquí está"
            ]):
                clean_lines.append(line)

        return '\n'.join(clean_lines).strip()

    def _identify_improvements(self, original: str, rewritten: str) -> List[Dict[str, str]]:
        """Identify key improvements made during rewriting"""
        improvements = []

        # Count sentences
        original_sentences = len([s for s in original.split('.') if s.strip()])
        rewritten_sentences = len([s for s in rewritten.split('.') if s.strip()])

        if rewritten_sentences > original_sentences:
            improvements.append({
                "type": "structure",
                "description": f"Dividió el texto en más oraciones ({original_sentences} → {rewritten_sentences})",
                "reason": "Mejora la claridad al expresar una idea por oración"
            })

        # Check average sentence length
        original_words = len(original.split())
        rewritten_words = len(rewritten.split())

        if original_sentences > 0 and rewritten_sentences > 0:
            orig_avg = original_words / original_sentences
            new_avg = rewritten_words / rewritten_sentences

            if orig_avg > 30 and new_avg <= 30:
                improvements.append({
                    "type": "sentence_length",
                    "description": f"Redujo la longitud promedio de oraciones ({orig_avg:.1f} → {new_avg:.1f} palabras)",
                    "reason": "Cumple con el límite recomendado de 30 palabras por oración"
                })

        # Check for passive to active voice conversion (basic heuristic)
        passive_words = ["fue", "fueron", "es", "son", "está siendo", "han sido"]
        original_passive = sum(1 for word in passive_words if word in original.lower())
        rewritten_passive = sum(1 for word in passive_words if word in rewritten.lower())

        if original_passive > rewritten_passive:
            improvements.append({
                "type": "voice",
                "description": "Convirtió construcciones pasivas a voz activa",
                "reason": "La voz activa es más directa y clara"
            })

        return improvements