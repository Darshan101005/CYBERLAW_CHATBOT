'use client'

import { ReactElement } from 'react'

interface ChatMessageProps {
  content: string
  isUser: boolean
}

export default function ChatMessage({ content, isUser }: ChatMessageProps) {
  // Function to format the text with proper markdown parsing
  const formatContent = (text: string) => {
    // Split by lines and process each line
    const lines = text.split('\n')
    const formattedLines: ReactElement[] = []
    
    lines.forEach((line, index) => {
      // Handle section headers like **IT_ACT Section 66B** or **Section 67**
      if (line.trim().includes('**') && (line.includes('Section') || line.includes('ACT') || line.includes('IPC') || line.includes('BNS'))) {
        const parts = line.split(/(\*\*[^*]+\*\*)/g)
        const formatted = parts.map((part, partIndex) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return (
              <span key={partIndex} className="font-bold text-orange-600 bg-orange-50 px-2 py-1 rounded-md">
                {part.slice(2, -2)}
              </span>
            )
          }
          return <span key={partIndex}>{part}</span>
        })
        formattedLines.push(
          <div key={index} className="my-2 font-medium">
            {formatted}
          </div>
        )
      }
      // Handle regular headers with **
      else if (line.trim().startsWith('**') && line.trim().endsWith('**') && !line.includes(':')) {
        const headerText = line.trim().slice(2, -2)
        formattedLines.push(
          <h3 key={index} className="font-bold text-lg mt-4 mb-2 first:mt-0 text-orange-700">
            {headerText}
          </h3>
        )
      }
      // Handle bullet points starting with * (convert to •)
      else if (line.trim().startsWith('* ')) {
        const content = line.trim().slice(2)
        
        // Check for color-coded legal sections (Support/Against with emojis)
        if (content.includes('Support:') && content.includes('🟢')) {
          const parts = content.split(/(\*\*[^*]*\*\*)/g)
          const formatted = parts.map((part, partIndex) => {
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
              return (
                <strong key={partIndex} className="font-semibold text-green-800">
                  {part.slice(2, -2)}
                </strong>
              )
            }
            return <span key={partIndex}>{part}</span>
          })
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-2 bg-green-50 border-l-4 border-green-400 p-3 rounded-r-lg">
              <span className="text-green-600 font-bold mt-0.5">•</span>
              <span className="text-green-700">{formatted}</span>
            </div>
          )
        }
        else if (content.includes('Against:') && content.includes('🔴')) {
          const parts = content.split(/(\*\*[^*]*\*\*)/g)
          const formatted = parts.map((part, partIndex) => {
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
              return (
                <strong key={partIndex} className="font-semibold text-red-800">
                  {part.slice(2, -2)}
                </strong>
              )
            }
            return <span key={partIndex}>{part}</span>
          })
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-2 bg-red-50 border-l-4 border-red-400 p-3 rounded-r-lg">
              <span className="text-red-600 font-bold mt-0.5">•</span>
              <span className="text-red-700">{formatted}</span>
            </div>
          )
        }
        else if (content.includes('General:') && content.includes('🟡')) {
          const parts = content.split(/(\*\*[^*]*\*\*)/g)
          const formatted = parts.map((part, partIndex) => {
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
              return (
                <strong key={partIndex} className="font-semibold text-yellow-800">
                  {part.slice(2, -2)}
                </strong>
              )
            }
            return <span key={partIndex}>{part}</span>
          })
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-2 bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded-r-lg">
              <span className="text-yellow-600 font-bold mt-0.5">•</span>
              <span className="text-yellow-700">{formatted}</span>
            </div>
          )
        }
        // Regular bullet point with bold formatting
        else if (content.includes('**')) {
          const parts = content.split(/(\*\*[^*]*\*\*)/g)
          const formatted = parts.map((part, partIndex) => {
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
              return (
                <strong key={partIndex} className="font-semibold text-orange-800">
                  {part.slice(2, -2)}
                </strong>
              )
            }
            return <span key={partIndex}>{part}</span>
          })
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-1">
              <span className="text-orange-500 font-bold mt-0.5">•</span>
              <span>{formatted}</span>
            </div>
          )
        } else {
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-1">
              <span className="text-orange-500 font-bold mt-0.5">•</span>
              <span>{content}</span>
            </div>
          )
        }
      }
      // Handle bullet points starting with • (keep as is)
      else if (line.trim().startsWith('• ')) {
        const content = line.trim().slice(2)
        
        // Check for color-coded legal sections (Support/Against with emojis)
        if (content.includes('Support:') && content.includes('🟢')) {
          const parts = content.split(/(\*\*[^*]*\*\*)/g)
          const formatted = parts.map((part, partIndex) => {
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
              return (
                <strong key={partIndex} className="font-semibold text-green-800">
                  {part.slice(2, -2)}
                </strong>
              )
            }
            return <span key={partIndex}>{part}</span>
          })
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-2 bg-green-50 border-l-4 border-green-400 p-3 rounded-r-lg">
              <span className="text-green-600 font-bold mt-0.5">•</span>
              <span className="text-green-700">{formatted}</span>
            </div>
          )
        }
        else if (content.includes('Against:') && content.includes('🔴')) {
          const parts = content.split(/(\*\*[^*]*\*\*)/g)
          const formatted = parts.map((part, partIndex) => {
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
              return (
                <strong key={partIndex} className="font-semibold text-red-800">
                  {part.slice(2, -2)}
                </strong>
              )
            }
            return <span key={partIndex}>{part}</span>
          })
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-2 bg-red-50 border-l-4 border-red-400 p-3 rounded-r-lg">
              <span className="text-red-600 font-bold mt-0.5">•</span>
              <span className="text-red-700">{formatted}</span>
            </div>
          )
        }
        else if (content.includes('General:') && content.includes('🟡')) {
          const parts = content.split(/(\*\*[^*]*\*\*)/g)
          const formatted = parts.map((part, partIndex) => {
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
              return (
                <strong key={partIndex} className="font-semibold text-yellow-800">
                  {part.slice(2, -2)}
                </strong>
              )
            }
            return <span key={partIndex}>{part}</span>
          })
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-2 bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded-r-lg">
              <span className="text-yellow-600 font-bold mt-0.5">•</span>
              <span className="text-yellow-700">{formatted}</span>
            </div>
          )
        }
        // Regular bullet point with bold formatting
        else if (content.includes('**')) {
          const parts = content.split(/(\*\*[^*]*\*\*)/g)
          const formatted = parts.map((part, partIndex) => {
            if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
              return (
                <strong key={partIndex} className="font-semibold text-orange-800">
                  {part.slice(2, -2)}
                </strong>
              )
            }
            return <span key={partIndex}>{part}</span>
          })
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-1">
              <span className="text-orange-500 font-bold mt-0.5">•</span>
              <span>{formatted}</span>
            </div>
          )
        } else {
          formattedLines.push(
            <div key={index} className="flex items-start gap-2 my-1">
              <span className="text-orange-500 font-bold mt-0.5">•</span>
              <span>{content}</span>
            </div>
          )
        }
      }
      // Handle numbered lists
      else if (/^\d+\.\s/.test(line.trim())) {
        formattedLines.push(
          <div key={index} className="flex items-start gap-2 my-1">
            <span className="text-orange-600 font-semibold">{line.trim().match(/^\d+\./)?.[0]}</span>
            <span>{line.trim().replace(/^\d+\.\s/, '')}</span>
          </div>
        )
      }
      // Handle lines with bold text (** formatting)
      else if (line.includes('**')) {
        const parts = line.split(/(\*\*[^*]*\*\*)/g)
        const formatted = parts.map((part, partIndex) => {
          if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
            return (
              <strong key={partIndex} className="font-semibold text-orange-800">
                {part.slice(2, -2)}
              </strong>
            )
          }
          return <span key={partIndex}>{part}</span>
        })
        formattedLines.push(
          <p key={index} className="my-1">
            {formatted}
          </p>
        )
      }
      // Handle regular text
      else if (line.trim()) {
        formattedLines.push(
          <p key={index} className="my-1">
            {line}
          </p>
        )
      }
      // Handle empty lines (add spacing)
      else {
        formattedLines.push(<div key={index} className="h-2" />)
      }
    })
    
    return formattedLines
  }
  
  return (
    <div className={`leading-relaxed ${isUser ? 'text-white' : 'text-primary-800'}`}>
      {formatContent(content)}
    </div>
  )
}