import streamlit as st
from PIL import Image
from groq import Groq
import os

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

# Initialize the Groq client
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except:
    client = None

# Load system prompt
def load_system_prompt():
    """Load the comprehensive system prompt from markdown file"""
    try:
        with open('system_prompt.md', 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract the prompt from the markdown code block
            start_marker = "```\n"
            end_marker = "\n```"
            start_idx = content.find(start_marker)
            if start_idx != -1:
                start_idx += len(start_marker)
                end_idx = content.find(end_marker, start_idx)
                if end_idx != -1:
                    return content[start_idx:end_idx].strip()
        return None
    except Exception as e:
        print(f"Error loading system prompt: {e}")
        return None

# Function to process the input text (with conditional tracing)
def process_text(input_text, enable_tracing=True):
    """Process text using comprehensive system prompt with optional tracing"""

    # Apply tracing decorator conditionally
    if enable_tracing and LANGSMITH_ENABLED:
        @traceable(name="process_text")
        def _process_with_tracing(text):
            return _process_text_core(text)
        return _process_with_tracing(input_text)
    else:
        return _process_text_core(input_text)

def _process_text_core(input_text):
    """Core text processing logic"""
    if not client:
        return "Error: GROQ_API_KEY no configurado"

    # Load enhanced system prompt
    system_prompt = load_system_prompt()

    if not system_prompt:
        # Fallback to basic prompt
        system_prompt = '''
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
        '''

    # Combine system prompt with user input
    full_prompt = f"{system_prompt}\n\n{input_text}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error procesando con Groq: {e}"

# Main app
st.set_page_config(
    page_title="Aclarador - Lenguaje Claro",
    page_icon="📝",
    layout="wide"
)

st.write("# 📝 Aclarador - Lenguaje Claro")
st.write("*Herramienta para mejorar la claridad de textos en español*")

# Sidebar for configuration
st.sidebar.write("## ⚙️ Configuración")

# LangSmith tracing toggle
if LANGSMITH_ENABLED:
    tracing_enabled = st.sidebar.toggle(
        "🔍 LangSmith Tracing",
        value=True,
        help="Activar/desactivar el seguimiento de LangSmith para análisis detallado"
    )

    if tracing_enabled:
        st.sidebar.success("✅ Tracing activo")
        # Set environment variables when enabled
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "aclarador"
    else:
        st.sidebar.info("⏸️ Tracing desactivado")
        # Disable tracing when toggled off
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
else:
    st.sidebar.info("🔍 LangSmith: No disponible")
    tracing_enabled = False

# System prompt status
system_prompt_loaded = load_system_prompt() is not None
if system_prompt_loaded:
    st.sidebar.success("📖 Manual de Estilo: Cargado")
else:
    st.sidebar.warning("📖 Manual de Estilo: Usando prompt básico")

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
        # Use the tracing state from the toggle
        processed_output = process_text(user_input, enable_tracing=tracing_enabled)
        st.write("## 📋 Resultado")
        st.markdown(processed_output)

# Footer
st.write("---")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.write("**🎯 Principios del lenguaje claro:**")
    st.write("• Una idea por oración")
    st.write("• Máximo 30 palabras por oración")
    st.write("• Evitar jerga técnica")
    st.write("• Estructura lógica y coherente")

with col_f2:
    st.write("**📖 Manual de Estilo:**")
    st.write("• Vocabulario claro y preciso")
    st.write("• Voz activa preferente")
    st.write("• Puntuación efectiva")
    st.write("• Adaptación digital y SEO")

with col_f3:
    st.write("**📊 Estado del sistema:**")
    st.write(f"• Manual de Estilo: {'✅ Cargado' if system_prompt_loaded else '⚠️ Básico'}")
    if LANGSMITH_ENABLED:
        st.write(f"• LangSmith: {'🔍 Activo' if tracing_enabled else '⏸️ Inactivo'}")
    else:
        st.write("• LangSmith: ❌ No disponible")
    st.write(f"• Groq API: {'✅ Configurado' if client else '❌ No configurado'}")