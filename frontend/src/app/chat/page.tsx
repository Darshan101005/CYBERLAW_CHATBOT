'use client'

import { useState, useRef, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import { Send, Sparkles, MessageCircle, Menu, LogOut, User, Plus, Trash2 } from 'lucide-react'

interface Message {
  id: string
  content: string
  is_user: boolean
  created_at: string
}

interface ChatSession {
  id: string
  title: string
  created_at: string
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSession, setCurrentSession] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [user, setUser] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const router = useRouter()

  useEffect(() => {
    checkUser()
    loadSessions()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const checkUser = async () => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) {
      router.push('/auth/login')
      return
    }
    setUser(user)
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadSessions = async () => {
    const { data, error } = await supabase
      .from('chat_sessions')
      .select('*')
      .order('updated_at', { ascending: false })

    if (data) {
      setSessions(data)
      if (data.length > 0 && !currentSession) {
        setCurrentSession(data[0].id)
        loadMessages(data[0].id)
      }
    }
  }

  const loadMessages = async (sessionId: string) => {
    const { data, error } = await supabase
      .from('messages')
      .select('*')
      .eq('session_id', sessionId)
      .order('created_at', { ascending: true })

    if (data) {
      setMessages(data)
    }
  }

  const createNewSession = async () => {
    const { data, error } = await supabase
      .from('chat_sessions')
      .insert({
        title: 'New Chat',
        user_id: user?.id
      })
      .select()
      .single()

    if (data) {
      setSessions([data, ...sessions])
      setCurrentSession(data.id)
      setMessages([])
    }
  }

  const deleteSession = async (sessionId: string) => {
    const { error } = await supabase
      .from('chat_sessions')
      .delete()
      .eq('id', sessionId)

    if (!error) {
      setSessions(sessions.filter(s => s.id !== sessionId))
      if (currentSession === sessionId) {
        const remainingSessions = sessions.filter(s => s.id !== sessionId)
        if (remainingSessions.length > 0) {
          setCurrentSession(remainingSessions[0].id)
          loadMessages(remainingSessions[0].id)
        } else {
          setCurrentSession(null)
          setMessages([])
        }
      }
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !currentSession) return

    const userMessage = {
      content: inputValue,
      is_user: true,
      session_id: currentSession
    }

    setIsLoading(true)
    const currentInput = inputValue
    setInputValue('')

    try {
      const { data: userMsg, error: userError } = await supabase
        .from('messages')
        .insert(userMessage)
        .select()
        .single()

      if (userMsg) {
        setMessages(prev => [...prev, userMsg])
      }

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentInput })
      })

      const { reply } = await response.json()

      const aiMessage = {
        content: reply,
        is_user: false,
        session_id: currentSession
      }

      const { data: aiMsg, error: aiError } = await supabase
        .from('messages')
        .insert(aiMessage)
        .select()
        .single()

      if (aiMsg) {
        setMessages(prev => [...prev, aiMsg])
      }

      const firstMessage = messages.length === 0
      if (firstMessage && currentInput.length > 0) {
        const sessionTitle = currentInput.length > 30 
          ? currentInput.substring(0, 30) + '...' 
          : currentInput

        await supabase
          .from('chat_sessions')
          .update({ title: sessionTitle })
          .eq('id', currentSession)

        setSessions(prev => 
          prev.map(s => 
            s.id === currentSession 
              ? { ...s, title: sessionTitle }
              : s
          )
        )
      }

    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/')
  }

  if (!user) {
    return <div className="min-h-screen bg-gradient-hero flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-400"></div>
    </div>
  }

  return (
    <div className="h-screen bg-gradient-hero flex">
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-80 bg-surface-200/90 backdrop-blur-xl border-r border-surface-400 shadow-2xl transform transition-transform duration-200 ease-in-out md:relative md:translate-x-0`}>
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-surface-400">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center shadow-lg">
                  <MessageCircle className="w-6 h-6 text-primary-50" />
                </div>
                <div>
                  <span className="font-bold text-primary-800 text-lg">CyberLaw AI</span>
                  <p className="text-primary-600 text-sm">Legal Assistant</p>
                </div>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="md:hidden p-2 text-primary-600 hover:text-primary-800 hover:bg-surface-300 rounded-lg transition-all"
              >
                ×
              </button>
            </div>
            <button
              onClick={createNewSession}
              className="w-full flex items-center justify-center space-x-2 bg-gradient-primary text-primary-50 px-4 py-3 rounded-xl hover:shadow-lg hover:scale-105 transition-all duration-200 font-medium"
            >
              <Plus className="w-4 h-4" />
              <span>New Chat</span>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-3">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`group flex items-center justify-between p-4 rounded-xl cursor-pointer transition-all duration-200 ${
                    currentSession === session.id
                      ? 'bg-surface-300/80 backdrop-blur-sm border border-surface-500 shadow-sm'
                      : 'hover:bg-surface-300/50 hover:backdrop-blur-sm'
                  }`}
                  onClick={() => {
                    setCurrentSession(session.id)
                    loadMessages(session.id)
                  }}
                >
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-primary-800 truncate mb-1">
                      {session.title}
                    </h3>
                    <p className="text-xs text-primary-600">
                      {new Date(session.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteSession(session.id)
                    }}
                    className="opacity-0 group-hover:opacity-100 p-2 text-primary-600 hover:text-primary-800 hover:bg-surface-400 rounded-lg transition-all"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 border-t border-surface-400">
            <div className="flex items-center space-x-3 p-3 bg-surface-300/60 backdrop-blur-sm rounded-xl border border-surface-400">
              <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center shadow-md">
                <User className="w-5 h-5 text-primary-50" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-primary-800 truncate">
                  {user?.email}
                </p>
                <p className="text-xs text-primary-600">Online</p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-primary-600 hover:text-primary-800 hover:bg-surface-400 rounded-lg transition-all"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <header className="bg-surface-200/90 backdrop-blur-xl border-b border-surface-400 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 text-primary-600 hover:text-primary-800 hover:bg-surface-300 rounded-lg transition-all"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center shadow-md">
                <Sparkles className="w-5 h-5 text-primary-50" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-primary-800">
                  CyberLaw Assistant
                </h1>
                <p className="text-sm text-primary-600">AI-powered legal guidance</p>
              </div>
            </div>
            <div className="w-8"></div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-20">
              <div className="w-20 h-20 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-2xl">
                <MessageCircle className="w-10 h-10 text-primary-50" />
              </div>
              <h2 className="text-2xl font-bold text-primary-800 mb-3">
                Welcome to CyberLaw AI
              </h2>
              <p className="text-primary-600 max-w-lg mx-auto leading-relaxed font-medium">
                Ask me anything about cybercrime laws, IT Act 2000, legal procedures, or get guidance on cybersecurity compliance. I'm here to help with your legal questions.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 max-w-2xl mx-auto">
                <div className="p-4 bg-surface-300/70 backdrop-blur-sm rounded-xl border border-surface-400">
                  <h3 className="font-semibold text-primary-800 mb-2">Cybercrime Laws</h3>
                  <p className="text-sm text-primary-600 font-medium">Learn about cybercrime provisions and penalties</p>
                </div>
                <div className="p-4 bg-surface-400/70 backdrop-blur-sm rounded-xl border border-surface-500">
                  <h3 className="font-semibold text-primary-800 mb-2">IT Act 2000</h3>
                  <p className="text-sm text-primary-600 font-medium">Understanding digital rights and regulations</p>
                </div>
                <div className="p-4 bg-primary-100/70 backdrop-blur-sm rounded-xl border border-primary-300">
                  <h3 className="font-semibold text-primary-800 mb-2">Legal Procedures</h3>
                  <p className="text-sm text-primary-600 font-medium">Step-by-step guidance for legal processes</p>
                </div>
                <div className="p-4 bg-primary-200/70 backdrop-blur-sm rounded-xl border border-primary-400">
                  <h3 className="font-semibold text-primary-800 mb-2">Compliance</h3>
                  <p className="text-sm text-primary-600 font-medium">Cybersecurity and data protection guidance</p>
                </div>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.is_user ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl px-6 py-4 rounded-2xl shadow-sm ${
                    message.is_user
                      ? 'bg-gradient-primary text-primary-50 shadow-lg border border-primary-400'
                      : 'bg-surface-300/80 backdrop-blur-sm border border-surface-400 text-primary-800'
                  }`}
                >
                  <p className={`leading-relaxed font-medium ${message.is_user ? 'text-primary-50' : 'text-primary-800'}`}>
                    {message.content}
                  </p>
                  <span
                    className={`text-xs mt-2 block ${
                      message.is_user ? 'text-primary-200' : 'text-primary-600'
                    }`}
                  >
                    {new Date(message.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-surface-300/80 backdrop-blur-sm border border-surface-400 px-6 py-4 rounded-2xl shadow-sm">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-6 bg-surface-200/90 backdrop-blur-xl border-t border-surface-400">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
              placeholder="Ask about cybercrime laws, IT Act, legal procedures..."
              className="flex-1 px-6 py-4 bg-primary-50/80 backdrop-blur-sm border border-primary-200 rounded-xl focus:ring-2 focus:ring-primary-400 focus:border-primary-400 outline-none transition-all text-primary-900 placeholder-primary-700"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim() || !currentSession}
              className="px-8 py-4 bg-gradient-primary text-primary-50 rounded-xl hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200 flex items-center space-x-2 font-medium"
            >
              <Send className="w-5 h-5" />
              <span className="hidden sm:block">Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}