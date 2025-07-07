import { Bot } from 'lucide-react'

const Header = () => {
  return (
    <header className="header">
      <Bot size={24} color="#1f6feb" />
      <div>
        <h1 className="header-title">FootBot</h1>
        <p className="header-subtitle">Seu assistente especializado em futebol</p>
      </div>
    </header>
  )
}

export default Header
