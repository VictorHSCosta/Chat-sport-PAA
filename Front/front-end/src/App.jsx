import { Header, MessageList, ChatInput } from './components'
import { useChat, useChatEditor } from './hooks'
import './App.css'

function App() {
  const { messages, isTyping, messagesEndRef, sendMessage, apiStatus } = useChat()
  const { editor, handleSendMessage, handleKeyDown, setEditorContent } = useChatEditor(sendMessage)

  const handleExampleClick = (text) => {
    setEditorContent(text)
  }

  return (
    <div className="app">
      <Header apiStatus={apiStatus} />

      <div className="chat-container">
        <MessageList
          messages={messages}
          isTyping={isTyping}
          messagesEndRef={messagesEndRef}
          onExampleClick={handleExampleClick}
        />

        <ChatInput
          editor={editor}
          onSendMessage={handleSendMessage}
          onKeyDown={handleKeyDown}
          isTyping={isTyping}
        />
      </div>
    </div>
  )
}

export default App