# model_config.py
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from prompt import template, prompt_7b_2  # Importar el template desde el archivo prompt.py

def initialize_model(model="sqlcoder"):
    # Inicializar el modelo OllamaLLM
    if model == "pxlksr/defog_sqlcoder-7b-2:F16":
        template_to_use = prompt_7b_2
    else:
        template_to_use = template
    model = OllamaLLM(
        model=model,
        #num_gpu=1, # habilito el uso de GPU
        num_ctx=2*4096, # Aumento el tamaño del contexto (por default es 2048)
        #num_predict=-1, # Dejo ilimitado el numero de tokens usados para predecir, en nuestro caso deberian ser siempre pocos
        #repeat_last_n=-1, # -1 es igual al numero del contexto, este parametro no deberia cambiar nada           
        #temperature=0.3, #, # por default es 0.8, en 0.5 le bajo la creatividad
        #tfs_z=1,
        top_k=25, # default es 40, si lo bajo, baja la creatividad, si lo subo es mas creativo
        top_p=0.3, # default 0.9, va en conjunto con top_k, si lo bajo, baja la creatividad, si lo subo es mas creativo
    )
    # Crear el prompt basado en el template
    prompt = ChatPromptTemplate.from_template(template_to_use)
    # Crear la cadena que combina el prompt y el modelo
    chain = prompt | model
    return chain

