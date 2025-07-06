# Guia de Uso dos Componentes e Hooks

## 🎯 Como Usar os Hooks

### `useChat`

Hook principal para gerenciar o estado do chat.

```jsx
import { useChat } from './hooks'

function MeuComponente() {
  const { messages, isTyping, messagesEndRef, sendMessage } = useChat()

  // Enviar uma mensagem
  const handleSendMessage = () => {
    sendMessage("Qual time ganhou a Copa de 2022?")
  }

  return (
    <div>
      {/* Renderizar mensagens */}
      {messages.map(message => (
        <div key={message.id}>{message.content}</div>
      ))}
      
      {/* Elemento para scroll automático */}
      <div ref={messagesEndRef} />
      
      {/* Mostrar loading */}
      {isTyping && <div>Digitando...</div>}
    </div>
  )
}
```

### `useChatEditor`

Hook para gerenciar o editor TipTap.

```jsx
import { useChatEditor } from './hooks'

function MeuInput() {
  const { messages, sendMessage } = useChat()
  const { 
    editor, 
    handleSendMessage, 
    handleKeyDown, 
    setEditorContent 
  } = useChatEditor(sendMessage)

  // Definir conteúdo programaticamente
  const preencherInput = () => {
    setEditorContent("Quem é o maior jogador de todos os tempos?")
  }

  return (
    <div>
      {/* Editor TipTap */}
      <div onKeyDown={handleKeyDown}>
        <EditorContent editor={editor} />
      </div>
      
      {/* Botão de envio */}
      <button onClick={handleSendMessage}>
        Enviar
      </button>
      
      {/* Botão para preencher */}
      <button onClick={preencherInput}>
        Pergunta Exemplo
      </button>
    </div>
  )
}
```

## 🧩 Como Usar os Componentes

### `<Header />`

Componente simples sem props.

```jsx
import { Header } from './components'

function App() {
  return (
    <div>
      <Header />
      {/* resto da aplicação */}
    </div>
  )
}
```

### `<MessageList />`

Lista de mensagens com props obrigatórias.

```jsx
import { MessageList } from './components'
import { useChat } from './hooks'

function ChatArea() {
  const { messages, isTyping, messagesEndRef } = useChat()

  const handleExampleClick = (text) => {
    console.log("Exemplo clicado:", text)
  }

  return (
    <MessageList
      messages={messages}
      isTyping={isTyping}
      messagesEndRef={messagesEndRef}
      onExampleClick={handleExampleClick}
    />
  )
}
```

### `<Message />`

Componente individual de mensagem.

```jsx
import { Message } from './components'

function MeuChat() {
  const mensagem = {
    id: 1,
    type: 'user', // ou 'bot'
    content: 'Olá, FootBot!',
    timestamp: new Date()
  }

  return (
    <div>
      <Message message={mensagem} />
    </div>
  )
}
```

### `<ChatInput />`

Input com editor TipTap.

```jsx
import { ChatInput } from './components'
import { useChat, useChatEditor } from './hooks'

function MinhaArea() {
  const { sendMessage } = useChat()
  const { editor, handleSendMessage, handleKeyDown } = useChatEditor(sendMessage)
  const [isTyping, setIsTyping] = useState(false)

  return (
    <ChatInput
      editor={editor}
      onSendMessage={handleSendMessage}
      onKeyDown={handleKeyDown}
      isTyping={isTyping}
    />
  )
}
```

### `<WelcomeMessage />`

Mensagem de boas-vindas com exemplos.

```jsx
import { WelcomeMessage } from './components'

function TelaInicial() {
  const handleExampleClick = (texto) => {
    console.log("Exemplo selecionado:", texto)
    // Aqui você pode definir o texto no editor
  }

  return (
    <WelcomeMessage onExampleClick={handleExampleClick} />
  )
}
```

### `<TypingIndicator />`

Indicador de digitação simples.

```jsx
import { TypingIndicator } from './components'

function MeuChat() {
  const [isTyping, setIsTyping] = useState(true)

  return (
    <div>
      {isTyping && <TypingIndicator />}
    </div>
  )
}
```

## 🔧 Customização

### Estendendo a Base de Dados

Para adicionar mais respostas no `footballData.js`:

```javascript
// footballData.js
export const footballData = {
  responses: {
    // Adicionar nova categoria
    'mundial de clubes': [
      "Nova resposta sobre Mundial de Clubes...",
      "Outra resposta alternativa..."
    ],
    
    // Adicionar novo jogador
    'neymar': [
      "Informações sobre Neymar...",
      "Estatísticas do Neymar..."
    ]
  },
  
  // Adicionar novos fatos
  facts: [
    ...footballData.facts,
    "Novo fato curioso sobre futebol..."
  ],

  // Adicionar novas perguntas sugeridas
  faq: {
    ...footballData.faq,
    "nova pergunta": "Nova resposta detalhada..."
  }
}
```

### Criando Novos Componentes

Para criar um novo componente seguindo o padrão:

```jsx
// components/NovoComponente.jsx
const NovoComponente = ({ prop1, prop2, onCallback }) => {
  return (
    <div className="novo-componente">
      {/* seu conteúdo */}
    </div>
  )
}

export default NovoComponente
```

Não esqueça de exportar no `components/index.js`:

```javascript
// components/index.js
export { default as NovoComponente } from './NovoComponente'
```

### Criando Novos Hooks

Para criar um novo hook:

```jsx
// hooks/useNovoHook.js
import { useState, useEffect } from 'react'

export const useNovoHook = (parametro) => {
  const [estado, setEstado] = useState(null)

  useEffect(() => {
    // lógica do hook
  }, [parametro])

  const funcaoHelper = () => {
    // função auxiliar
  }

  return {
    estado,
    setEstado,
    funcaoHelper
  }
}
```

E exportar no `hooks/index.js`:

```javascript
// hooks/index.js
export { useNovoHook } from './useNovoHook'
```

## 🚀 Exemplo de Integração Completa

```jsx
// App.jsx - Exemplo de uso completo
import { Header, MessageList, ChatInput } from './components'
import { useChat, useChatEditor } from './hooks'
import './App.css'

function App() {
  // Hooks principais
  const { messages, isTyping, messagesEndRef, sendMessage } = useChat()
  const { editor, handleSendMessage, handleKeyDown, setEditorContent } = useChatEditor(sendMessage)

  // Handler para exemplos
  const handleExampleClick = (text) => {
    setEditorContent(text)
  }

  return (
    <div className="app">
      <Header />
      
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
```

Este guia mostra como cada peça se encaixa no sistema modular do FootBot. A arquitetura facilita a manutenção, teste e extensão da aplicação.
