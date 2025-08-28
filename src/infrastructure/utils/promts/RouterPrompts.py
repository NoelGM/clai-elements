from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

from src.logger.logger_config import logger

logger = logger.bind(category="agents")


# Prompt y cadena de generacion del prompt para FHIR
def router_obtener_prompt(modelo: str, tipo_prompt: str):
    # Templates según tipos y modelos
    llama_templates = {
        "router": ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """
                Eres un experto en dirigir preguntas del usuario a la etapa de generación, búsqueda web o respuestas generales, según corresponda. A continuación, los criterios para seleccionar la mejor opción:
                
                1. Si la pregunta requiere información reciente o más contexto específico que no esté disponible directamente en el modelo, debes devolver 'web_search' y realizar una búsqueda en internet.
                2. Si la pregunta es general y no necesita búsqueda previa en internet para ser respondida correctamente (como hechos comunes o información general), debes devolver 'generate' para generar la respuesta.
                3. Si la pregunta es un saludo, una pregunta trivially general, o no requiere contexto adicional (por ejemplo, cálculos matemáticos, saludos, etc.), devuelve 'chat'.
                4. Si la pregunta está relacionada con información concreta sobre un paciente determinado, debes devolver 'graph'.
                5. Si la pregunta es sobre la historia clínica completa, debes devolver 'texto'.
                6. Si en la pregunta hay algún indicio que indique que se debe buscar sobre algún repositorio médico como PubMed, ClinicalTrials, etc., y no internet, debes devolver 'repo'. 

                Asegúrate de seleccionar la opción más adecuada para cada pregunta. Devuelve solo una de las siguientes opciones: 'web_search', 'generate', 'chat', 'graph', 'texto' o 'repo'.
                Retorna la respuesta en formato JSON con la clave 'choice' que contenga la opción seleccionada, sin preámbulos ni explicaciones adicionales.
                """
            ),
            HumanMessagePromptTemplate.from_template(""" Pregunta para direccionar: {question}""")
        ]),
        "general": ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """
                Eres un copiloto de IA para tareas de preguntas sobre atención clínica, que, dependiendo de la pregunta, sintetiza resultados de búsquedas en la web.
                Utiliza las piezas de contexto proporcionadas resultado de la búsqueda web, si lo hay, para responder la pregunta, pero no hagas referencia en 
                tu respuesta a que se ha realizado una busqueda web previa cuyo resultado se te ha indicado.
                Usa el historial previo de interacciones con el usuario para dar una respueta más fluida.
                Es importante que, si no sabes la respuesta, digas simplemente que no lo sabes.
                Cuando se incorpora resultados de la busqueda web, mantén la respuesta concisa.
                Si el contexto es "chat" responde de forma coloquial, pero concisa, y si hacer ninguna referencia al historial de interacciones previas. 
                Igualmente, si el contexto es "chat", no sigas dando nueva información referente a lo que se haya hablado en el historial
                No metas nunca en tus respuestas ninguna frase literal que sea parte del historial previo.
                Entradas de la historia clínica relevantes: {context} 
                """
            ),
            HumanMessagePromptTemplate.from_template(
                """
                Pregunta actual: {question}  
                
                Respuesta:
                """  )
        ]),
        "FHIR": ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """
                A continuación, te proporciono un conjunto de entradas con detalles de la historia clínica de un paciente, junto con información previa de una conversación anterior (memoria). 

                Tu tarea es responder preguntas sobre la historia clínica basándote únicamente en la información proporcionada. 
                **Es importante que respondas siempre en español y sólo respondas a la pregunta concreta que se te haga sobre la historia clínica.**

                Instrucciones:
                - Utiliza la memoria de la conversación (pregunta y respuesta anterior) como contexto adicional para entender mejor la pregunta actual.
                - Basa todas tus respuestas exclusivamente en la información proporcionada en la historia clínica y el contexto de la memoria.
                - Si la información no está disponible en los datos proporcionados, responde exclusivamente con: "No se encontró esta información en la historia clínica". No añadas nada más.
                - Responde de forma breve y precisa, sin añadir resúmenes ni explicaciones no solicitadas.
                - Si la pregunta no es relativa a la historia clínica, responde exclusivamente con: "La pregunta no tiene relación con la historia clínica".
                - Si es un saludo o comentario trivial, puedes responder de forma cordial ignorando la historia clínica.
                - Responde siempre en español.
                 
                """
            ),
            HumanMessagePromptTemplate.from_template(
                """
                Pregunta actual: {question}  
                Entradas de la historia clínica relevantes: {context}
                Respuesta: 
                """  )
        ]),
         "forms": ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """
                Eres un copiloto de IA especializado en ayudar a los médicos a completar formularios clínicos sobre su paciente correctamente.
                Tu tarea es ayudar a interpretar, explicar y completar los campos del formulario en base a las preguntas y opciones disponibles.
                Usa únicamente la información de contexto extraída del formulario que se te ha proporcionado, y evita mencionar que proviene de un formulario o que se te ha pasado como contexto.

                {{'%- if contexto_hc %'}}
                Además, tienes acceso a información relevante de la historia clínica del paciente, que puedes usar para complementar tus respuestas si es necesario. Si no es relevante para la pregunta, ignórala.
                {{'%- endif %'}}
                Puedes usar el historial previo de interacciones con el usuario para dar una respuesta más coherente y natural.
                Si el contexto no está relacionado con un formulario, responde de forma general.

                Si no conoces la respuesta, responde con sinceridad que no puedes ayudar con esa información.
                No repitas ni cites literalmente fragmentos del historial.

                Mantén siempre un tono claro, útil y respetuoso. Si el usuario está confundido, ofrece una sugerencia concreta basada en las preguntas y opciones extraídas.
                """
                ),
            HumanMessagePromptTemplate.from_template(
                    """
                    Historial previo:
                    - Preguntas anteriores: {historial_p}
                    - Respuestas anteriores: {historial_r}

                    Pregunta actual del usuario: {question}

                    Preguntas y opciones del formulario: {context}

                    Respuesta:
                    """
                )    
                ]),   
            "transformar_hc": ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(
                """
                
                Eres un asistente experto en formular preguntas para consultar la historia clínica de un paciente.

                - Si la pregunta que se te pasa trata exclusivamente sobre el cuestionario y NO es necesaria información de la historia clínica, responde con el siguiente JSON:{{"hc": "No es necesaria información de la historia clínica para responder a esta pregunta"}}.
                - Si la pregunta es del tipo "Ayúdame con la pregunta X", DEBES consultar el texto de la pregunta X en el formulario. Si ese texto requiere información de la historia clínica (por ejemplo: "¿Está el calendario vacunal actualizado?", "¿Hubo alguna reacción adversa documentada tras las inmunizaciones?", "¿Está documentado dolor crónico?", "¿Está presente alguna alteración neurológica significativa?"), transforma la pregunta X en una pregunta específica que pueda ser respondida a partir de la historia clínica. Si el texto de la pregunta X NO requiere datos de la historia clínica, responde con el JSON con el mensaje indicado.
                - Si por ejemplo te preguntan "¿Hay alguna información relevante sobre la pregunta 13 en la historia clínica?", debes coger la pregunta 13 del formulario y reformularla para que sea una pregunta sobre la historia clínica, como por ejemplo: "¿Qué antecedentes médicos relevantes tiene el paciente relacionados con la pregunta 13?".
                
                - Devuelve SIEMPRE SOLO un JSON con la clave 'hc' y el valor la pregunta reformulada o la cadena vacía según corresponda.
                - NO añadas explicaciones, texto adicional, ni comentarios antes o después del JSON.
                - Ejemplo de salida: {{"hc": "¿Qué antecedentes médicos tiene el paciente?"}}
                """
                    ),
                HumanMessagePromptTemplate.from_template(
                    """
                    Pregunta original: {question}
                    """
                )
                ]),
            "combinar_forms_hc": ChatPromptTemplate.from_messages([
                 SystemMessagePromptTemplate.from_template(
                """

                Eres un asistente clínico experto en combinar información de formularios médicos y de la historia clínica de un paciente.
                Tu tarea es analizar la pregunta del usuario y, usando la respuesta generada a partir del formulario y la información relevante de la historia clínica, devolver una única respuesta clara y útil para el médico.

                Si la información de la historia clínica es relevante para la pregunta y complementa la respuesta del formulario, intégrala de forma natural y coherente.
                Si la información de la historia clínica no aporta nada relevante, prioriza la respuesta del formulario.
                Si la respuesta del formulario no es suficiente pero la historia clínica sí contiene la información necesaria, prioriza la historia clínica.
                No repitas información ni hagas referencias explícitas a "formulario" o "historia clínica", simplemente responde como si tuvieras toda la información.
                Usa el historial de la conversación solo si ayuda a clarificar la respuesta.
                Responde siempre en español, de forma breve, precisa y profesional.
               """
                ),
                HumanMessagePromptTemplate.from_template(
                    """
                    Historial previo:
                    - Preguntas anteriores: {historial_p}
                    - Respuestas anteriores: {historial_r}
                    Pregunta del usuario: {question}

                    Respuesta generada a partir del formulario:
                    {context}

                    Información relevante de la historia clínica:
                    {contexto_hc}

                    Respuesta final combinada:
                    """
                )
            ]),

    }

    phi4_templates = {
        # Puedes definir plantillas específicas para phi4 aquí si es necesario
    }

    # Diccionario que mapea los modelos a los templates
    prompts = {
        "llama3:latest": llama_templates,
        "llama3.2:3b": llama_templates,
        "llama3.1:8b": llama_templates,
        "phi4:14b": llama_templates,
        "deepseek-r1:7b": llama_templates,
        "deepseek-r1:32b": llama_templates,
        "mistral-small:24b": llama_templates,
        "deepseek-r1:8b": llama_templates,
        "qwen2.5:1.5b": llama_templates,
        "qwen2.5:3b": llama_templates,
        "qwen2.5:7b": llama_templates,
        "llama3:8b-instruct-q8_0": llama_templates,
        "llama3.1:8b-instruct-q4_0": llama_templates,
        "llama": llama_templates,
        "cogito:latest": llama_templates,
        "phi": phi4_templates,
    }

    # Devuelve el prompt correspondiente al modelo y al tipo
    if "llama" in modelo:
        return prompts["llama"][tipo_prompt] 
    elif "phi" in modelo:
        return phi4_templates["phi4:14b"][tipo_prompt]
    else:
        return prompts["llama"][tipo_prompt]     