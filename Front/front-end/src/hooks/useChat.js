import { useState, useRef, useEffect } from 'react'
import { footballAPI } from '../services/api'

export const useChat = () => {
  const [messages, setMessages] = useState([])
  const [isTyping, setIsTyping] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  useEffect(() => {
    const checkApiHealth = async () => {
      const healthData = await footballAPI.checkHealth()
      setApiStatus(healthData.status === 'healthy' ? 'healthy' : 'unhealthy')
    }
    
    checkApiHealth()
    
    const interval = setInterval(checkApiHealth, 30000)
    return () => clearInterval(interval)
  }, [])

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
      console.log('🚀 Enviando para API:', content)
      
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Timeout: Resposta muito lenta')), 25000)
      )
      
      const apiPromise = footballAPI.sendMessage(content)
      
      const responseData = await Promise.race([apiPromise, timeoutPromise])
      console.log('✅ Resposta da API recebida:', responseData)
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `${responseData.message.includes('cache') ? '⚡' : '�'} **${responseData.message.includes('cache') ? 'Resposta Rápida' : 'Resposta via Ollama'}**: ${responseData.answer}`,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
      setApiStatus('healthy')
    } catch (error) {
      console.error('❌ Erro ao enviar mensagem:', error)
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `❌ **Erro na API**: ${error.message}. Verifique se o servidor está rodando em http://localhost:8000`,
        timestamp: new Date(),
        isError: true
      }

      setMessages(prev => [...prev, errorMessage])
      setApiStatus('unhealthy')
    } finally {
      setIsTyping(false)
    }
  }

  return {
    messages,
    isTyping,
    messagesEndRef,
    sendMessage,
    apiStatus
  }
}
