import { NextRequest, NextResponse } from 'next/server'
import path from 'path'
import fs from 'fs'

export async function GET() {
  try {
    // Path to the MCQ JSON file in public directory
    const filePath = path.join(process.cwd(), 'public', 'mcq.json')
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return NextResponse.json(
        { error: 'MCQ questions file not found' },
        { status: 404 }
      )
    }

    // Read and parse the JSON file
    const fileContent = fs.readFileSync(filePath, 'utf-8')
    const questions = JSON.parse(fileContent)

    // Validate that we have questions
    if (!Array.isArray(questions) || questions.length === 0) {
      return NextResponse.json(
        { error: 'Invalid questions format' },
        { status: 400 }
      )
    }

    // Shuffle and return 10 random questions
    const shuffledQuestions = [...questions].sort(() => Math.random() - 0.5).slice(0, 10)

    return NextResponse.json({
      success: true,
      questions: shuffledQuestions,
      total: questions.length
    })

  } catch (error) {
    console.error('Error loading MCQ questions:', error)
    return NextResponse.json(
      { error: 'Failed to load questions' },
      { status: 500 }
    )
  }
}