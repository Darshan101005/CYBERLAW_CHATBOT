'use client'

import { useState, useEffect } from 'react'
import { X, Brain, ChevronRight, Clock, CheckCircle, XCircle, Award, BookOpen, Target, TrendingUp } from 'lucide-react'

interface MCQQuestion {
  id: number
  category: string
  question: string
  options: {
    a: string
    b: string
    c: string
    d: string
  }
  answer: string
}

interface UserAnswer {
  questionId: number
  selectedAnswer: string
  isCorrect: boolean
  category: string
}

interface QuizProps {
  isOpen: boolean
  onClose: () => void
}

export default function CyberLawQuiz({ isOpen, onClose }: QuizProps) {
  const [questions, setQuestions] = useState<MCQQuestion[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [userAnswers, setUserAnswers] = useState<UserAnswer[]>([])
  const [selectedAnswer, setSelectedAnswer] = useState('')
  const [timeRemaining, setTimeRemaining] = useState(600) // 10 minutes
  const [quizStarted, setQuizStarted] = useState(false)
  const [quizCompleted, setQuizCompleted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // Load and shuffle questions when component mounts
  useEffect(() => {
    if (isOpen && !quizStarted) {
      loadQuestions()
    }
  }, [isOpen])

  // Timer effect
  useEffect(() => {
    let timer: NodeJS.Timeout
    if (quizStarted && !quizCompleted && timeRemaining > 0) {
      timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleQuizComplete()
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => clearInterval(timer)
  }, [quizStarted, quizCompleted, timeRemaining])

  const loadQuestions = async () => {
    setIsLoading(true)
    try {
      const response = await fetch('/api/mcq-questions')
      
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.questions) {
          setQuestions(data.questions)
          return
        }
      }

      // Fallback to mock data if API fails
      console.warn('API failed, using fallback questions')
      const allQuestions: MCQQuestion[] = [
        {
          "id": 1,
          "category": "Foundational Concepts & Terminology",
          "question": "What is the primary purpose of Cyber Law?",
          "options": {
            "a": "To regulate the internet's hardware infrastructure.",
            "b": "To govern the legal issues related to the use of the internet and information technology.",
            "c": "To exclusively prosecute hackers.",
            "d": "To manage the sale of computer software."
          },
          "answer": "b"
        },
        {
          "id": 2,
          "category": "Foundational Concepts & Terminology",
          "question": "Which of the following best defines 'Cybercrime'?",
          "options": {
            "a": "Any crime committed using a computer.",
            "b": "A criminal activity that involves a computer, networked device, or a network.",
            "c": "Only financial fraud conducted online.",
            "d": "The act of sending spam emails."
          },
          "answer": "b"
        },
        {
          "id": 3,
          "category": "Foundational Concepts & Terminology",
          "question": "In the context of cyber law, what does 'Jurisdiction' refer to?",
          "options": {
            "a": "The type of computer used to commit a crime.",
            "b": "The legal authority of a court or government to hear a case and enforce laws.",
            "c": "The speed of the internet connection.",
            "d": "The software used to browse the internet."
          },
          "answer": "b"
        },
        {
          "id": 4,
          "category": "Foundational Concepts & Terminology",
          "question": "The Information Technology Act, 2000 is the primary cyber law of which country?",
          "options": {
            "a": "United States",
            "b": "United Kingdom",
            "c": "India",
            "d": "Australia"
          },
          "answer": "c"
        },
        {
          "id": 5,
          "category": "Foundational Concepts & Terminology",
          "question": "What is the main function of a Digital Signature?",
          "options": {
            "a": "To encrypt the entire content of a document.",
            "b": "To provide a secure and authentic way to sign electronic documents.",
            "c": "To hide the sender's identity.",
            "d": "To scan a handwritten signature."
          },
          "answer": "b"
        },
        {
          "id": 6,
          "category": "Foundational Concepts & Terminology",
          "question": "'Personally Identifiable Information' (PII) refers to:",
          "options": {
            "a": "Any data about a computer.",
            "b": "Information that can be used to identify, contact, or locate a single person.",
            "c": "Publicly available information like news articles.",
            "d": "Any file stored on a personal computer."
          },
          "answer": "b"
        },
        {
          "id": 7,
          "category": "Foundational Concepts & Terminology",
          "question": "The process of collecting, processing, and analyzing digital evidence from computer systems is known as:",
          "options": {
            "a": "Cyber Hacking",
            "b": "Data Encryption",
            "c": "Cyber Forensics",
            "d": "Network Security"
          },
          "answer": "c"
        },
        {
          "id": 8,
          "category": "Data Privacy and Protection",
          "question": "What is the main objective of a Data Protection Law?",
          "options": {
            "a": "To ensure all data is stored in the cloud.",
            "b": "To protect individuals' fundamental right to privacy with respect to their personal data.",
            "c": "To make all personal data publicly accessible.",
            "d": "To regulate the price of data storage."
          },
          "answer": "b"
        },
        {
          "id": 9,
          "category": "Data Privacy and Protection",
          "question": "Under most data protection laws, what is 'Consent'?",
          "options": {
            "a": "Permission given by any person on behalf of the data subject.",
            "b": "A freely given, specific, informed and unambiguous indication of the data subject's wishes.",
            "c": "An automatic permission granted when someone uses a website.",
            "d": "A verbal agreement that doesn't need to be documented."
          },
          "answer": "b"
        },
        {
          "id": 10,
          "category": "Data Privacy and Protection",
          "question": "What does 'Data Breach' typically refer to?",
          "options": {
            "a": "A security incident where sensitive, protected or confidential data is copied, transmitted, viewed, stolen or used by an unauthorized individual.",
            "b": "The normal process of backing up data.",
            "c": "Updating software on a computer.",
            "d": "Sharing data with authorized users."
          },
          "answer": "a"
        }
      ]

      // Shuffle and select 10 random questions
      const shuffled = [...allQuestions].sort(() => Math.random() - 0.5).slice(0, 10)
      setQuestions(shuffled)
    } catch (error) {
      console.error('Failed to load questions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const startQuiz = () => {
    setQuizStarted(true)
    setCurrentQuestionIndex(0)
    setUserAnswers([])
    setSelectedAnswer('')
    setTimeRemaining(600)
    setQuizCompleted(false)
  }

  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswer(answer)
  }

  const handleNextQuestion = () => {
    if (!selectedAnswer) return

    const currentQuestion = questions[currentQuestionIndex]
    const isCorrect = selectedAnswer === currentQuestion.answer
    
    const newAnswer: UserAnswer = {
      questionId: currentQuestion.id,
      selectedAnswer,
      isCorrect,
      category: currentQuestion.category
    }

    const updatedAnswers = [...userAnswers, newAnswer]
    setUserAnswers(updatedAnswers)
    setSelectedAnswer('')

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    } else {
      handleQuizComplete()
    }
  }

  const handleQuizComplete = () => {
    setQuizCompleted(true)
    setQuizStarted(false)
  }

  const calculateResults = () => {
    const correctAnswers = userAnswers.filter(answer => answer.isCorrect).length
    const totalQuestions = questions.length
    const percentage = Math.round((correctAnswers / totalQuestions) * 100)

    // Category-wise analysis
    const categoryStats = userAnswers.reduce((stats, answer) => {
      if (!stats[answer.category]) {
        stats[answer.category] = { correct: 0, total: 0 }
      }
      stats[answer.category].total++
      if (answer.isCorrect) {
        stats[answer.category].correct++
      }
      return stats
    }, {} as Record<string, { correct: number; total: number }>)

    return { correctAnswers, totalQuestions, percentage, categoryStats }
  }

  const getPerformanceLevel = (percentage: number) => {
    if (percentage >= 90) return { level: 'Expert', color: 'text-green-600', bgColor: 'bg-green-100', icon: Award }
    if (percentage >= 80) return { level: 'Advanced', color: 'text-blue-600', bgColor: 'bg-blue-100', icon: TrendingUp }
    if (percentage >= 70) return { level: 'Proficient', color: 'text-orange-600', bgColor: 'bg-orange-100', icon: Target }
    if (percentage >= 60) return { level: 'Intermediate', color: 'text-yellow-600', bgColor: 'bg-yellow-100', icon: BookOpen }
    return { level: 'Beginner', color: 'text-red-600', bgColor: 'bg-red-100', icon: Brain }
  }

  const getRecommendations = (percentage: number, categoryStats: Record<string, { correct: number; total: number }>) => {
    const recommendations = []
    
    if (percentage < 70) {
      recommendations.push("Consider reviewing fundamental cyber law concepts")
      recommendations.push("Practice more MCQs to improve your understanding")
    }

    // Find weak categories
    Object.entries(categoryStats).forEach(([category, stats]) => {
      const categoryPercentage = (stats.correct / stats.total) * 100
      if (categoryPercentage < 60) {
        recommendations.push(`Focus on strengthening knowledge in: ${category}`)
      }
    })

    if (percentage >= 80) {
      recommendations.push("Excellent performance! Consider taking advanced cyber law courses")
      recommendations.push("You're ready to help others with cyber law questions")
    }

    return recommendations
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const resetQuiz = () => {
    setQuizStarted(false)
    setQuizCompleted(false)
    setCurrentQuestionIndex(0)
    setUserAnswers([])
    setSelectedAnswer('')
    setTimeRemaining(600)
    loadQuestions()
  }

  if (!isOpen) return null

  const currentQuestion = questions[currentQuestionIndex]
  const results = quizCompleted ? calculateResults() : null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center shadow-lg">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">Cyber Law Quiz</h2>
                <p className="text-sm text-gray-600">Test your cyber law knowledge</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {quizStarted && (
                <div className="flex items-center space-x-2 text-orange-600">
                  <Clock className="w-4 h-4" />
                  <span className="font-mono text-sm">{formatTime(timeRemaining)}</span>
                </div>
              )}
              <button
                onClick={onClose}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        <div className="p-6">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading questions...</p>
            </div>
          ) : !quizStarted && !quizCompleted ? (
            // Quiz Introduction
            <div className="text-center space-y-6">
              <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-8">
                <Brain className="w-16 h-16 text-orange-500 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-gray-800 mb-4">Cyber Law Knowledge Test</h3>
                <p className="text-gray-600 mb-6 leading-relaxed">
                  Challenge yourself with 10 randomly selected questions from our comprehensive cyber law database. 
                  Test your understanding of digital rights, cybercrime laws, data protection, and more.
                </p>
                <div className="grid grid-cols-2 gap-4 mb-8">
                  <div className="bg-white p-4 rounded-lg border border-orange-100">
                    <div className="flex items-center justify-center space-x-2 text-orange-600 mb-2">
                      <Target className="w-5 h-5" />
                      <span className="font-semibold">Questions</span>
                    </div>
                    <p className="text-2xl font-bold text-gray-800">10</p>
                    <p className="text-xs text-gray-500">Questions</p>
                  </div>
                  <div className="bg-white p-4 rounded-lg border border-orange-100">
                    <div className="flex items-center justify-center space-x-2 text-orange-600 mb-2">
                      <Clock className="w-5 h-5" />
                      <span className="font-semibold">Time Limit</span>
                    </div>
                    <p className="text-2xl font-bold text-gray-800">10</p>
                    <p className="text-xs text-gray-500">Minutes</p>
                  </div>
                </div>
                <button
                  onClick={startQuiz}
                  className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-8 py-3 rounded-lg font-medium hover:from-orange-600 hover:to-red-600 transition-all flex items-center space-x-2 mx-auto"
                >
                  <Brain className="w-5 h-5" />
                  <span>Start Quiz</span>
                </button>
              </div>
            </div>
          ) : quizCompleted && results ? (
            // Quiz Results
            <div className="space-y-6">
              <div className="text-center bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-8">
                <div className="flex items-center justify-center mb-4">
                  {results.percentage >= 70 ? (
                    <CheckCircle className="w-16 h-16 text-green-500" />
                  ) : (
                    <XCircle className="w-16 h-16 text-red-500" />
                  )}
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">Quiz Completed!</h3>
                <div className="text-6xl font-bold text-orange-600 mb-2">{results.percentage}%</div>
                <p className="text-gray-600 mb-4">
                  You scored {results.correctAnswers} out of {results.totalQuestions} questions correctly
                </p>
                
                {(() => {
                  const performance = getPerformanceLevel(results.percentage)
                  const Icon = performance.icon
                  return (
                    <div className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full ${performance.bgColor}`}>
                      <Icon className={`w-5 h-5 ${performance.color}`} />
                      <span className={`font-semibold ${performance.color}`}>{performance.level}</span>
                    </div>
                  )
                })()}
              </div>

              {/* Category Analysis */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-orange-500" />
                  Performance by Category
                </h4>
                <div className="space-y-3">
                  {Object.entries(results.categoryStats).map(([category, stats]) => {
                    const categoryPercentage = Math.round((stats.correct / stats.total) * 100)
                    return (
                      <div key={category} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm font-medium text-gray-700">{category}</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-600">{stats.correct}/{stats.total}</span>
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${categoryPercentage >= 80 ? 'bg-green-500' : categoryPercentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                              style={{ width: `${categoryPercentage}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-semibold text-gray-800 w-12">{categoryPercentage}%</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Recommendations */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
                  <BookOpen className="w-5 h-5 mr-2 text-orange-500" />
                  Recommendations
                </h4>
                <div className="space-y-2">
                  {getRecommendations(results.percentage, results.categoryStats).map((recommendation, index) => (
                    <div key={index} className="flex items-start space-x-2 text-sm text-gray-700">
                      <ChevronRight className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                      <span>{recommendation}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4">
                <button
                  onClick={resetQuiz}
                  className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 px-6 rounded-lg font-medium hover:from-orange-600 hover:to-red-600 transition-all"
                >
                  Take Quiz Again
                </button>
                <button
                  onClick={onClose}
                  className="flex-1 bg-gray-500 text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-600 transition-all"
                >
                  Close
                </button>
              </div>
            </div>
          ) : (
            // Quiz Questions
            <div className="space-y-6">
              {/* Progress Bar */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <span className="text-sm font-medium text-gray-600">
                    Question {currentQuestionIndex + 1} of {questions.length}
                  </span>
                  <div className="w-48 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Current Question */}
              {currentQuestion && (
                <div className="space-y-6">
                  <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-6">
                    <div className="mb-4">
                      <span className="inline-block bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full mb-3">
                        {currentQuestion.category}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800 leading-relaxed">
                      {currentQuestion.question}
                    </h3>
                  </div>

                  <div className="space-y-3">
                    {Object.entries(currentQuestion.options).map(([key, option]) => (
                      <button
                        key={key}
                        onClick={() => handleAnswerSelect(key)}
                        className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                          selectedAnswer === key
                            ? 'border-orange-500 bg-orange-50 text-orange-800'
                            : 'border-gray-200 hover:border-orange-300 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-start space-x-3">
                          <span className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center text-sm font-medium ${
                            selectedAnswer === key
                              ? 'border-orange-500 bg-orange-500 text-white'
                              : 'border-gray-300 text-gray-500'
                          }`}>
                            {key.toUpperCase()}
                          </span>
                          <span className="text-gray-700">{option}</span>
                        </div>
                      </button>
                    ))}
                  </div>

                  <div className="flex justify-end">
                    <button
                      onClick={handleNextQuestion}
                      disabled={!selectedAnswer}
                      className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-8 py-3 rounded-lg font-medium hover:from-orange-600 hover:to-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center space-x-2"
                    >
                      <span>{currentQuestionIndex === questions.length - 1 ? 'Finish Quiz' : 'Next Question'}</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}