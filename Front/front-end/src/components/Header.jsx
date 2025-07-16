import { Trophy, Wifi, WifiOff, Loader2 } from 'lucide-react'

const Header = ({ apiStatus }) => {
  const getStatusIcon = () => {
    switch (apiStatus) {
      case 'healthy':
        return <Wifi size={16} color="#28a745" />
      case 'unhealthy':
        return <WifiOff size={16} color="#dc3545" />
      case 'checking':
        return <Loader2 size={16} color="#6c757d" className="animate-spin" />
      default:
        return null
    }
  }

  const getStatusText = () => {
    switch (apiStatus) {
      case 'healthy':
        return 'Online'
      case 'unhealthy':
        return 'Offline'
      case 'checking':
        return 'Verificando...'
      default:
        return ''
    }
  }

  return (
    <header className="header">
      <Trophy size={24} color="#1f6feb" />
      <div>
        <h1 className="header-title">World Cup Chat</h1>
        <p className="header-subtitle">Seu assistente especializado em Copa do Mundo FIFA</p>
      </div>
      <div className="api-status">
        {getStatusIcon()}
        <span className="status-text">{getStatusText()}</span>
      </div>
    </header>
  )
}

export default Header
