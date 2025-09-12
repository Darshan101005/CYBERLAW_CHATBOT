'use client'

import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { Bell, X, ChevronLeft, RefreshCw, ExternalLink, Calendar, Globe } from 'lucide-react'

interface NewsItem {
  id: string
  title: string
  description: string
  url: string
  image: string
  publishedAt: string
  source: string
}

export default function NewsNotification() {
  const [isOpen, setIsOpen] = useState(false)
  const [news, setNews] = useState<NewsItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchNews = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/news', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-cache'
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('Fetched news data:', data)
      
      if (Array.isArray(data)) {
        setNews(data)
      } else {
        throw new Error('Invalid data format received')
      }
    } catch (err) {
      setError('Failed to load news. Please try again.')
      console.error('Error fetching news:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen) {
      fetchNews()
    }
    // Lock body scroll when panel is open
    if (typeof document !== 'undefined') {
      const originalOverflow = document.body.style.overflow
      document.body.style.overflow = isOpen ? 'hidden' : originalOverflow
      return () => {
        document.body.style.overflow = originalOverflow
      }
    }
  }, [isOpen])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  return (
    <>
      {/* Bell Icon Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="relative p-3 text-orange-600 hover:text-orange-800 hover:bg-orange-50 rounded-xl transition-all duration-200 group"
        title="Latest Cybercrime News"
      >
        <Bell className="w-6 h-6" />
        {news.length > 0 && (
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
        )}
      </button>

      {/* Sliding News Panel */}
      {createPortal(
        <div className={`fixed inset-y-0 right-0 z-[9999] w-[var(--news-panel-width)] h-screen bg-white border-l border-gray-200 shadow-2xl transform transition-transform duration-300 ease-in-out overflow-hidden pointer-events-auto ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}>
        <div className="flex flex-col h-full max-h-screen bg-white">
          {/* Header */}
          <div className="sticky top-0 z-10 flex-shrink-0 p-4 border-b border-gray-200 bg-gradient-to-r from-white to-orange-50">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                  <Bell className="w-4 h-4 text-white" />
                </div>
                <h2 className="text-xl font-bold text-gray-800">Latest News</h2>
              </div>
              <div className="flex items-center space-x-1">
                <button
                  onClick={fetchNews}
                  disabled={isLoading}
                  className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-all disabled:opacity-50"
                  title="Reload news"
                >
                  <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-all"
                  title="Close"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
              </div>
            </div>
            <p className="text-sm text-orange-600">
              Stay updated with latest cybercrime & security news
            </p>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto min-h-0 p-4 bg-white">
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-400"></div>
                <span className="ml-3 text-gray-600">Loading news...</span>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4">
                <p className="text-red-600 text-sm mb-2">{error}</p>
                <button
                  onClick={fetchNews}
                  className="px-3 py-1 bg-red-100 text-red-700 hover:bg-red-200 rounded-lg text-sm font-medium transition-colors"
                >
                  Try Again
                </button>
              </div>
            )}

            {!isLoading && !error && news.length === 0 && (
              <div className="text-center py-12">
                <Globe className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">No news available</p>
                <button
                  onClick={fetchNews}
                  className="px-4 py-2 bg-orange-500 text-white hover:bg-orange-600 rounded-lg font-medium transition-colors"
                >
                  Load News
                </button>
              </div>
            )}

            {/* News Cards */}
            {!isLoading && !error && news.length > 0 && (
              <div className="space-y-5 pb-6">
                {news.map((item) => (
                  <div
                    key={item.id}
                    className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-all duration-200 group"
                  >
                    {/* News Image */}
                    {item.image && (
                      <div className="relative mb-3 rounded-xl overflow-hidden ring-1 ring-gray-100">
                        <img
                          src={item.image}
                          alt={item.title}
                          className="w-full h-44 object-cover group-hover:scale-105 transition-transform duration-200"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none'
                          }}
                        />
                      </div>
                    )}

                    {/* News Content */}
                    <div className="space-y-3">
                      <h3 className="font-semibold text-gray-800 leading-tight text-base">
                        {item.title}
                      </h3>
                      
                      <p className="text-sm text-gray-600 leading-relaxed">
                        {truncateText(item.description, 150)}
                      </p>

                      {/* Meta Information */}
                      <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-gray-100">
                        <div className="flex items-center space-x-1">
                          <Globe className="w-3 h-3" />
                          <span className="truncate max-w-[100px]">{item.source}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{formatDate(item.publishedAt)}</span>
                        </div>
                      </div>

                      {/* Read More Button */}
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center space-x-1 text-orange-700 hover:text-orange-800 font-medium text-sm group/link"
                      >
                        <span>Read Full Article</span>
                        <ExternalLink className="w-3 h-3 group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>,
      document.body)}

      {/* Backdrop */}
      {isOpen && createPortal(
        <div
          className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[9998]"
          onClick={() => setIsOpen(false)}
        />,
      document.body)}
    </>
  )
}