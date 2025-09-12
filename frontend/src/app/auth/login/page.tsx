'use client'

import { useState } from 'react'
import { supabase } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Eye, EyeOff, Mail, Lock, Scale } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) {
        setMessage(error.message)
      } else if (data.user) {
        router.push('/chat')
      }
    } catch (error) {
      setMessage('An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    if (!email) {
      setMessage('Please enter your email address first')
      return
    }

    setLoading(true)
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    })

    if (error) {
      setMessage(error.message)
    } else {
      setMessage('Password reset email sent! Check your inbox.')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gradient-hero flex items-center justify-center p-4">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-mesh opacity-60"></div>
      <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-primary-300/30 to-transparent rounded-full blur-3xl"></div>
  <div className="absolute bottom-0 right-0 w-80 h-80 bg-gradient-to-br from-primary-200/30 to-transparent rounded-full blur-3xl"></div>
      
      <div className="relative z-10 max-w-md w-full">
        <div className="bg-surface-200/90 backdrop-blur-xl rounded-3xl shadow-large p-10 border border-surface-300">
          <div className="text-center mb-10">
            <div className="mx-auto w-20 h-20 bg-gradient-primary rounded-2xl flex items-center justify-center mb-6 shadow-glow">
              <Scale className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-primary-800 mb-3">Welcome Back</h1>
            <p className="text-primary-600 text-lg font-medium">Sign in to Cyberlex Assistant</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-8">
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-primary-900 mb-3">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-primary-700 w-5 h-5" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 bg-primary-50/80 border border-primary-200 rounded-2xl focus:ring-2 focus:ring-primary-400 focus:border-primary-400 outline-none transition-all text-primary-900 placeholder-primary-600"
                  placeholder="Enter your email"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-primary-900 mb-3">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-primary-700 w-5 h-5" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-12 pr-14 py-4 bg-primary-50/80 border border-primary-200 rounded-2xl focus:ring-2 focus:ring-primary-400 focus:border-primary-400 outline-none transition-all text-primary-900 placeholder-primary-600"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-primary-700 hover:text-primary-900 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember"
                  type="checkbox"
                  className="w-5 h-5 text-primary-600 bg-surface-200 border-surface-400 rounded-lg focus:ring-primary-500 focus:ring-2"
                />
                <label htmlFor="remember" className="ml-3 block text-sm text-primary-800 font-medium">
                  Remember me
                </label>
              </div>
              <button
                type="button"
                onClick={handleForgotPassword}
                className="text-sm text-primary-700 hover:text-primary-900 font-semibold transition-colors"
              >
                Forgot password?
              </button>
            </div>

            {message && (
              <div className={`p-4 rounded-2xl text-sm font-medium ${
                message.includes('reset email') 
                  ? 'bg-primary-100 text-primary-800 border border-primary-300' 
                  : 'bg-primary-100 text-primary-800 border border-primary-300'
              }`}>
                {message}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-primary text-primary-50 py-4 px-6 rounded-2xl font-bold text-lg shadow-medium hover:shadow-glow focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105"
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-primary-600 text-lg font-medium">
              Don't have an account?{' '}
              <Link href="/auth/signup" className="text-primary-800 font-bold hover:text-primary-900 transition-colors">
                Sign up
              </Link>
            </p>
          </div>

          <div className="mt-6 text-center">
            <Link 
              href="/" 
              className="text-sm text-primary-500 hover:text-primary-700 font-medium transition-colors"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}