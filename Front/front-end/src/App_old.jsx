import { useState, useRef, useEffect } from 'react'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { Send, Bot, User, Sparkles } from 'lucide-react'
import { getFootballResponse, suggestedQuestions } from './footballData.js'
import './App.css'

// Mock API para simular respostas do bot
const mockFootballAPI = {
  async getResponse(message) {
    // Simula delay da API (1-3 segundos)
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
    
    return getFootballResponse(message)
  }
}

function App() {
  const [messages, setMessages] = useState([])
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: false,
        bold: false,
        italic: false,
        code: false,
        codeBlock: false,
        blockquote: false,
        horizontalRule: false,
        bulletList: false,
        orderedList: false,
        listItem: false,
      }),
      Placeholder.configure({
        placeholder: 'Pergunte sobre futebol... (Ex: Quando foi a última Copa do Mundo?)',
      }),
    ],
    editorProps: {
      attributes: {
        class: 'editor-content',
      },
    },
    onUpdate: ({ editor }) => {
      // Limita a 1000 caracteres
      const text = editor.getText()
      if (text.length > 1000) {
        const limitedText = text.substring(0, 1000)
        editor.commands.setContent(`<p>${limitedText}</p>`)
        editor.commands.focus('end')
      }
    },
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const sendMessage = async () => {
    if (!editor) return
    
    const content = editor.getText().trim()
    if (!content) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: content,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    editor.commands.clearContent()
    setIsTyping(true)

    try {
      const response = await mockFootballAPI.getResponse(content)
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Desculpe, houve um erro ao processar sua pergunta. Tente novamente.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleExampleClick = (text) => {
    if (editor) {
      editor.commands.setContent(`<p>${text}</p>`)
      editor.commands.focus('end')
    }
  }

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
    <div className="app">
      <header className="header">
        <Bot size={24} color="#1f6feb" />
        <div>
          <h1 className="header-title">FootBot</h1>
          <p className="header-subtitle">Seu assistente especializado em futebol</p>
        </div>
      </header>

      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 ? (
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
                    onClick={() => handleExampleClick(prompt.text)}
                  >
                    <div className="example-prompt-title">{prompt.title}</div>
                    <div className="example-prompt-text">{prompt.text}</div>
                  </div>
                ))}
              </div>

              <div style={{ marginTop: '2rem' }}>
                <h3 style={{ color: '#f0f6fc', fontSize: '1.1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
                  <Sparkles size={20} color="#1f6feb" />
                  Sugestões Aleatórias
                </h3>
                <div className="random-suggestions">
                  {randomSuggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      className="suggestion-button"
                      onClick={() => handleExampleClick(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className={`message-avatar ${message.type}`}>
                  {message.type === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className="message-content">
                  {message.content}
                </div>
              </div>
            ))
          )}
          
          {isTyping && (
            <div className="message bot">
              <div className="message-avatar bot">
                <Bot size={16} />
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  FootBot está digitando
                  <div className="typing-dots">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <div className="editor-container">
              <div className="editor" onKeyDown={handleKeyDown}>
                <EditorContent editor={editor} />
              </div>
              <div className="input-actions">
                <div style={{ fontSize: '0.875rem', color: '#8b949e' }}>
                  {editor?.getText().length || 0}/1000
                </div>
                <button 
                  className="send-button"
                  onClick={sendMessage}
                  disabled={!editor?.getText().trim() || isTyping}
                >
                  <Send size={16} />
                  Enviar
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
