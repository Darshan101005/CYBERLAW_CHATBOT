import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Fetch news from the external API
    const response = await fetch('https://webwatch.tech/NEWSAPI/news.json', {
      headers: {
        'User-Agent': 'CYBERLAW_CHATBOT/1.0',
      },
      // Add cache control to avoid too many requests
      next: { revalidate: 300 } // Cache for 5 minutes
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const newsData = await response.json();

    // Return the news data with proper CORS headers
    return NextResponse.json(newsData, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error) {
    console.error('Error fetching news:', error);
    return NextResponse.json(
      { error: 'Failed to fetch news' },
      { 
        status: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      }
    );
  }
}