import { Bot } from 'lucide-react'

const TypingIndicator = () => {
  return (
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
  )
}

export default TypingIndicator
