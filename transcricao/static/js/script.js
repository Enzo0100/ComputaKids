// Configuração do jogo
const gameConfig = {
  currentLevel: 0,
  score: 0,
  stars: 0,
  currentQuestion: null,
  isConsultMode: false,
  totalLevels: 3,
  questionsAnswered: 0,
  questionsPerLevel: 3
};

// Elementos do DOM
const elements = {
  score: document.getElementById("score"),
  messages: document.getElementById("messages"),
  startRecording: document.getElementById("start-recording"),
  stopRecording: document.getElementById("stop-recording"),
  userInput: document.getElementById("user-input"),
  sendButton: document.getElementById("send-button"),
  questionText: document.getElementById("question-text"),
  speechBubble: document.getElementById("speech-bubble"),
  feedback: document.getElementById("feedback"),
  progress: document.getElementById("progress"),
  levelComplete: document.getElementById("level-complete"),
  nextLevel: document.getElementById("next-level"),
  skipQuestion: document.getElementById("skip-question"),
  toggleMode: document.getElementById("toggle-mode"),
  scoreBoard: document.querySelector(".score-board"),
  progressBar: document.querySelector(".progress-bar"),
  gameComplete: document.getElementById("game-complete"),
  finalScore: document.getElementById("final-score"),
  restartGame: document.getElementById("restart-game"),
  skipModal: document.getElementById("skip-modal"),
  correctAnswer: document.getElementById("correct-answer"),
  continueGame: document.getElementById("continue-game")
};

// Variáveis para gravação de áudio
let mediaRecorder = null;
let audioChunks = [];

// Inicialização
async function initGame() {
  setupEventListeners();
  setupVoiceRecording();
  await startLevel(gameConfig.currentLevel);
}

// Configuração dos event listeners
function setupEventListeners() {
  elements.sendButton.addEventListener("click", handleTextSubmission);
  elements.userInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleTextSubmission();
    }
  });
  elements.nextLevel.addEventListener("click", async () => {
    gameConfig.currentLevel++;
    if (gameConfig.currentLevel >= gameConfig.totalLevels) {
      showGameComplete();
    } else {
      await startLevel(gameConfig.currentLevel);
      elements.levelComplete.classList.add("hidden");
    }
  });

  // Event listeners para gravação
  elements.startRecording.addEventListener("click", startRecording);
  elements.stopRecording.addEventListener("click", stopRecording);

  // Event listener para pular questão
  elements.skipQuestion.addEventListener("click", handleSkipQuestion);

  // Event listener para alternar modo
  elements.toggleMode.addEventListener("click", toggleMode);

  // Event listener para reiniciar jogo
  elements.restartGame.addEventListener("click", restartGame);

  // Event listener para continuar após pular
  elements.continueGame.addEventListener("click", async () => {
    elements.skipModal.classList.add("hidden");
    await nextQuestion();
  });
}

// Verificar progresso do nível
function checkLevelProgress() {
  if (gameConfig.questionsAnswered >= gameConfig.questionsPerLevel) {
    if (gameConfig.currentLevel >= gameConfig.totalLevels - 1) {
      showGameComplete();
    } else {
      completeLevel();
    }
    return true;
  }
  return false;
}

// Lidar com pular questão
async function handleSkipQuestion() {
  if (!gameConfig.currentQuestion) return;

  elements.correctAnswer.textContent = gameConfig.currentQuestion.expected_answer;
  elements.skipModal.classList.remove("hidden");
  elements.speechBubble.classList.add("hidden");
  showMessage(`A resposta correta é: ${gameConfig.currentQuestion.expected_answer}`, "bot");
  fetch('/speak', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: `A resposta correta é: ${gameConfig.currentQuestion.expected_answer}` })
  })
  .then(response => response.blob())
  .then(blob => {
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.addEventListener('canplaythrough', () => {
        audio.play();
    });
  })
  .catch(error => console.error('Erro ao obter áudio:', error));
}

// Reiniciar jogo
async function restartGame() {
  gameConfig.currentLevel = 0;
  gameConfig.score = 0;
  gameConfig.stars = 0;
  gameConfig.currentQuestion = null;
  gameConfig.questionsAnswered = 0;
  elements.score.textContent = "0";
  elements.gameComplete.classList.add("hidden");
  await startLevel(0);
}

// Mostrar tela de fim de jogo
function showGameComplete() {
  elements.finalScore.textContent = gameConfig.score;
  elements.gameComplete.querySelector(".total-stars").textContent = "⭐".repeat(calculateTotalStars());
  elements.gameComplete.classList.remove("hidden");
}

// Calcular total de estrelas
function calculateTotalStars() {
  const maxPossibleScore = gameConfig.totalLevels * (gameConfig.questionsPerLevel * 10);
  const percentage = (gameConfig.score / maxPossibleScore) * 100;
  
  if (percentage >= 90) return 3;
  if (percentage >= 70) return 2;
  return 1;
}

// Alternar entre modo jogo e consulta
function toggleMode() {
  gameConfig.isConsultMode = !gameConfig.isConsultMode;
  elements.toggleMode.classList.toggle("active");
  
  if (gameConfig.isConsultMode) {
    elements.toggleMode.innerHTML = '<span class="icon">🎮</span> Modo Jogo';
    elements.scoreBoard.classList.add("hidden");
    elements.progressBar.classList.add("hidden");
    elements.skipQuestion.classList.add("hidden");
    elements.userInput.placeholder = "Faça uma pergunta sobre Arquitetura de Computadores...";
    elements.speechBubble.classList.add("hidden");
  } else {
    elements.toggleMode.innerHTML = '<span class="icon">💭</span> Modo Consulta';
    elements.scoreBoard.classList.remove("hidden");
    elements.progressBar.classList.remove("hidden");
    elements.skipQuestion.classList.remove("hidden");
    elements.userInput.placeholder = "Ou digite sua resposta...";
    startLevel(gameConfig.currentLevel);
  }
}

// Configuração da gravação de voz
async function setupVoiceRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      await sendAudioToServer(audioBlob);
      audioChunks = [];
    };

    elements.startRecording.disabled = false;
    elements.startRecording.title = "Clique para começar a gravar";
  } catch (error) {
    console.error("Erro ao configurar gravação:", error);
    showMessage("Não foi possível acessar o microfone. Por favor, use o campo de texto.", "bot");
  }
}

// Iniciar gravação
function startRecording() {
  if (mediaRecorder && mediaRecorder.state === "inactive") {
    mediaRecorder.start();
    elements.startRecording.disabled = true;
    elements.stopRecording.disabled = false;
    elements.startRecording.classList.add("recording");
    showMessage("Gravando... Fale sua resposta!", "bot");
  }
}

// Parar gravação
function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    elements.startRecording.disabled = false;
    elements.stopRecording.disabled = true;
    elements.startRecording.classList.remove("recording");
    showMessage("Processando sua resposta...", "bot");
  }
}

// Enviar áudio para o servidor
async function sendAudioToServer(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob);

  try {
    const response = await fetch('/transcribe', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();

    if (data.error) {
      showMessage(data.error, "bot");
      return;
    }

    if (data.transcription) {
      showMessage(`Você disse: ${data.transcription}`, "user");
      // Enviar transcrição para processamento
      await handleTextSubmission(data.transcription);
    }

  } catch (error) {
    console.error("Erro ao enviar áudio:", error);
    showMessage("Ocorreu um erro ao processar o áudio. Tente novamente.", "bot");
  }
}

// Lidar com envio de texto
async function handleTextSubmission(transcription = null) {
  const userInput = transcription || elements.userInput.value.trim();
  if (!userInput) return;

  if (!transcription) {
    showMessage(userInput, "user");
    elements.userInput.value = "";
  }

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        question: userInput,
        level: gameConfig.currentLevel,
        currentQuestion: gameConfig.currentQuestion,
        isConsultMode: gameConfig.isConsultMode
      })
    });

    const data = await response.json();

    if (data.error) {
      showMessage(data.error, "bot");
      return;
    }

    if (data.type === "feedback") {
      handleFeedback(data);
    } else if (data.type === "question") {
      handleNewQuestion(data);
    } else if (data.type === "explanation") {
      showMessage(data.text, "bot");
    }

  } catch (error) {
    console.error("Erro ao enviar mensagem:", error);
    showMessage("Ocorreu um erro ao processar sua resposta. Tente novamente.", "bot");
  }
}

// Lidar com feedback
function handleFeedback(data) {
  if (data.correct) {
    gameConfig.score += data.points || 10;
    elements.score.textContent = gameConfig.score;
    showFeedback(data.message, "correct");
    gameConfig.questionsAnswered++;
    updateProgress();
    
    setTimeout(() => {
      if (!checkLevelProgress()) {
        nextQuestion();
      }
    }, 2000);
  } else {
    showFeedback(data.message, "incorrect");
    if (data.hint) {
      setTimeout(() => {
        showMessage(data.hint, "bot");
      }, 1000);
    }
  }
}

// Lidar com nova pergunta
function handleNewQuestion(data) {
  if (!gameConfig.isConsultMode) {
    gameConfig.currentQuestion = data.question;
    elements.questionText.textContent = data.text;
    elements.speechBubble.classList.remove("hidden");
    updateProgress();
  }
}

// Mostrar feedback
function showFeedback(message, type) {
  elements.feedback.classList.remove("hidden");
  elements.feedback.querySelector(".feedback-text").textContent = message;
  elements.feedback.className = `feedback ${type}`;
  
  setTimeout(() => {
    elements.feedback.classList.add("hidden");
  }, 2000);
}

// Atualizar progresso
function updateProgress() {
  if (!gameConfig.isConsultMode) {
    const progress = (gameConfig.questionsAnswered / gameConfig.questionsPerLevel) * 100;
    elements.progress.style.width = `${progress}%`;
  }
}

// Completar nível
function completeLevel() {
  const stars = calculateStars();
  gameConfig.stars = stars;
  gameConfig.questionsAnswered = 0;
  
  elements.levelComplete.querySelector(".stars-earned").textContent = "⭐".repeat(stars);
  elements.levelComplete.classList.remove("hidden");
}

// Calcular estrelas
function calculateStars() {
  const maxPossibleScore = (gameConfig.currentLevel + 1) * (gameConfig.questionsPerLevel * 10);
  const percentage = (gameConfig.score / maxPossibleScore) * 100;
  
  if (percentage >= 90) return 3;
  if (percentage >= 70) return 2;
  return 1;
}

// Iniciar nível
async function startLevel(levelIndex) {
  if (gameConfig.isConsultMode) return;

  try {
    const response = await fetch(`/start_level/${levelIndex}`);
    const data = await response.json();
    
    if (data.error) {
      showMessage(data.error, "bot");
      return;
    }
    
    if (data.gameComplete) {
      showGameComplete();
      return;
    }

    gameConfig.currentQuestion = data.question;
    updateProgress();
    handleNewQuestion(data);
  } catch (error) {
    console.error("Erro ao iniciar nível:", error);
    showMessage("Ocorreu um erro ao carregar o nível. Tente novamente.", "bot");
  }
}

// Próxima pergunta
async function nextQuestion() {
  if (gameConfig.isConsultMode) return;

  try {
    const response = await fetch(`/next_question/${gameConfig.currentLevel}`);
    const data = await response.json();
    
    if (data.error) {
      showMessage(data.error, "bot");
      return;
    }
    
    handleNewQuestion(data);
  } catch (error) {
    console.error("Erro ao carregar próxima pergunta:", error);
    showMessage("Ocorreu um erro ao carregar a próxima pergunta. Tente novamente.", "bot");
  }
}

// Mostrar mensagem
function showMessage(text, sender) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${sender}`;
  messageDiv.textContent = text;
  elements.messages.appendChild(messageDiv);
  elements.messages.scrollTop = elements.messages.scrollHeight;
}

// Iniciar o jogo
initGame();
