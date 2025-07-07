import { Bot, User } from 'lucide-react'

const Message = ({ message }) => {
  return (
    <div className={`message ${message.type}`}>
      <div className={`message-avatar ${message.type}`}>
        {message.type === 'user' ? <User size={16} /> : <Bot size={16} />}
      </div>
      <div className="message-content">
        {message.content}
      </div>
    </div>
  )
}

export default Message
