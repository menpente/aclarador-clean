import streamlit as st
from PIL import Image
from groq import Groq
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(__file__))

# LangSmith tracing setup (simple)
try:
    from langsmith import traceable
    # Set environment variables for LangSmith
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "aclarador"
    LANGSMITH_ENABLED = True
except ImportError:
    # Fallback decorator if LangSmith not available
    def traceable(name=None):
        def decorator(func):
            return func
        return decorator
    LANGSMITH_ENABLED = False

from agent_coordinator import AgentCoordinator

# Initialize the Groq client (fallback option)
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except:
    client = None

# Function to process the input text with original method (fallback)
@traceable(name="process_text_original")
def process_text_original(input_text):
    """Original processing method using Groq directly"""
    if not client:
        return "Error: GROQ_API_KEY no configurado"
        
    prompt = '''
    Eres un experto en lenguaje claro. Las pautas básicas para lenguaje claro son:
    - Expresar una idea por oración.
    - Utilizar oraciones de treinta palabras o menos.
    - Evitar la jerga.
    - Seguir el orden sujeto, verbo y predicado.
    - Utilizar una estructura lógica, organizando la información de manera clara y coherente.
    Evalúa la calidad del lenguaje de este texto y sugiere las correcciones oportunas. 
    Muestra siempre primero el texto corregido y a continuación las explicaciones, utilizando el siguiente lenguaje de marcado:


###TEXTO CORREGIDO###



###EXPLICACIÓN###


"
    '''
    input_prompt = prompt + input_text

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": input_prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error procesando con Groq: {e}"

# Initialize agent coordinator
@st.cache_resource
@traceable(name="initialize_coordinator")
def initialize_coordinator():
    """Initialize the agent coordinator (cached for performance)"""
    try:
        # Try to initialize with knowledge base
        coordinator = AgentCoordinator(use_knowledge_base=True)
        return coordinator, True
    except Exception as e:
        st.warning(f"No se pudo cargar la base de conocimientos: {e}")
        try:
            # Fallback to basic coordinator
            coordinator = AgentCoordinator(use_knowledge_base=False)
            return coordinator, False
        except Exception as e2:
            st.error(f"Error inicializando coordinador: {e2}")
            return None, False

# Main app
st.set_page_config(
    page_title="Aclarador - Lenguaje Claro",
    page_icon="📝",
    layout="wide"
)

st.write("# 📝 Aclarador - Lenguaje Claro")
st.write("*Sistema multiagente para mejorar la claridad de textos en español*")

# Initialize coordinator
coordinator, has_knowledge_base = initialize_coordinator()

# Sidebar for configuration
st.sidebar.write("## ⚙️ Configuración")

# LangSmith status
if LANGSMITH_ENABLED:
    st.sidebar.success("🔍 LangSmith Tracing: Activo")
else:
    st.sidebar.info("🔍 LangSmith: No disponible")

# Processing method selection
processing_method = st.sidebar.radio(
    "Método de procesamiento:",
    ["Sistema multiagente", "Groq original"],
    index=0 if coordinator else 1
)

# Agent selection (only for multiagent system)
if processing_method == "Sistema multiagente" and coordinator:
    st.sidebar.write("### Agentes a utilizar:")
    
    available_agents = coordinator.get_available_agents()
    selected_agents = []
    
    for agent_name, description in available_agents.items():
        if agent_name not in ["analyzer", "rewriter"]:  # Analyzer and rewriter always run
            if st.sidebar.checkbox(
                f"**{agent_name.title()}**",
                value=agent_name in ["grammar", "style", "validator"],
                help=description
            ):
                selected_agents.append(agent_name)
    
    # Knowledge base status
    if has_knowledge_base:
        st.sidebar.success("✅ Base de conocimientos cargada")
    else:
        st.sidebar.warning("⚠️ Base de conocimientos no disponible")
        st.sidebar.info("Ejecuta `python setup_knowledge_base.py` para cargarla")

# Main input area
col1, col2 = st.columns([3, 1])

with col1:
    st.write("## 📝 Introduce tu texto")
    
    # Create a text input widget with session state
    if "user_input" not in st.session_state:
        st.session_state["user_input"] = ""

    user_input = st.text_area(
        'Pega tu texto aquí:',
        value=st.session_state["user_input"],
        height=150,
        placeholder="Escribe o pega el texto que quieres mejorar..."
    )

with col2:
    st.write("## 🎯 Acción")
    process_button = st.button(
        "🔄 Procesar texto",
        type="primary",
        disabled=not user_input.strip()
    )
    
    if st.button("🗑️ Limpiar"):
        st.session_state["user_input"] = ""
        st.rerun()

# Process text when button is clicked
if process_button and user_input.strip():
    with st.spinner('Procesando texto...'):
        
        if processing_method == "Sistema multiagente" and coordinator:
            # Use multiagent system
            try:
                results = coordinator.process_text(
                    user_input, 
                    selected_agents=selected_agents if selected_agents else None
                )
                
                # Display results
                st.write("## 📊 Resultados del análisis")
                
                # Tabs for different views
                tab1, tab2, tab3 = st.tabs(["📋 Resultado", "🔍 Detalles", "📚 Manual"])
                
                with tab1:
                    formatted_output = coordinator.format_results_for_display(results)
                    st.markdown(formatted_output)
                
                with tab2:
                    # Analysis details
                    st.write("### Análisis inicial")
                    analysis = results.get("analysis", {})
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric("Tipo de texto", analysis.get("text_type", "No determinado"))
                    with col_b:
                        st.metric("Severidad", analysis.get("severity_level", "No determinado"))
                    with col_c:
                        issues = analysis.get("issues_detected", [])
                        st.metric("Problemas detectados", len(issues))
                    
                    if issues:
                        st.write("**Problemas identificados:**")
                        for issue in issues:
                            st.write(f"- {issue}")
                    
                    # Agent results
                    st.write("### Resultados por agente")
                    for agent_name, agent_result in results.get("agent_results", {}).items():
                        with st.expander(f"🤖 {agent_name.title()}"):
                            st.json(agent_result)
                
                with tab3:
                    # Knowledge base guidelines
                    guidelines = results.get("knowledge_guidelines", [])
                    if guidelines:
                        st.write("### 📚 Directrices del Manual de Lenguaje Claro")
                        for i, guideline in enumerate(guidelines, 1):
                            with st.expander(f"Directriz {i} (Página {guideline['page']}) - Relevancia: {guideline['relevance']:.1%}"):
                                st.write(guideline['content'])
                    else:
                        st.info("No hay directrices específicas disponibles para este texto.")
                        if not has_knowledge_base:
                            st.warning("La base de conocimientos no está cargada. Ejecuta `python setup_knowledge_base.py`")
                
            except Exception as e:
                st.error(f"Error procesando con sistema multiagente: {e}")
                st.write("Intentando con método original...")
                
                # Fallback to original method
                processed_output = process_text_original(user_input)
                st.write('### Resultado (método original):')
                st.write(processed_output)
        
        else:
            # Use original Groq method
            processed_output = process_text_original(user_input)
            st.write("## 📋 Resultado")
            st.write(processed_output)
    
    # Keep input text visible after processing for user reference

# Footer
st.write("---")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.write("**🎯 Principios del lenguaje claro:**")
    st.write("• Una idea por oración")
    st.write("• Máximo 30 palabras por oración")
    st.write("• Evitar jerga técnica")

with col_f2:
    st.write("**🤖 Agentes disponibles:**")
    if coordinator:
        agents = coordinator.get_available_agents()
        for name, desc in list(agents.items())[:3]:
            st.write(f"• **{name.title()}**: {desc}")
    else:
        st.write("• Sistema multiagente no disponible")

with col_f3:
    st.write("**📊 Estado del sistema:**")
    st.write(f"• Coordinador: {'✅ Activo' if coordinator else '❌ No disponible'}")
    st.write(f"• Base de conocimientos: {'✅ Cargada' if has_knowledge_base else '⚠️ No disponible'}")
    st.write(f"• Groq API: {'✅ Configurado' if client else '❌ No configurado'}")