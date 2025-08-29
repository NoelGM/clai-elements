from abc import ABC

import ollama

from src.domain.ports.agents.agent import Agent


class LlamaAgent(Agent, ABC):

    def __init__(
            self,
            name,
            max_retries: int = 2,
            verbose: bool = True,
            logger_=None
    ):
        super().__init__(name, max_retries=max_retries, verbose=verbose, logger_=logger_)

    # TODO probablemente se elimine este método, por lo tanto no haría falta tampoco este nivel de abstracción y se eliminaría la clase LLamaAgent
    def call_llm(self, messages, temperature=0.7, max_tokens=150):
        """
        Calls the Llama model via Ollama and retrieves the response.

        Args:
            messages (list): A list of message dictionaries.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum number of tokens in the response.

        Returns:
            str: The content of the model's response.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                if self.verbose:
                    self.logger.info(f"[{self.name}] Sending messages to Ollama:")
                    for msg in messages:
                        self.logger.debug(f"  {msg['role']}: {msg['content']}")

                # Call the Ollama chat API
                response = ollama.chat(
                    model='gemma2:2b',  # Updated model name
                    messages=messages
                )

                # Parse the response to extract the text content
                reply = response['message']['content']

                if self.verbose:
                    self.logger.info(f"[{self.name}] Received response: {reply}")

                return reply
            except Exception as e:
                retries += 1
                self.logger.error(f"[{self.name}] Error during Ollama call: {e}. Retry {retries}/{self.max_retries}")
        raise Exception(f"[{self.name}] Failed to get response from Ollama after {self.max_retries} retries.")