import Message from './Message'
import TypingIndicator from './TypingIndicator'
import WelcomeMessage from './WelcomeMessage'

const MessageList = ({ 
  messages, 
  isTyping, 
  messagesEndRef, 
  onExampleClick 
}) => {
  return (
    <div className="messages-container">
      {messages.length === 0 ? (
        <WelcomeMessage onExampleClick={onExampleClick} />
      ) : (
        messages.map((message) => (
          <Message key={message.id} message={message} />
        ))
      )}
      
      {isTyping && <TypingIndicator />}
      
      <div ref={messagesEndRef} />
    </div>
  )
}

export default MessageList
