export const API_CONFIG = {
  baseURL: 'http://localhost:8000',
  fastURL: 'http://localhost:8001',
  useFastAPI: false,
  endpoints: {
    chat: '/chat',
    health: '/health',
    root: '/'
  },
  timeout: 150000
}

export class FootballAPI {
  constructor() {
    this.baseURL = API_CONFIG.useFastAPI ? API_CONFIG.fastURL : API_CONFIG.baseURL
  }

  async sendMessage(message) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout)

      const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.chat}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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
        message: data.message
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Timeout: A resposta está demorando muito. Tente novamente.')
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
        }
      })

      if (!response.ok) {
        return { status: 'unhealthy', message: 'API não respondeu' }
      }

      const data = await response.json()
      return {
        status: data.status,
        message: data.message
      }
    } catch (error) {
      console.error('Erro ao verificar saúde da API:', error)
      return { status: 'unhealthy', message: error.message }
    }
  }

  async getApiInfo() {
    try {
      const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.root}`)
      const data = await response.json()
      return data
    } catch (error) {
      console.error('Erro ao obter informações da API:', error)
      return null
    }
  }
}

export const footballAPI = new FootballAPI()
