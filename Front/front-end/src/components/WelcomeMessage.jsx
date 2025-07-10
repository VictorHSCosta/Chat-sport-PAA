import { useState } from 'react'
import { Sparkles } from 'lucide-react'

const suggestedQuestions = [
  "Quando foi a última Copa do Mundo?",
  "Quem é o maior jogador de todos os tempos?",
  "Quantas Champions League o Real Madrid tem?",
  "Qual time tem mais Brasileirões?",
  "Quem ganhou a Bola de Ouro de 2024?",
  "Como está o Palmeiras este ano?",
  "Qual a história do Pelé?",
  "Quando é a próxima Copa do Mundo?",
  "Quem são os maiores artilheiros da história?",
  "Qual o maior clássico do futebol brasileiro?"
]

const WelcomeMessage = ({ onExampleClick }) => {
  const examplePrompts = [
    {
      title: "Copa do Mundo",
      text: "Quando foi a última Copa do Mundo?"
    },
    {
      title: "Maiores Jogadores",
      text: "Quem é o maior jogador de todos os tempos?"
    },
    {
      title: "Champions League",
      text: "Quantas Champions League o Real Madrid tem?"
    },
    {
      title: "Futebol Brasileiro",
      text: "Qual time tem mais Brasileirões?"
    },
    {
      title: "Bola de Ouro",
      text: "Quem ganhou a Bola de Ouro de 2024?"
    },
    {
      title: "História do Futebol",
      text: "Qual a história do Pelé?"
    }
  ]

  // Função para obter sugestões aleatórias
  const getRandomSuggestions = () => {
    const shuffled = [...suggestedQuestions].sort(() => 0.5 - Math.random())
    return shuffled.slice(0, 4)
  }

  const [randomSuggestions] = useState(getRandomSuggestions())

  return (
    <div className="welcome-message">
      <h2 className="welcome-title">⚽ Bem-vindo ao FootBot!</h2>
      <p className="welcome-subtitle">
        Sou seu assistente especializado em futebol. Posso responder sobre jogadores, times, 
        competições, história e curiosidades do mundo do futebol.
      </p>
      
      <div className="example-prompts">
        {examplePrompts.map((prompt, index) => (
          <div 
            key={index}
            className="example-prompt"
            onClick={() => onExampleClick(prompt.text)}
          >
            <div className="example-prompt-title">{prompt.title}</div>
            <div className="example-prompt-text">{prompt.text}</div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h3 style={{ 
          color: '#f0f6fc', 
          fontSize: '1.1rem', 
          marginBottom: '1rem', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem', 
          justifyContent: 'center' 
        }}>
          <Sparkles size={20} color="#1f6feb" />
          Sugestões Aleatórias
        </h3>
        <div className="random-suggestions">
          {randomSuggestions.map((suggestion, index) => (
            <button
              key={index}
              className="suggestion-button"
              onClick={() => onExampleClick(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default WelcomeMessage
