'use client'

import { useState, useRef, useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import { Send, Sparkles, MessageCircle, Menu, LogOut, User, Plus, Trash2, Edit3, Check, X, Paperclip, Upload, FileText } from 'lucide-react'
import NewsNotification from '@/components/NewsNotification'
import ChatMessage from '@/components/ChatMessage'

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
  const [editingSession, setEditingSession] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [uploadedFileName, setUploadedFileName] = useState<string>('')
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
      return data.id
    }
    return null
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

  const updateSessionTitle = async (sessionId: string, newTitle: string) => {
    try {
      const { error } = await supabase
        .from('chat_sessions')
        .update({ title: newTitle.trim() })
        .eq('id', sessionId)

      if (error) throw error

      setSessions(sessions.map(s => 
        s.id === sessionId ? { ...s, title: newTitle.trim() } : s
      ))
      setEditingSession(null)
      setEditingTitle('')
    } catch (error) {
      console.error('Error updating session title:', error)
    }
  }

  const startEditing = (sessionId: string, currentTitle: string) => {
    setEditingSession(sessionId)
    setEditingTitle(currentTitle)
  }

  const cancelEditing = () => {
    setEditingSession(null)
    setEditingTitle('')
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Check file type (allow common document formats)
      const allowedTypes = [
        'application/pdf',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png',
        'image/gif'
      ]
      
      if (allowedTypes.includes(file.type)) {
        setSelectedFile(file)
        setUploadedFileName(file.name)
        setShowFileUpload(false)
      } else {
        alert('Please select a valid file type (PDF, DOC, DOCX, TXT, JPG, PNG, GIF)')
      }
    }
  }

  const removeSelectedFile = () => {
    setSelectedFile(null)
    setUploadedFileName('')
  }

  const toggleFileUpload = () => {
    setShowFileUpload(!showFileUpload)
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    // Create a session if none exists
    let sessionId = currentSession
    if (!sessionId) {
      sessionId = await createNewSession()
      if (!sessionId) return // If session creation failed, abort
    }

    const userMessage = {
      content: selectedFile ? `${inputValue}\n\n📎 Attached file: ${uploadedFileName}` : inputValue,
      is_user: true,
      session_id: sessionId
    }

    setIsLoading(true)
    const currentInput = inputValue
    const currentFile = selectedFile
    setInputValue('')
    
    // Clear file after sending
    if (selectedFile) {
      removeSelectedFile()
    }

    try {
      const { data: userMsg, error: userError } = await supabase
        .from('messages')
        .insert(userMessage)
        .select()
        .single()

      if (userMsg) {
        setMessages(prev => [...prev, userMsg])
      }

      // Prepare request body with file if present
      let requestBody: any = { message: currentInput }
      
      if (currentFile) {
        // Convert file to base64 for API transmission
        const reader = new FileReader()
        const fileData = await new Promise<string>((resolve) => {
          reader.onload = () => resolve(reader.result as string)
          reader.readAsDataURL(currentFile)
        })
        
        requestBody = {
          message: currentInput,
          file: {
            name: currentFile.name,
            type: currentFile.type,
            data: fileData,
            size: currentFile.size
          }
        }
      }

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
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
      <div className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-80 bg-white/95 backdrop-blur-xl border-r border-primary-200 shadow-2xl transform transition-transform duration-200 ease-in-out md:relative md:translate-x-0`}>
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-primary-200">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center shadow-lg">
                  <MessageCircle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <span className="font-bold text-primary-700 text-lg">Cyberlex</span>
                  <p className="text-primary-600 text-sm">Legal Assistant</p>
                </div>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="md:hidden p-2 text-primary-600 hover:text-primary-800 hover:bg-primary-50 rounded-lg transition-all"
              >
                ×
              </button>
            </div>
            <button
              onClick={createNewSession}
              className="w-full flex items-center justify-center space-x-2 bg-gradient-primary text-white px-4 py-3 rounded-xl hover:shadow-lg hover:scale-105 transition-all duration-200 font-medium"
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
                  className={`group flex items-center justify-between p-4 rounded-xl transition-all duration-200 ${
                    currentSession === session.id
                      ? 'bg-gradient-to-r from-white to-primary-50 backdrop-blur-sm border border-primary-200 shadow-sm'
                      : 'hover:bg-primary-50/50 hover:backdrop-blur-sm'
                  } ${editingSession === session.id ? 'cursor-default' : 'cursor-pointer'}`}
                  onClick={() => {
                    if (editingSession !== session.id) {
                      setCurrentSession(session.id)
                      loadMessages(session.id)
                    }
                  }}
                >
                  <div className="flex-1 min-w-0">
                    {editingSession === session.id ? (
                      <div className="flex items-center space-x-2">
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              updateSessionTitle(session.id, editingTitle)
                            } else if (e.key === 'Escape') {
                              cancelEditing()
                            }
                          }}
                          className="flex-1 text-sm font-semibold text-primary-800 bg-transparent border-b border-primary-300 focus:border-primary-500 outline-none"
                          autoFocus
                        />
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            updateSessionTitle(session.id, editingTitle)
                          }}
                          className="p-1 text-green-600 hover:text-green-800 hover:bg-green-100 rounded transition-all"
                        >
                          <Check className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            cancelEditing()
                          }}
                          className="p-1 text-red-600 hover:text-red-800 hover:bg-red-100 rounded transition-all"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ) : (
                      <h3 className="text-sm font-semibold text-primary-800 truncate mb-1">
                        {session.title}
                      </h3>
                    )}
                    <p className="text-xs text-primary-600">
                      {new Date(session.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  {editingSession !== session.id && (
                    <div className="flex space-x-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          startEditing(session.id, session.title)
                        }}
                        className="opacity-0 group-hover:opacity-100 p-2 text-primary-600 hover:text-primary-800 hover:bg-primary-100 rounded-lg transition-all"
                        title="Edit thread name"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteSession(session.id)
                        }}
                        className="opacity-0 group-hover:opacity-100 p-2 text-primary-600 hover:text-primary-800 hover:bg-primary-100 rounded-lg transition-all"
                        title="Delete thread"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 border-t border-primary-200">
            <div className="flex items-center space-x-3 p-3 bg-gradient-to-r from-white to-primary-50 backdrop-blur-sm rounded-xl border border-primary-200">
              <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center shadow-md">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-primary-800 truncate">
                  {user?.email}
                </p>
                <p className="text-xs text-primary-600">Online</p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-primary-600 hover:text-primary-800 hover:bg-primary-100 rounded-lg transition-all"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <header className="bg-white/95 backdrop-blur-xl border-b border-primary-200 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 text-primary-600 hover:text-primary-800 hover:bg-primary-50 rounded-lg transition-all"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center shadow-md">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-primary-800">
                  Cyberlex Assistant
                </h1>
                <p className="text-sm text-primary-600">AI-powered legal guidance</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <NewsNotification />
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="text-center py-20">
              <div className="w-20 h-20 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-2xl">
                <MessageCircle className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-primary-800 mb-3">
                Welcome to Cyberlex
              </h2>
              <p className="text-primary-600 max-w-lg mx-auto leading-relaxed font-medium">
                Ask me anything about cybercrime laws, IT Act 2000, legal procedures, or get guidance on cybersecurity compliance. I'm here to help with your legal questions.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 max-w-2xl mx-auto">
                <div className="p-4 bg-gradient-to-br from-white to-primary-50 backdrop-blur-sm rounded-xl border border-primary-200">
                  <h3 className="font-semibold text-primary-800 mb-2">Cybercrime Laws</h3>
                  <p className="text-sm text-primary-600 font-medium">Learn about cybercrime provisions and penalties</p>
                </div>
                <div className="p-4 bg-gradient-to-br from-white to-primary-100 backdrop-blur-sm rounded-xl border border-primary-200">
                  <h3 className="font-semibold text-primary-800 mb-2">IT Act 2000</h3>
                  <p className="text-sm text-primary-600 font-medium">Understanding digital rights and regulations</p>
                </div>
                <div className="p-4 bg-gradient-to-br from-primary-50 to-primary-100 backdrop-blur-sm rounded-xl border border-primary-200">
                  <h3 className="font-semibold text-primary-800 mb-2">Legal Procedures</h3>
                  <p className="text-sm text-primary-600 font-medium">Step-by-step guidance for legal processes</p>
                </div>
                <div className="p-4 bg-gradient-to-br from-primary-100 to-primary-200 backdrop-blur-sm rounded-xl border border-primary-300">
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
                <div className="flex flex-col max-w-3xl">
                  {!message.is_user && (
                    <div className="mb-1 ml-2">
                      <span className="text-xs font-semibold text-orange-600 bg-orange-50 px-2 py-1 rounded-full">
                        🤖 Cyberlex
                      </span>
                    </div>
                  )}
                  <div
                    className={`px-6 py-4 rounded-2xl shadow-sm ${
                      message.is_user
                        ? 'bg-gradient-primary text-white shadow-lg border border-primary-400'
                        : 'bg-gradient-to-r from-white to-primary-50 backdrop-blur-sm border border-primary-200 text-primary-800'
                    }`}
                  >
                    <ChatMessage content={message.content} isUser={message.is_user} />
                    <span
                      className={`text-xs mt-2 block ${
                        message.is_user ? 'text-primary-100' : 'text-primary-600'
                      }`}
                    >
                      {new Date(message.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gradient-to-r from-white to-primary-50 backdrop-blur-sm border border-primary-200 px-6 py-4 rounded-2xl shadow-sm">
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

        <div className="p-6 bg-white/95 backdrop-blur-xl border-t border-primary-100">
          {/* File Upload Area */}
          {selectedFile && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">{uploadedFileName}</span>
                <span className="text-xs text-blue-600">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
              </div>
              <button
                onClick={removeSelectedFile}
                className="text-blue-600 hover:text-blue-800 p-1"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* File Upload Modal */}
          {showFileUpload && (
            <div className="mb-4 p-4 bg-primary-50 border border-primary-200 rounded-xl">
              <div className="text-center">
                <Upload className="w-8 h-8 text-primary-600 mx-auto mb-2" />
                <p className="text-sm font-medium text-primary-800 mb-3">Upload a document for analysis</p>
                <input
                  type="file"
                  onChange={handleFileSelect}
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif"
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 cursor-pointer transition-colors"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Choose File
                </label>
                <p className="text-xs text-primary-600 mt-2">
                  Supported: PDF, DOC, DOCX, TXT, JPG, PNG, GIF (Max 10MB)
                </p>
                <button
                  onClick={() => setShowFileUpload(false)}
                  className="mt-2 text-primary-600 hover:text-primary-800 text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          <div className="flex space-x-2">
            {/* Multimedia Pin Button */}
            <button
              onClick={toggleFileUpload}
              className="p-4 bg-primary-100 text-primary-600 rounded-xl hover:bg-primary-200 hover:scale-105 transition-all duration-200 flex items-center justify-center"
              title="Attach file"
            >
              <Paperclip className="w-5 h-5" />
            </button>

            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage()
                }
              }}
              placeholder={selectedFile ? "Ask questions about the uploaded file..." : "Ask about cybercrime laws, IT Act, legal procedures..."}
              className="flex-1 px-6 py-4 bg-primary-50/80 backdrop-blur-sm border border-primary-200 rounded-xl focus:ring-2 focus:ring-primary-400 focus:border-primary-400 outline-none transition-all text-primary-900 placeholder-primary-700"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
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