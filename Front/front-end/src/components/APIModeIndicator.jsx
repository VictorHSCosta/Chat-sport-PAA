import React, { useState, useEffect } from 'react'
import { footballAPI, API_MODES, getCurrentMode, DEBUG } from '../services/api_enhanced'

export const APIModeIndicator = () => {
  const [apiInfo, setApiInfo] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    loadApiInfo()
  }, [])

  const loadApiInfo = async () => {
    try {
      setIsLoading(true)
      const [info, status] = await Promise.all([
        footballAPI.getApiInfo(),
        footballAPI.getStatus()
      ])
      setApiInfo({ ...info, ...status })
    } catch (error) {
      console.error('Erro ao carregar info da API:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const currentMode = getCurrentMode()
  const modeConfig = API_MODES[currentMode]

  if (isLoading) {
    return (
      <div className="api-mode-indicator loading">
        <div className="indicator-dot loading"></div>
        <span>Carregando...</span>
      </div>
    )
  }

  const getStatusColor = () => {
    if (!apiInfo) return 'red'
    if (apiInfo.status === 'healthy' || apiInfo.llm_ready) return 'green'
    return 'orange'
  }

  const getStatusIcon = () => {
    const color = getStatusColor()
    if (color === 'green') return '✅'
    if (color === 'orange') return '⚠️'
    return '❌'
  }

  return (
    <div className="api-mode-indicator">
      <div 
        className="mode-summary"
        onClick={() => setShowDetails(!showDetails)}
        style={{ cursor: 'pointer' }}
      >
        <div className={`indicator-dot ${getStatusColor()}`}></div>
        <span className="mode-name">
          {getStatusIcon()} {modeConfig?.name || 'Desconhecido'}
        </span>
        <span className="toggle-icon">
          {showDetails ? '▼' : '▶'}
        </span>
      </div>

      {showDetails && (
        <div className="mode-details">
          {apiInfo && (
            <>
              <div className="detail-section">
                <h4>🔧 Configuração Atual</h4>
                <ul>
                  <li><strong>Modo:</strong> {apiInfo.frontend_mode}</li>
                  <li><strong>Backend:</strong> {apiInfo.description || 'N/A'}</li>
                  <li><strong>Modelo:</strong> {apiInfo.llm_model || 'N/A'}</li>
                  <li><strong>Provider:</strong> {apiInfo.provider || 'N/A'}</li>
                  <li><strong>Framework:</strong> {apiInfo.framework || 'N/A'}</li>
                  <li><strong>Versão:</strong> {apiInfo.version || 'N/A'}</li>
                </ul>
              </div>

              {apiInfo.model_config && (
                <div className="detail-section">
                  <h4>⚙️ Configuração do Modelo</h4>
                  <ul>
                    <li><strong>Abordagem:</strong> {apiInfo.model_config.approach}</li>
                    <li><strong>Idioma:</strong> {apiInfo.model_config.language}</li>
                    <li><strong>Anti-alucinação:</strong> {apiInfo.model_config.anti_hallucination ? '✅' : '❌'}</li>
                    <li><strong>Dados only:</strong> {apiInfo.model_config.data_only ? '✅' : '❌'}</li>
                  </ul>
                </div>
              )}

              {apiInfo.data_sources && (
                <div className="detail-section">
                  <h4>📊 Fontes de Dados</h4>
                  <ul>
                    {Object.entries(apiInfo.data_sources).map(([key, value]) => (
                      <li key={key}>
                        <strong>{key}:</strong> {value}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="detail-section">
                <h4>🚀 URLs</h4>
                <ul>
                  <li><strong>API:</strong> <a href={footballAPI.baseURL} target="_blank" rel="noopener noreferrer">{footballAPI.baseURL}</a></li>
                  <li><strong>Docs:</strong> <a href={`${footballAPI.baseURL}/docs`} target="_blank" rel="noopener noreferrer">{footballAPI.baseURL}/docs</a></li>
                  <li><strong>Health:</strong> <a href={`${footballAPI.baseURL}/health`} target="_blank" rel="noopener noreferrer">{footballAPI.baseURL}/health</a></li>
                </ul>
              </div>

              <div className="detail-actions">
                <button onClick={loadApiInfo} className="refresh-btn">
                  🔄 Atualizar
                </button>
                <button onClick={() => DEBUG.logCurrentConfig()} className="debug-btn">
                  🐛 Log Config
                </button>
              </div>
            </>
          )}
        </div>
      )}

      <style jsx>{`
        .api-mode-indicator {
          position: fixed;
          top: 10px;
          right: 10px;
          background: rgba(0, 0, 0, 0.8);
          color: white;
          border-radius: 8px;
          padding: 8px 12px;
          font-size: 12px;
          z-index: 1000;
          max-width: 400px;
          backdrop-filter: blur(10px);
        }

        .mode-summary {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .indicator-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          display: inline-block;
        }

        .indicator-dot.green {
          background-color: #4CAF50;
          box-shadow: 0 0 6px #4CAF50;
        }

        .indicator-dot.orange {
          background-color: #FF9800;
          box-shadow: 0 0 6px #FF9800;
        }

        .indicator-dot.red {
          background-color: #F44336;
          box-shadow: 0 0 6px #F44336;
        }

        .indicator-dot.loading {
          background-color: #2196F3;
          animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .mode-name {
          font-weight: bold;
          flex: 1;
        }

        .toggle-icon {
          font-size: 10px;
          opacity: 0.7;
        }

        .mode-details {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid rgba(255, 255, 255, 0.2);
        }

        .detail-section {
          margin-bottom: 12px;
        }

        .detail-section h4 {
          margin: 0 0 6px 0;
          font-size: 11px;
          color: #FFD700;
        }

        .detail-section ul {
          margin: 0;
          padding-left: 16px;
          font-size: 10px;
          opacity: 0.9;
        }

        .detail-section li {
          margin-bottom: 2px;
        }

        .detail-actions {
          display: flex;
          gap: 6px;
          margin-top: 8px;
        }

        .detail-actions button {
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 10px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .detail-actions button:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .detail-section a {
          color: #64B5F6;
          text-decoration: none;
        }

        .detail-section a:hover {
          text-decoration: underline;
        }

        @media (max-width: 768px) {
          .api-mode-indicator {
            position: relative;
            top: auto;
            right: auto;
            margin: 10px;
            max-width: none;
          }
        }
      `}</style>
    </div>
  )
}

export default APIModeIndicator
