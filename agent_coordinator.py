from typing import Dict, List, Any, Optional
from agents.analyzer_agent import AnalyzerAgent
from agents.grammar_agent import GrammarAgent
from agents.style_agent import StyleAgent
from agents.seo_agent import SEOAgent
from agents.validator_agent import ValidatorAgent

class AgentCoordinator:
    """Coordinates multiple agents for comprehensive text analysis"""
    
    def __init__(self, use_knowledge_base: bool = False):
        # Initialize agents
        self.analyzer = AnalyzerAgent()
        self.grammar = GrammarAgent()
        self.style = StyleAgent()
        self.seo = SEOAgent()
        self.validator = ValidatorAgent()
        
        self.use_knowledge_base = use_knowledge_base
        self.knowledge_retrieval = None
        
        # Try to initialize knowledge base if available
        if use_knowledge_base:
            try:
                # Try real knowledge base first
                from knowledge.vector_store import VectorStore
                from knowledge.retrieval import KnowledgeRetrieval
                
                vector_store = VectorStore()
                if vector_store.get_collection_info()['count'] > 0:
                    self.knowledge_retrieval = KnowledgeRetrieval(vector_store)
                    print("Real knowledge base loaded successfully")
                else:
                    raise Exception("Real knowledge base empty")
                    
            except Exception as e:
                print(f"Real knowledge base not available: {e}")
                # Fallback to mock knowledge base
                try:
                    from knowledge_mock import MockKnowledgeRetrieval
                    self.knowledge_retrieval = MockKnowledgeRetrieval()
                    print("Mock knowledge base loaded successfully")
                except Exception as e2:
                    print(f"Could not load mock knowledge base: {e2}")
                    self.use_knowledge_base = False
    
    def process_text(self, text: str, selected_agents: List[str] = None) -> Dict[str, Any]:
        """Process text through selected agents"""
        
        # Step 1: Analyze text
        analysis = self.analyzer.analyze(text)
        
        # Step 2: Determine which agents to use
        if selected_agents is None:
            agents_to_use = analysis.get("recommended_agents", ["grammar", "style", "validator"])
        else:
            agents_to_use = selected_agents
        
        results = {
            "original_text": text,
            "analysis": analysis,
            "agent_results": {},
            "final_validation": {},
            "corrected_text": text,
            "improvements": [],
            "knowledge_guidelines": []
        }
        
        # Step 3: Process with each agent
        current_text = text
        
        # Create context for agents
        agent_context = {
            "knowledge_retrieval": self.knowledge_retrieval if self.use_knowledge_base else None,
            "text_analysis": analysis
        }
        
        if "grammar" in agents_to_use:
            grammar_result = self.grammar.analyze(current_text, context=agent_context)
            results["agent_results"]["grammar"] = grammar_result
            
            # Apply basic corrections for demonstration
            for correction in grammar_result.get("corrections", []):
                if correction["original"] in current_text:
                    current_text = current_text.replace(
                        correction["original"], 
                        correction["corrected"]
                    )
                    results["improvements"].append({
                        "agent": "grammar",
                        "type": correction["type"],
                        "change": f"{correction['original']} → {correction['corrected']}",
                        "reason": correction["reason"],
                        "reference": correction.get("pdf_reference", "")
                    })
        
        if "style" in agents_to_use:
            style_result = self.style.analyze(current_text, context=agent_context)
            results["agent_results"]["style"] = style_result
            
            # Add style recommendations (not automatic corrections)
            for improvement in style_result.get("improvements", []):
                results["improvements"].append({
                    "agent": "style", 
                    "type": improvement["type"],
                    "suggestion": improvement["corrected"],
                    "reason": improvement["reason"],
                    "reference": improvement.get("pdf_reference", "")
                })
        
        if "seo" in agents_to_use and analysis.get("text_type") == "web":
            seo_result = self.seo.analyze(current_text)
            results["agent_results"]["seo"] = seo_result
            
            # Add SEO recommendations
            for rec in seo_result.get("seo_recommendations", []):
                results["improvements"].append({
                    "agent": "seo",
                    "type": rec["type"],
                    "recommendation": rec["recommendation"],
                    "reason": rec["reason"],
                    "reference": rec.get("pdf_reference", "")
                })
        
        # Step 4: Collect all knowledge base guidelines from agents
        all_kb_guidelines = []
        for agent_name, agent_result in results["agent_results"].items():
            kb_guidelines = agent_result.get("kb_guidelines", [])
            for guideline in kb_guidelines:
                guideline["source_agent"] = agent_name
                all_kb_guidelines.append(guideline)
        
        # Remove duplicates and limit results
        seen_content = set()
        unique_guidelines = []
        for guideline in all_kb_guidelines:
            content_key = guideline["content"][:100]  # Use first 100 chars as key
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_guidelines.append(guideline)
        
        results["knowledge_guidelines"] = unique_guidelines[:5]  # Limit to 5 guidelines
        
        # Step 5: Final validation
        if "validator" in agents_to_use:
            validation = self.validator.analyze(current_text, context=results)
            results["final_validation"] = validation
        
        results["corrected_text"] = current_text
        
        return results
    
    def get_available_agents(self) -> Dict[str, str]:
        """Get list of available agents and their descriptions"""
        return {
            "analyzer": "Analyzes text and classifies issues",
            "grammar": "Checks and corrects grammar errors",
            "style": "Suggests style improvements for clarity",
            "seo": "Optimizes for search engines while maintaining clarity",
            "validator": "Performs final quality validation"
        }
    
    def format_results_for_display(self, results: Dict[str, Any]) -> str:
        """Format results for Streamlit display"""
        output = []
        
        # Corrected text
        output.append("## TEXTO CORREGIDO")
        output.append(results["corrected_text"])
        output.append("")
        
        # Analysis summary
        analysis = results.get("analysis", {})
        output.append("## ANÁLISIS")
        output.append(f"**Tipo de texto**: {analysis.get('text_type', 'No determinado')}")
        output.append(f"**Nivel de severidad**: {analysis.get('severity_level', 'No determinado')}")
        if analysis.get("issues_detected"):
            output.append(f"**Problemas detectados**: {', '.join(analysis['issues_detected'])}")
        output.append("")
        
        # Improvements
        if results.get("improvements"):
            output.append("## MEJORAS APLICADAS")
            for i, improvement in enumerate(results["improvements"], 1):
                output.append(f"**{i}. {improvement['agent'].upper()}**")
                if "change" in improvement:
                    output.append(f"   - Cambio: {improvement['change']}")
                if "suggestion" in improvement:
                    output.append(f"   - Sugerencia: {improvement['suggestion']}")
                if "recommendation" in improvement:
                    output.append(f"   - Recomendación: {improvement['recommendation']}")
                output.append(f"   - Razón: {improvement['reason']}")
                if improvement.get("reference"):
                    output.append(f"   - Referencia: {improvement['reference']}")
                output.append("")
        
        # Knowledge base guidelines
        if results.get("knowledge_guidelines"):
            output.append("## DIRECTRICES DEL MANUAL")
            for i, guideline in enumerate(results["knowledge_guidelines"], 1):
                output.append(f"**{i}. Página {guideline['page']}** (Relevancia: {guideline['relevance']:.1%})")
                output.append(f"   {guideline['content'][:200]}...")
                output.append("")
        
        # Quality metrics
        if results.get("final_validation"):
            validation = results["final_validation"]
            if "quality_score" in validation:
                quality_score = validation["quality_score"]
                output.append(f"## PUNTUACIÓN DE CALIDAD: {quality_score:.1%}")
        
        return "\n".join(output)