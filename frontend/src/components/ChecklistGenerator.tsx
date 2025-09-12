'use client'

import { useState } from 'react'
import { X, CheckSquare, AlertCircle, Info, DollarSign } from 'lucide-react'

interface ChecklistGeneratorProps {
  isOpen: boolean
  onClose: () => void
}

export default function ChecklistGenerator({ isOpen, onClose }: ChecklistGeneratorProps) {
  const [complaintType, setComplaintType] = useState('')
  const [complaintDetails, setComplaintDetails] = useState('')
  const [showChecklist, setShowChecklist] = useState(false)
  const [checklist, setChecklist] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const generateChecklist = async () => {
    if (!complaintType || !complaintDetails) return
    
    setIsLoading(true)
    setError('')
    
    try {
      const response = await fetch('http://localhost:5000/api/generate-checklist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          complaint_type: `${complaintType}: ${complaintDetails}`
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to generate checklist')
      }
      
      const data = await response.json()
      
      if (data.success && data.checklist) {
        setChecklist(data.checklist)
        setShowChecklist(true)
      } else {
        throw new Error('Invalid response format')
      }
      
    } catch (err) {
      console.error('Error generating checklist:', err)
      setError('Failed to generate checklist. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const resetForm = () => {
    setComplaintType('')
    setComplaintDetails('')
    setShowChecklist(false)
    setChecklist(null)
    setError('')
  }

  const complaintTypes = [
    'Financial Fraud/Cyber Crime',
    'Identity Theft',
    'Fake Social Media Profile',
    'Cyberbullying/Online Harassment',
    'Hacking/Unauthorized Access',
    'Data Breach',
    'Online Fraud/Scam',
    'Phishing Attack',
    'Ransomware Attack',
    'Other Cyber Crime'
  ]

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center shadow-lg">
                <CheckSquare className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">Complaint Checklist Generator</h2>
                <p className="text-sm text-gray-600">Get ready for filing your cyber crime complaint</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6">
          {!showChecklist ? (
            // Input Form
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type of Complaint
                </label>
                <select
                  value={complaintType}
                  onChange={(e) => setComplaintType(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                >
                  <option value="">Select complaint type...</option>
                  {complaintTypes.map((type) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Brief Description of Your Complaint
                </label>
                <textarea
                  value={complaintDetails}
                  onChange={(e) => setComplaintDetails(e.target.value)}
                  placeholder="Describe what happened, when it happened, and any other relevant details..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 h-32 resize-none"
                />
              </div>

              <button
                onClick={generateChecklist}
                disabled={!complaintType || !complaintDetails || isLoading}
                className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 px-6 rounded-lg font-medium hover:from-orange-600 hover:to-red-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <CheckSquare className="w-4 h-4" />
                    Generate Checklist
                  </>
                )}
              </button>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              )}
            </div>
          ) : (
            // Checklist Display
            <div className="space-y-8">
              <div className="bg-orange-50 border-l-4 border-orange-400 p-4 rounded-r-lg">
                <div className="flex items-start">
                  <AlertCircle className="w-5 h-5 text-orange-400 mt-0.5 mr-3" />
                  <div>
                    <h3 className="font-medium text-orange-800">{checklist?.title || `Checklist for ${complaintType}`}</h3>
                    <p className="text-sm text-orange-700 mt-1">{complaintDetails}</p>
                  </div>
                </div>
              </div>

              {/* Mandatory Information */}
              {checklist?.mandatory && checklist.mandatory.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                  <h3 className="text-lg font-bold text-red-800 mb-4 flex items-center">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    Mandatory Information
                  </h3>
                  <div className="space-y-4">
                    {checklist.mandatory.map((item: any, index: number) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          {typeof item === 'string' ? (
                            <p className="text-red-800">{item}</p>
                          ) : (
                            <div>
                              <p className="text-red-800 font-medium">{item.item}</p>
                              <p className="text-red-700 text-sm mt-1">{item.description}</p>
                              {item.format && (
                                <p className="text-red-600 text-xs mt-1 bg-red-100 px-2 py-1 rounded inline-block">
                                  Format: {item.format}
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Financial Information */}
              {checklist?.financial && checklist.financial.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                  <h3 className="text-lg font-bold text-yellow-800 mb-4 flex items-center">
                    <DollarSign className="w-5 h-5 mr-2" />
                    Financial Information (if applicable)
                  </h3>
                  <div className="space-y-4">
                    {checklist.financial.map((item: any, index: number) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-yellow-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          {typeof item === 'string' ? (
                            <p className="text-yellow-800">{item}</p>
                          ) : (
                            <div>
                              <p className="text-yellow-800 font-medium">{item.item}</p>
                              <p className="text-yellow-700 text-sm mt-1">{item.description}</p>
                              {item.format && (
                                <p className="text-yellow-600 text-xs mt-1 bg-yellow-100 px-2 py-1 rounded inline-block">
                                  Format: {item.format}
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Optional Information */}
              {checklist?.optional && checklist.optional.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="text-lg font-bold text-blue-800 mb-4 flex items-center">
                    <Info className="w-5 h-5 mr-2" />
                    Optional/Desirable Information
                  </h3>
                  <div className="space-y-4">
                    {checklist.optional.map((item: any, index: number) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          {typeof item === 'string' ? (
                            <p className="text-blue-800">{item}</p>
                          ) : (
                            <div>
                              <p className="text-blue-800 font-medium">{item.item}</p>
                              <p className="text-blue-700 text-sm mt-1">{item.description}</p>
                              {item.format && (
                                <p className="text-blue-600 text-xs mt-1 bg-blue-100 px-2 py-1 rounded inline-block">
                                  Format: {item.format}
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tips */}
              {checklist?.specific_tips && checklist.specific_tips.length > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h3 className="text-lg font-bold text-green-800 mb-4 flex items-center">
                    <CheckSquare className="w-5 h-5 mr-2" />
                    Helpful Tips
                  </h3>
                  <div className="space-y-3">
                    {checklist.specific_tips.map((tip: string, index: number) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                        <p className="text-green-800">{tip}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4 pt-6 border-t border-gray-200">
                <button
                  onClick={resetForm}
                  className="flex-1 bg-gray-500 text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-600 transition-all"
                >
                  Generate New Checklist
                </button>
                <button
                  onClick={() => window.print()}
                  className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 px-6 rounded-lg font-medium hover:from-orange-600 hover:to-red-600 transition-all"
                >
                  Print Checklist
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}