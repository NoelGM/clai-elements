from langsmith import Client
from pydantic import BaseModel, Field
import ollama

from langsmith.evaluation import RunEvaluator
from langsmith.schemas import Run, Example
from typing import Optional

from src.logger.logger_config import logger

#   TODO NGM parametrizar y arreglar
config_dict = {
    "LANGSMITH_API_KEY": '...',
    "LANGSMITH_ENDPOINT": 'https://eu.api.smith.langchain.com'
}

logger = logger.bind(category="agents")

class EvalUtility:
    def __init__(self, config_dict):
        # LangSmith Client
        self.client = Client(
            api_key=config_dict.get("LANGSMITH_API_KEY"), 
            api_url=config_dict.get("LANGSMITH_ENDPOINT")
        )

        print("LangSmith Client initialized.")

        self.examples = [
            (
                "¿Cuándo fue la última consulta del paciente Jaume Guiral Llopis?",
                "La última consulta del paciente Jaume Guiral Llopis fue el 22 de octubre de 2024.",
            ),
            (
                "¿Qué enfermedades tiene diagnosticadas el paciente Jaume Guiral Llopis?",
                "El paciente Jaume Guiral Llopis tiene diagnosticada diabetes mellitus tipo 2.",
            ),
            (
                "¿Qué medicamentos tiene recetados el paciente Jaume Guiral Llopis?",
                "Los medicamentos del paciente Jaume Guiral son: Mupirocina 20 MG/G POMADA Anestesderma 25 MG CREMA Amoxicilina 250 MG 20 COMPRIMIDOS Nurofen 40 MG 10 SOBRES"
            ),
            (
                "Dame los datos de la cita más reciente del paciente Jaume Guiral y toda la información relacionada con este encuentro",
                "Fecha de inicio: 10/22/2024 a las 12:19:45 Fecha de finalización: 10/22/2024 a las 12:19:45 Clase del encuentro: Consultas Externas Tipo del encuentro: Enfermedad común y Accidentes no clasificables en otros valores de la tabla Inmunizaciones: DTPa (Difteria, Tétanos y Tosferina acelular) Poliomielitis (VIP, Poliomielitis inactivada) Hepatitis A Varicela Neumocócica (PCV13) También se menciona que el paciente recibió una solicitud de medicamento para Mupirocina 20 MG/G POMADA y que se registró una condición médica llamada Infección local de la piel y tejido subcutáneo."
            )
        ]

        self.inputs = [{"question": example[0]} for example in self.examples]
        self.outputs = [{"answer": example[1]} for example in self.examples]



        # Create a dataset in LangSmith
        self.dataset = self.client.create_dataset(
            dataset_name="Evaluación paciente Jaume Guiral",
            description="Dataset con preguntas clínicas para evaluar la precisión del modelo."
        )

        # Add examples to the dataset
        self.client.create_examples(
            inputs=self.inputs,
            outputs=self.outputs,
            dataset_id=self.dataset.id
        )

    def target(self, inputs: dict) -> dict:
        response = ollama.chat(
            model="llama3:latest",  # Change this to your preferred Ollama model
            messages=[
                { "role": "system", "content": "Answer the following question accurately" },
                { "role": "user", "content": inputs["question"] },
            ],
        )
        return { "answer": response["message"]["content"].strip() }

    instructions = """Evaluate Student Answer against Ground Truth for conceptual similarity and classify true or false: 
    - False: No conceptual match and similarity
    - True: Most or full conceptual match and similarity
    - Key criteria: Concept should match, not exact wording.
    """

    class Grade(BaseModel):
        score: bool = Field(
            description="Boolean that indicates whether the response is accurate relative to the reference answer"
        )

    def accuracy(self, outputs: dict, reference_outputs: dict) -> bool:
        response = ollama.chat(
            model="llama3",  # Change this to your preferred Ollama model
            messages=[
                { "role": "system", "content": self.instructions },
                {
                    "role": "user",
                    "content": f"""Ground Truth answer: {reference_outputs["answer"]}; 
                    Student's Answer: {outputs["response"]}"""
                },
            ]
        )
        return response["message"]["content"].lower() == "true"

    def get_accuracy_evaluator(self) -> RunEvaluator:
            def _evaluator(run: Run, example: Example) -> Optional[dict]:
                result = self.accuracy(run.outputs, example.outputs)
                return {"score": result}
            return RunEvaluator(name="custom_accuracy", evaluate=_evaluator)
    
    def run_evaluation(self):
        experiment_results = self.client.evaluate(
            self.target,
            data=self.dataset,  
            evaluators = [self.get_accuracy_evaluator()],
            experiment_prefix="first-eval-in-langsmith",
            max_concurrency=2,
        )
        return experiment_results
    
    