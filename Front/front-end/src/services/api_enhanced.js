// Configuração para alternar entre diferentes modos da API
export const API_MODES = {
  LANGCHAIN: {
    name: 'LangChain + Ollama',
    baseURL: 'http://localhost:8000',
    description: 'Modo original com RAG avançado e Ollama local',
    features: ['RAG completo', 'Embeddings locais', 'FAISS', 'Ollama']
  },
  LLAMA_INDEX: {
    name: 'LlamaIndex + Groq',
    baseURL: 'http://localhost:8000',
    description: 'Modo novo com LlamaIndex e Groq Cloud',
    features: ['Template direto', 'Groq Cloud', 'llama3-70b-8192', 'Mais rápido']
  }
}

// Modo padrão (pode ser alterado via variável de ambiente ou aqui)
export const DEFAULT_MODE = 'LLAMA_INDEX'

// Configuração atual baseada no modo
export const getCurrentMode = () => {
  // Permitir override via localStorage para desenvolvimento
  const savedMode = localStorage.getItem('api_mode')
  if (savedMode && API_MODES[savedMode]) {
    return savedMode
  }
  
  // Usar modo padrão
  return DEFAULT_MODE
}

export const setMode = (mode) => {
  if (!API_MODES[mode]) {
    throw new Error(`Modo inválido: ${mode}`)
  }
  localStorage.setItem('api_mode', mode)
  // Recarregar página para aplicar mudanças
  window.location.reload()
}

export const getModeConfig = (mode = null) => {
  if (!mode) {
    mode = getCurrentMode()
  }
  return API_MODES[mode] || API_MODES[DEFAULT_MODE]
}

// Configuração da API baseada no modo atual
const currentModeConfig = getModeConfig()

export const API_CONFIG = {
  baseURL: currentModeConfig.baseURL,
  mode: getCurrentMode(),
  endpoints: {
    chat: '/chat',
    health: '/health',
    root: '/',
    status: '/status'
  },
  timeout: 300000, // 5 minutos para consultas complexas
  retries: 3
}

export class FootballAPI {
  constructor() {
    this.baseURL = API_CONFIG.baseURL
    this.mode = API_CONFIG.mode
    this.currentModeConfig = getModeConfig()
  }

  async sendMessage(message) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout)

      const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.chat}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        credentials: 'omit',
        body: JSON.stringify({
          message: message
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Erro na comunicação com o servidor')
      }

      const data = await response.json()
      return {
        answer: data.answer,
        success: data.success,
        message: data.message,
        mode: this.mode
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Timeout: Resposta muito lenta. Verifique se o servidor está rodando em http://localhost:8000')
      }
      console.error('Erro na API:', error)
      throw new Error(`Erro de conexão: ${error.message}`)
    }
  }

  async checkHealth() {
    try {
      const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.health}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        credentials: 'omit',
      })

      if (!response.ok) {
        return { status: 'unhealthy', message: 'API não respondeu' }
      }

      const data = await response.json()
      return {
        status: data.status,
        message: data.message,
        mode: this.mode
      }
    } catch (error) {
      console.error('Erro ao verificar saúde da API:', error)
      return { status: 'unhealthy', message: error.message, mode: this.mode }
    }
  }

  async getApiInfo() {
    try {
      const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.root}`)
      const data = await response.json()
      return {
        ...data,
        frontend_mode: this.mode,
        mode_config: this.currentModeConfig
      }
    } catch (error) {
      console.error('Erro ao obter informações da API:', error)
      return null
    }
  }

  async getStatus() {
    try {
      const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.status}`)
      const data = await response.json()
      return {
        ...data,
        frontend_mode: this.mode,
        mode_config: this.currentModeConfig
      }
    } catch (error) {
      console.error('Erro ao obter status da API:', error)
      return null
    }
  }

  // Método para alternar modo
  switchMode(newMode) {
    setMode(newMode)
  }

  // Método para obter modos disponíveis
  getAvailableModes() {
    return API_MODES
  }
}

export const footballAPI = new FootballAPI()

// Utilitários para debug
export const DEBUG = {
  getCurrentMode,
  setMode,
  getModeConfig,
  API_MODES,
  switchMode: (mode) => footballAPI.switchMode(mode),
  logCurrentConfig: () => {
    console.log('🔧 Configuração atual da API:')
    console.log(`   Modo: ${getCurrentMode()}`)
    console.log(`   URL: ${API_CONFIG.baseURL}`)
    console.log(`   Config:`, getModeConfig())
  }
}

// Log automático no desenvolvimento
if (import.meta.env.DEV) {
  console.log('🚀 Chat Sport PAA - API Client')
  DEBUG.logCurrentConfig()
}
