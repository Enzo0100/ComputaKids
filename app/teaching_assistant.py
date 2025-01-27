class TeachingAssistant:
    def __init__(self, groq_model):
        self.groq_model = groq_model
        self.current_question = None
        self.current_level = 0
        self.questions_per_level = 3
        self.questions_answered = 0
        self.topics = {
            0: [
                "arquitetura von Neumann",
                "ciclo de instrução",
                "registradores",
                "memória principal",
                "unidade lógica e aritmética",
                "barramento de dados",
                "barramento de endereços",
                "barramento de controle",
                "clock do processador"
            ],
            1: [
                "memória cache",
                "pipeline",
                "conjunto de instruções",
                "arquitetura RISC",
                "arquitetura CISC",
                "memória virtual",
                "DMA (Direct Memory Access)",
                "interrupções",
                "E/S mapeada em memória",
                "microarquitetura"
            ],
            2: [
                "hierarquia de memória",
                "barramentos",
                "unidade de controle",
                "paralelismo em nível de instrução",
                "superescalar",
                "branch prediction",
                "memória associativa",
                "coerência de cache",
                "protocolo MESI",
                "arquitetura multicore",
                "SIMD (Single Instruction Multiple Data)",
                "MIMD (Multiple Instruction Multiple Data)"
            ]
        }
        
    def start_level(self, level):
        """Inicia um novo nível."""
        if level >= len(self.topics):
            return {
                "gameComplete": True,
                "message": "Parabéns! Você completou todos os níveis! 🎉"
            }
        
        self.current_level = level
        self.questions_answered = 0
        question_data = self.generate_question()
        return {
            "type": "question",
            "text": question_data["question"]["question"],
            "question": question_data["question"],
            "progress": 0
        }

    def next_question(self):
        """Gera a próxima pergunta do nível atual."""
        self.questions_answered += 1
        if self.questions_answered >= self.questions_per_level:
            return {
                "levelComplete": True,
                "message": "Nível completo! 🎉"
            }
            
        question_data = self.generate_question()
        return {
            "type": "question",
            "text": question_data["question"]["question"],
            "question": question_data["question"],
            "progress": (self.questions_answered / self.questions_per_level) * 100
        }
        
    def process_question(self, user_input, level=None):
        """Processa a entrada do usuário e retorna uma resposta apropriada."""
        if level is not None and level != self.current_level:
            self.current_level = level
            
        if "o que é" in user_input.lower() or "para que serve" in user_input.lower():
            return self.explain_concept(user_input)
        
        if self.current_question:
            return self.check_answer(user_input)
        
        question_data = self.generate_question()
        return {
            "type": "question",
            "text": question_data["question"]["question"],
            "question": question_data["question"],
            "progress": (self.questions_answered / self.questions_per_level) * 100
        }

    def explain_concept(self, concept):
        """Cria um prompt para explicar conceitos de arquitetura de computadores."""
        prompt = (
            f"Explique o conceito de '{concept}' no contexto de Arquitetura e Organização de Computadores. "
            "Use linguagem técnica apropriada, mas mantenha a explicação clara e objetiva. "
            "Inclua exemplos práticos quando possível e relacione com outros conceitos relevantes. "
            "Se aplicável, mencione a evolução histórica e as implementações modernas. "
            "Responda em português e mantenha um tom profissional."
        )
        return {
            "type": "explanation",
            "text": self.groq_model.get_response(prompt)
        }

    def generate_question(self):
        """Gera uma nova pergunta usando o LLM."""
        import random
        
        if self.current_level not in self.topics:
            return {
                "type": "error",
                "message": "Nível inválido"
            }
            
        topic = random.choice(self.topics[self.current_level])
        prompt = (
            f"Crie uma pergunta técnica sobre {topic} no contexto de Arquitetura e Organização de Computadores. "
            "A pergunta deve ser adequada para estudantes de computação. "
            f"Para o nível {self.current_level} (0=básico, 1=intermediário, 2=avançado), "
            "ajuste a complexidade técnica apropriadamente. "
            "A pergunta pode envolver comparações, análises de desempenho, casos de uso, "
            "vantagens e desvantagens, ou aspectos históricos do tema. "
            "Forneça a resposta esperada e 5 conceitos-chave relacionados ao tema. "
            "Responda no seguinte formato JSON:\n"
            "{\n"
            '  "question": "sua pergunta técnica aqui",\n'
            '  "expected_answer": "resposta técnica detalhada aqui",\n'
            '  "keywords": ["conceito1", "conceito2", "conceito3", "conceito4", "conceito5"],\n'
            '  "points": "número de pontos (10-20)"\n'
            "}"
        )
        
        try:
            response = self.groq_model.get_response(prompt)
            # Limpa a resposta para garantir que é um JSON válido
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:-3]  # Remove ```json e ```
            
            import json
            question_data = json.loads(response)
            
            self.current_question = {
                "topic": topic,
                "question": question_data["question"],
                "expected_answer": question_data["expected_answer"],
                "keywords": question_data["keywords"],
                "points": int(question_data.get("points", 10)),
                "progress": (self.questions_answered / self.questions_per_level) * 100
            }
            
            return {
                "question": self.current_question
            }
            
        except Exception as e:
            # Fallback para uma pergunta básica em caso de erro
            self.current_question = {
                "topic": topic,
                "question": f"Explique o conceito de {topic} no contexto de Arquitetura de Computadores.",
                "expected_answer": f"Uma explicação técnica sobre {topic} e sua importância na arquitetura de computadores",
                "keywords": [topic, "arquitetura", "computador", "hardware", "processamento"],
                "points": 10,
                "progress": (self.questions_answered / self.questions_per_level) * 100
            }
            
            return {
                "question": self.current_question
            }

    def check_answer(self, user_answer):
        """Verifica a resposta do usuário."""
        if not self.current_question:
            question_data = self.generate_question()
            return {
                "type": "question",
                "text": question_data["question"]["question"],
                "question": question_data["question"],
                "progress": (self.questions_answered / self.questions_per_level) * 100
            }

        # Verifica as palavras-chave na resposta do usuário
        user_words = user_answer.lower().split()
        matched_keywords = [
            keyword for keyword in self.current_question["keywords"]
            if keyword.lower() in user_words
        ]

        # Usa o LLM para avaliar a resposta de forma mais técnica
        prompt = (
            f"Avalie tecnicamente a resposta para a seguinte questão de Arquitetura de Computadores:\n\n"
            f"Pergunta: {self.current_question['question']}\n"
            f"Resposta esperada: {self.current_question['expected_answer']}\n"
            f"Resposta do aluno: {user_answer}\n\n"
            "Considere a precisão técnica, uso correto dos conceitos e profundidade da explicação. "
            "Responda apenas com 'correto' ou 'incorreto'"
        )
        
        try:
            evaluation = self.groq_model.get_response(prompt).lower().strip()
            is_correct = evaluation == "correto" or len(matched_keywords) >= len(self.current_question["keywords"]) * 0.6
            
            if is_correct:
                points = self.current_question["points"]
                expected_answer = self.current_question["expected_answer"]
                self.questions_answered += 1
                level_complete = self.questions_answered >= self.questions_per_level
                self.current_question = None  # Reset para próxima pergunta
                
                return {
                    "type": "feedback",
                    "correct": True,
                    "message": "Excelente! Sua resposta demonstra compreensão técnica do conceito.",
                    "explanation": expected_answer,
                    "points": points,
                    "levelComplete": level_complete
                }
            else:
                return {
                    "type": "feedback",
                    "correct": False,
                    "message": "Sua resposta precisa de mais precisão técnica.",
                    "hint": f"Revise os conceitos de {', '.join(self.current_question['keywords'][:2])}..."
                }
                
        except Exception as e:
            # Fallback para verificação básica em caso de erro do LLM
            is_correct = len(matched_keywords) >= len(self.current_question["keywords"]) * 0.6
            
            if is_correct:
                points = self.current_question["points"]
                expected_answer = self.current_question["expected_answer"]
                self.questions_answered += 1
                level_complete = self.questions_answered >= self.questions_per_level
                self.current_question = None
                
                return {
                    "type": "feedback",
                    "correct": True,
                    "message": "Excelente! Sua resposta demonstra compreensão técnica do conceito.",
                    "explanation": expected_answer,
                    "points": points,
                    "levelComplete": level_complete
                }
            else:
                return {
                    "type": "feedback",
                    "correct": False,
                    "message": "Sua resposta precisa de mais precisão técnica.",
                    "hint": f"Revise os conceitos de {', '.join(self.current_question['keywords'][:2])}..."
                }

    def get_progress(self):
        """Retorna o progresso atual do aluno."""
        return {
            "level": self.current_level,
            "questions_answered": self.questions_answered,
            "total_questions": self.questions_per_level,
            "progress": (self.questions_answered / self.questions_per_level) * 100,
            "current_topic": self.current_question["topic"] if self.current_question else None,
            "topics_available": self.topics[self.current_level]
        }
