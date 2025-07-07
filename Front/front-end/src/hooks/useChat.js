import { useState, useRef, useEffect } from 'react'
import { getFootballResponse } from '../footballData.js'

// Mock API para simular respostas do bot
const mockFootballAPI = {
  async getResponse(message) {
    // Simula delay da API (1-3 segundos)
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))
    
    return getFootballResponse(message)
  }
}

export const useChat = () => {
  const [messages, setMessages] = useState([])
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const sendMessage = async (content) => {
    if (!content?.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
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

  return {
    messages,
    isTyping,
    messagesEndRef,
    sendMessage
  }
}
