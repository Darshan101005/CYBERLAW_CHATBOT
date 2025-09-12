'use client'

import { X, Calendar, FileText, ExternalLink } from 'lucide-react'

interface Amendment {
  date: string
  title: string
  short_description: string
}

interface LatestAmendmentsProps {
  isOpen: boolean
  onClose: () => void
}

const amendmentsData: Amendment[] = [
  {
    "date": "2024-07-25",
    "title": "Corrigendum- Extension of last date for submission of application under the scheme for setting up of Semiconductor Fabs in India",
    "short_description": "A notification regarding the extension of the deadline for applications for setting up Semiconductor Fabs in India."
  },
  {
    "date": "2024-07-24",
    "title": "Office Memorandum regarding constitution of Grievance Appellate Committee (GAC) under the Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021",
    "short_description": "This memorandum details the formation of the Grievance Appellate Committee as established by the IT Rules of 2021."
  },
  {
    "date": "2024-07-17",
    "title": "Appointment of Designated Officer under Rule 13 of the Information Technology (Procedure and Safeguards for Interception, Monitoring and Decryption of Information) Rules, 2009",
    "short_description": "An order concerning the appointment of a Designated Officer for the purpose of interception, monitoring, and decryption of information under the IT Rules of 2009."
  },
  {
    "date": "2024-07-04",
    "title": "Gazette Notification for the appointment of Chairperson and Members of the Digital Competition Law Committee",
    "short_description": "The official gazette notification announcing the appointment of the Chairperson and Members of the Digital Competition Law Committee."
  },
  {
    "date": "2024-06-28",
    "title": "Office Order regarding the assignment of additional charge of the post of Controller of Certifying Authorities (CCA)",
    "short_description": "An office order detailing the assignment of additional responsibilities for the post of the Controller of Certifying Authorities."
  },
  {
    "date": "2024-06-21",
    "title": "Scheme for Promotion of Research and Development in Electronics and IT",
    "short_description": "Details of a scheme aimed at promoting research and development within the electronics and IT sectors."
  },
  {
    "date": "2024-06-12",
    "title": "Constitution of an Advisory Committee for the Semicon India Program",
    "short_description": "An order for the constitution of an advisory committee for the Semicon India Program."
  }
]

export default function LatestAmendments({ isOpen, onClose }: LatestAmendmentsProps) {
  if (!isOpen) return null

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center shadow-lg">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-800">Latest Amendments</h2>
                <p className="text-sm text-gray-600">Recent updates and changes in cyber law and IT regulations</p>
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
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-1">
            {amendmentsData.map((amendment, index) => (
              <div key={index} className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-6 hover:shadow-lg transition-all duration-200 hover:border-orange-300">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2 text-orange-600">
                    <Calendar className="w-4 h-4" />
                    <span className="text-sm font-medium">{formatDate(amendment.date)}</span>
                  </div>
                  <div className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full">
                    Amendment #{amendmentsData.length - index}
                  </div>
                </div>
                
                <h3 className="text-lg font-bold text-gray-800 mb-3 leading-tight">
                  {amendment.title}
                </h3>
                
                <p className="text-gray-600 text-sm leading-relaxed mb-4">
                  {amendment.short_description}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <FileText className="w-3 h-3" />
                    <span>Official Document</span>
                  </div>
                  <button className="flex items-center space-x-1 text-orange-600 hover:text-orange-800 text-sm font-medium transition-colors">
                    <span>View Details</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 p-4 bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center flex-shrink-0">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <h3 className="font-semibold text-orange-800 mb-1">Stay Updated</h3>
                <p className="text-orange-700 text-sm">
                  These amendments reflect the latest changes in cyber law and IT regulations. 
                  For the most current information, always refer to official government sources and gazette notifications.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}