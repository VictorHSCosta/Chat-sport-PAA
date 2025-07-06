import { useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'

export const useChatEditor = (onSendMessage) => {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: false,
        bold: false,
        italic: false,
        code: false,
        codeBlock: false,
        blockquote: false,
        horizontalRule: false,
        bulletList: false,
        orderedList: false,
        listItem: false,
      }),
      Placeholder.configure({
        placeholder: 'Pergunte sobre futebol... (Ex: Quando foi a última Copa do Mundo?)',
      }),
    ],
    editorProps: {
      attributes: {
        class: 'editor-content',
      },
    },
    onUpdate: ({ editor }) => {
      // Limita a 1000 caracteres
      const text = editor.getText()
      if (text.length > 1000) {
        const limitedText = text.substring(0, 1000)
        editor.commands.setContent(`<p>${limitedText}</p>`)
        editor.commands.focus('end')
      }
    },
  })

  const handleSendMessage = () => {
    if (!editor) return
    
    const content = editor.getText().trim()
    if (!content) return

    onSendMessage(content)
    editor.commands.clearContent()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const setEditorContent = (text) => {
    if (editor) {
      editor.commands.setContent(`<p>${text}</p>`)
      editor.commands.focus('end')
    }
  }

  return {
    editor,
    handleSendMessage,
    handleKeyDown,
    setEditorContent
  }
}
