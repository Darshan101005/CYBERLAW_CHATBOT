import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json()

    const mockResponse = generateMockResponse(message)
    
    return NextResponse.json({ reply: mockResponse })
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

function generateMockResponse(message: string): string {
  const lowerMessage = message.toLowerCase()
  
  if (lowerMessage.includes('it act') || lowerMessage.includes('information technology')) {
    return `The Information Technology Act, 2000 is India's primary legislation dealing with cybercrime and electronic commerce. Key provisions include:

• Section 43: Penalty for damage to computer systems
• Section 66: Computer-related offences  
• Section 67: Publishing obscene information
• Section 69: Power to issue directions for blocking public access
• Section 72: Breach of confidentiality and privacy

The Act was amended in 2008 to strengthen cybersecurity provisions and include stricter penalties for cyber offences.`
  }
  
  if (lowerMessage.includes('cyber') && lowerMessage.includes('report')) {
    return `To report cybercrime in India:

1. **Online Portal**: Visit cybercrime.gov.in
2. **Local Police**: File FIR at nearest police station
3. **Cyber Cell**: Contact state/city cyber crime cell
4. **Evidence**: Preserve digital evidence (screenshots, emails, transaction details)
5. **Documents**: Keep all relevant documents ready

**Important**: Report immediately to preserve evidence and increase chances of recovery.

For financial fraud, also contact your bank immediately.`
  }
  
  if (lowerMessage.includes('section 66') || lowerMessage.includes('hacking')) {
    return `Section 66 of IT Act 2000 deals with computer-related offences including hacking:

**Penalty**: Imprisonment up to 3 years or fine up to ₹5 lakh or both

**Covers**:
• Dishonestly or fraudulently accessing computer systems
• Downloading, copying or extracting data
• Introducing computer viruses
• Damaging or disrupting computer systems

**Related Sections**:
• Section 66B: Receiving stolen computer resources
• Section 66C: Identity theft  
• Section 66D: Cheating by personation using computer
• Section 66E: Violation of privacy`
  }
  
  if (lowerMessage.includes('privacy') || lowerMessage.includes('data protection')) {
    return `India's data protection framework includes:

**IT Act 2000**:
• Section 72: Breach of confidentiality (penalty: 2 years + fine)
• Section 72A: Disclosure of personal information (added in 2008)

**Digital Personal Data Protection Act 2023**:
• Comprehensive data protection law
• Rights of data principals
• Obligations of data fiduciaries
• Penalties up to ₹250 crores

**Key Principles**:
• Consent-based processing
• Purpose limitation
• Data minimization
• Storage limitation`
  }
  
  if (lowerMessage.includes('fine') || lowerMessage.includes('penalty')) {
    return `Penalties under IT Act 2000:

**Section 43**: Damage to computer systems - Compensation up to ₹1 crore
**Section 66**: Hacking - Up to 3 years + ₹5 lakh fine
**Section 66B**: Receiving stolen computer resource - 3 years + ₹1 lakh
**Section 66C**: Identity theft - 3 years + ₹1 lakh  
**Section 66D**: Cheating by personation - 3 years + ₹1 lakh
**Section 66E**: Privacy violation - 3 years + ₹2 lakh
**Section 67**: Obscene content - 3 years + ₹5 lakh (first), 5 years + ₹10 lakh (subsequent)

Penalties have been significantly increased with amendments.`
  }
  
  if (lowerMessage.includes('digital signature') || lowerMessage.includes('electronic signature')) {
    return `Digital Signatures under IT Act 2000:

**Legal Validity**: Section 3 gives legal recognition to electronic records
**Digital Signature**: Section 3A validates digital signatures

**Requirements**:
• Must use asymmetric crypto system
• Hash function for authentication
• Issued by licensed Certifying Authority (CA)

**Uses**:
• E-governance applications
• Online transactions
• Legal documents
• Company filings

**Certifying Authorities**: Licensed by Controller of Certifying Authorities (CCA) under Ministry of Electronics & IT.`
  }

  if (lowerMessage.includes('jurisdiction') || lowerMessage.includes('court')) {
    return `Jurisdiction for cyber crimes:

**Territorial Jurisdiction**: 
• Where crime was committed
• Where consequences were felt
• Where accused resides

**Court Hierarchy**:
• Sessions Court: Serious cyber crimes
• Metropolitan Magistrate: Minor offences
• Special Courts: Complex cyber cases

**Cyber Appellate Tribunal**: For appeals under IT Act (now merged with TDSAT)

**International Cases**: Mutual Legal Assistance Treaties (MLAT) for cross-border crimes.

**Investigation**: Cyber crime cells, special investigation teams with technical expertise.`
  }
  
  return `I understand you're asking about cybercrime law. As a CyberLaw AI assistant, I can help with:

• **IT Act 2000** provisions and amendments
• **Cybercrime reporting** procedures  
• **Penalties and punishments** for cyber offences
• **Data protection** and privacy laws
• **Digital evidence** and investigation
• **Jurisdiction** and court procedures
• **Case studies** and legal precedents

Could you please be more specific about what aspect of cyber law you'd like to know about? For example:
- "What is Section 66A of IT Act?"
- "How to report online fraud?"
- "What are penalties for hacking?"
- "Data protection laws in India"`
}