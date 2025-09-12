import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { complaintType } = await request.json()
    
    if (!complaintType) {
      return NextResponse.json(
        { error: 'Complaint type is required' },
        { status: 400 }
      )
    }

    // Call Python backend for dynamic checklist generation
    const response = await fetch('http://localhost:5000/api/generate-checklist', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        complaint_type: complaintType
      })
    })

    if (!response.ok) {
      // Fallback to static checklist if backend fails
      return NextResponse.json({
        checklist: getStaticChecklist(complaintType)
      })
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('Error generating checklist:', error)
    
    // Fallback to static checklist
    const { complaintType } = await request.json()
    return NextResponse.json({
      checklist: getStaticChecklist(complaintType || 'General Cyber Crime')
    })
  }
}

// Fallback static checklist function
function getStaticChecklist(complaintType: string) {
  return {
    title: `Checklist for ${complaintType}`,
    mandatory: [
      "Incident Date and Time",
      "Incident details (minimum 200 characters) without special characters (#$@^*`''~|!)",
      "Soft copy of national ID (Voter ID, Driving License, Passport, PAN Card, Aadhar Card) in .jpeg, .jpg, .png format (max 5 MB)",
      "All relevant evidence related to the cyber crime (max 10 MB each)"
    ],
    optional: [
      "Suspected website URLs/Social Media handles",
      "Suspect details (mobile, email, bank account, address)",
      "Photograph of suspect (.jpeg, .jpg, .png format, max 5 MB)"
    ],
    financial: complaintType.toLowerCase().includes('financial') || complaintType.toLowerCase().includes('fraud') ? [
      "Name of Bank/Wallet/Merchant",
      "12-digit Transaction ID/UTR Number",
      "Date of transaction",
      "Fraud amount"
    ] : []
  }
}