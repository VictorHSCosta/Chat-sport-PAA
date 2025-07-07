import { EditorContent } from '@tiptap/react'
import { Send } from 'lucide-react'

const ChatInput = ({ 
  editor, 
  onSendMessage, 
  onKeyDown, 
  isTyping 
}) => {
  return (
    <div className="input-container">
      <div className="input-wrapper">
        <div className="editor-container">
          <div className="editor" onKeyDown={onKeyDown}>
            <EditorContent editor={editor} />
          </div>
          <div className="input-actions">
            <div style={{ fontSize: '0.875rem', color: '#8b949e' }}>
              {editor?.getText().length || 0}/1000
            </div>
            <button 
              className="send-button"
              onClick={onSendMessage}
              disabled={!editor?.getText().trim() || isTyping}
            >
              <Send size={16} />
              Enviar
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatInput
