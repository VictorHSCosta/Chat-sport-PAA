import { useState } from 'react'
import { Trophy } from 'lucide-react'

const suggestedQuestions = [
  "Quantas copas o Brasil tem?",
  "Quem foi campeão da Copa de 2022?",
  "Qual país sediou mais Copas do Mundo?",
  "Quem foi o artilheiro da Copa de 2018?",
  "Quando será a próxima Copa do Mundo?",
  "Qual foi a primeira Copa do Mundo?",
  "Quantos gols Pelé fez em Copas?",
  "Quais países nunca ganharam uma Copa?",
  "Qual Copa teve mais gols?",
  "Argentina vs Brasil: histórico nas Copas"
]

const WelcomeMessage = ({ onExampleClick }) => {
  const examplePrompts = [
    {
      title: "Brasil Pentacampeão",
      text: "Quantas copas o Brasil tem?"
    },
    {
      title: "Copa Qatar 2022",
      text: "Quem foi campeão da Copa de 2022?"
    },
    {
      title: "História das Copas",
      text: "Qual país sediou mais Copas do Mundo?"
    },
    {
      title: "Artilheiros Históricos",
      text: "Quem foi o artilheiro da Copa de 2018?"
    },
    {
      title: "Próxima Copa",
      text: "Quando será a próxima Copa do Mundo?"
    },
    {
      title: "Pelé nas Copas",
      text: "Quantos gols Pelé fez em Copas?"
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
      <h2 className="welcome-title">🏆 Bem-vindo ao World Cup Chat!</h2>
      <p className="welcome-subtitle">
        Sou seu assistente especializado em Copa do Mundo FIFA. Posso responder sobre história, 
        estatísticas, jogadores, países campeões e curiosidades das Copas do Mundo de 1930 a 2022.
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
          <Trophy size={20} color="#1f6feb" />
          Perguntas sobre Copa do Mundo
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
