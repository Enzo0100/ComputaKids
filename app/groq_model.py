from groq import Groq

class GroqModel:
    def __init__(self, api_key, model="llama3-70b-8192"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 300,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }

    def get_response(self, prompt, **kwargs):
        """
        Envia o prompt para a API Groq e retorna a resposta.
        
        Args:
            prompt (str): O prompt para enviar ao modelo
            **kwargs: Parâmetros opcionais para sobrescrever os defaults
                     (temperature, max_tokens, top_p, etc.)
        """
        try:
            # Mescla os parâmetros default com os fornecidos
            params = {**self.default_params, **kwargs}
            
            # Prepara o sistema para responder como especialista em arquitetura de computadores
            messages = [
                {"role": "system", "content": "Você é um professor especializado em Arquitetura e Organização de Computadores, com vasto conhecimento em hardware, sistemas digitais e arquitetura de processadores. Responda sempre em português do Brasil, usando terminologia técnica apropriada e mantendo o rigor acadêmico, mas sendo claro e objetivo nas explicações."},
                {"role": "user", "content": prompt}
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=params["temperature"],
                max_tokens=params["max_tokens"],
                top_p=params["top_p"],
                frequency_penalty=params["frequency_penalty"],
                presence_penalty=params["presence_penalty"]
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Erro ao obter resposta do Groq: {str(e)}")
            raise
