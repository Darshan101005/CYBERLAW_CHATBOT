import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from 'next/server'

export async function PUT(request: NextRequest) {
  try {
    const { sessionId, is_favorite } = await request.json()
    
    if (!sessionId) {
      return NextResponse.json({ error: 'Session ID is required' }, { status: 400 })
    }

    const cookieStore = await cookies()
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          get(name: string) {
            return cookieStore.get(name)?.value
          },
        },
      }
    )
    
    // Get the current user
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    if (userError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Update the session
    const { data, error } = await supabase
      .from('chat_sessions')
      .update({ is_favorite, updated_at: new Date().toISOString() })
      .eq('id', sessionId)
      .eq('user_id', user.id)
      .select()

    if (error) {
      console.error('Error updating session favorite:', error)
      return NextResponse.json({ error: 'Failed to update session' }, { status: 500 })
    }

    if (!data || data.length === 0) {
      return NextResponse.json({ error: 'Session not found' }, { status: 404 })
    }

    return NextResponse.json({ 
      message: 'Session updated successfully',
      session: data[0]
    })

  } catch (error) {
    console.error('Error in sessions API:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const { sessionId, title } = await request.json()
    
    if (!sessionId || !title) {
      return NextResponse.json({ error: 'Session ID and title are required' }, { status: 400 })
    }

    const cookieStore = await cookies()
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          get(name: string) {
            return cookieStore.get(name)?.value
          },
        },
      }
    )
    
    // Get the current user
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    if (userError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Update the session title
    const { data, error } = await supabase
      .from('chat_sessions')
      .update({ title, updated_at: new Date().toISOString() })
      .eq('id', sessionId)
      .eq('user_id', user.id)
      .select()

    if (error) {
      console.error('Error updating session title:', error)
      return NextResponse.json({ error: 'Failed to update session' }, { status: 500 })
    }

    if (!data || data.length === 0) {
      return NextResponse.json({ error: 'Session not found' }, { status: 404 })
    }

    return NextResponse.json({ 
      message: 'Session title updated successfully',
      session: data[0]
    })

  } catch (error) {
    console.error('Error in sessions API:', error)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}