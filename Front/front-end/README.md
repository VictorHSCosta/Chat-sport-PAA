# FootBot - Chat de Futebol

Um chatbot especializado em futebol desenvolvido com React + Vite, TipTap e tema escuro.

## 🚀 Características

- **Interface Moderna**: Design inspirado no ChatGPT com tema escuro
- **Editor Rico**: Utiliza TipTap para input avançado
- **Especializado em Futebol**: Base de conhecimento focada em futebol
- **Modular**: Arquitetura componentizada com hooks customizados
- **Responsivo**: Funciona em diferentes tamanhos de tela

## 📁 Estrutura do Projeto

```
src/
├── App.jsx                 # Componente principal
├── App.css                 # Estilos globais da aplicação
├── index.css               # Estilos base e reset CSS
├── main.jsx                # Ponto de entrada da aplicação
├── footballData.js         # Base de dados de futebol
├── components/             # Componentes reutilizáveis
│   ├── Header.jsx          # Cabeçalho da aplicação
│   ├── MessageList.jsx     # Lista de mensagens do chat
│   ├── Message.jsx         # Componente individual de mensagem
│   ├── ChatInput.jsx       # Input do chat com TipTap
│   ├── TypingIndicator.jsx # Indicador de digitação
│   ├── WelcomeMessage.jsx  # Mensagem de boas-vindas
│   └── index.js           # Barrel export dos componentes
├── hooks/                  # Hooks customizados
│   ├── useChat.js         # Gerenciamento do estado do chat
│   ├── useChatEditor.js   # Gerenciamento do editor TipTap
│   └── index.js           # Barrel export dos hooks
└── assets/                # Recursos estáticos
    └── react.svg
```

## 🎯 Componentes

### `<Header />`
Exibe o cabeçalho da aplicação com logo e título do FootBot.

### `<MessageList />`
Gerencia a exibição das mensagens do chat, incluindo:
- Mensagem de boas-vindas quando não há conversas
- Lista de mensagens do usuário e bot
- Indicador de digitação

### `<Message />`
Componente individual para cada mensagem, suportando:
- Mensagens do usuário (alinhadas à direita)
- Mensagens do bot (alinhadas à esquerda)
- Avatares diferenciados

### `<ChatInput />`
Input avançado usando TipTap com:
- Placeholder dinâmico
- Limite de 1000 caracteres
- Envio com Enter (Shift+Enter para nova linha)
- Contador de caracteres

### `<WelcomeMessage />`
Tela inicial com:
- Prompts de exemplo organizados por categoria
- Sugestões aleatórias da base de dados
- Interface interativa para começar conversas

### `<TypingIndicator />`
Animação de "digitando..." durante o processamento das respostas.

## 🪝 Hooks Customizados

### `useChat()`
Gerencia o estado principal do chat:
```jsx
const { messages, isTyping, messagesEndRef, sendMessage } = useChat()
```

**Retorna:**
- `messages`: Array de mensagens
- `isTyping`: Estado de carregamento
- `messagesEndRef`: Ref para scroll automático
- `sendMessage`: Função para enviar mensagens

### `useChatEditor(onSendMessage)`
Gerencia o editor TipTap:
```jsx
const { editor, handleSendMessage, handleKeyDown, setEditorContent } = useChatEditor(sendMessage)
```

**Parâmetros:**
- `onSendMessage`: Callback para envio de mensagens

**Retorna:**
- `editor`: Instância do editor TipTap
- `handleSendMessage`: Handler para botão de envio
- `handleKeyDown`: Handler para teclas (Enter/Shift+Enter)
- `setEditorContent`: Função para definir conteúdo do editor

## 🧠 Base de Conhecimento

O arquivo `footballData.js` contém:

- **Respostas Específicas**: Mapeamento de palavras-chave para respostas detalhadas
- **FAQ**: Perguntas frequentes com respostas completas
- **Fatos Curiosos**: Array de curiosidades do futebol
- **Sugestões**: Lista de perguntas sugeridas

## 🚀 Scripts Disponíveis

```bash
# Instalar dependências
pnpm install

# Desenvolvimento
pnpm dev

# Build para produção
pnpm build

# Lint
pnpm lint

# Preview do build
pnpm preview
```

## 📦 Dependências Principais

- **React 18**: Library principal
- **TipTap**: Editor rico de texto
- **Lucide React**: Ícones
- **Vite**: Bundler e dev server
- **Tailwind CSS**: Framework CSS
