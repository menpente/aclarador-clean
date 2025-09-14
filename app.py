import streamlit as st
from PIL import Image
from groq import Groq
import os

# Initialize the Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Function to process the input text
def process_text(input_text):
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
    input = prompt + input_text

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": input,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

# Main app
st.write("# Inicio")

# Create a text input widget with session state
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

user_input = st.text_input('Pega tu texto:', st.session_state["user_input"])

# Create a button to submit the input
if st.button("Enviar"):
    processed_output = process_text(user_input)
    st.write('Aquí está el texto corregido:\n', processed_output)
    st.session_state["user_input"] = ""  # Clear the input field after processing