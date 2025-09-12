import Link from 'next/link';
import { MessageCircle, Shield, Scale, Users, ArrowRight, Sparkles } from 'lucide-react';

export default function Home() {
  return (
  <div className="min-h-screen bg-gradient-hero relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-mesh opacity-60"></div>
      <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-primary-300/30 to-transparent rounded-full blur-3xl"></div>
  <div className="absolute bottom-0 right-0 w-80 h-80 bg-gradient-to-br from-primary-200/30 to-transparent rounded-full blur-3xl"></div>
      
      <div className="relative z-10">
        {/* Modern Navigation */}
        <nav className="container mx-auto px-6 py-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center shadow-glow">
                <Scale className="w-7 h-7 text-primary-50" />
              </div>
              <span className="text-2xl font-bold text-primary-800">
                CyberLaw AI
              </span>
            </div>
            <div className="flex items-center space-x-6">
              <Link 
                href="/auth/login" 
                className="text-primary-700 hover:text-primary-800 font-medium px-6 py-3 rounded-xl hover:bg-primary-100/50 transition-all duration-300"
              >
                Sign In
              </Link>
              <Link 
                href="/auth/signup" 
                className="bg-gradient-primary text-primary-50 px-8 py-3 rounded-xl font-semibold shadow-medium hover:shadow-glow transition-all duration-300 transform hover:scale-105"
              >
                Get Started
              </Link>
            </div>
          </div>
        </nav>

        {/* Hero Section - Vibrant & Colorful */}
        <main className="container mx-auto px-6 py-20">
          <div className="text-center mb-24">
            {/* Badge */}
            <div className="inline-flex items-center bg-primary-100/80 backdrop-blur-sm rounded-full px-8 py-4 mb-12 shadow-soft border border-primary-200">
              <Sparkles className="w-6 h-6 text-primary-700 mr-4" />
              <span className="text-primary-800 font-semibold text-lg">AI-Powered Legal Intelligence</span>
            </div>
            
            {/* Main Title - Vibrant Typography */}
            <h1 className="text-6xl md:text-8xl font-bold mb-12 leading-tight">
              <span className="block text-primary-800 mb-4">Navigate Legal</span>
              <span className="block text-primary-700 mb-4">Complexities with</span>
              <span className="block bg-gradient-primary bg-clip-text text-transparent">AI Precision</span>
            </h1>
            
            {/* Description */}
            <p className="text-xl text-primary-600 mb-16 max-w-4xl mx-auto leading-relaxed font-medium">
              Your intelligent companion for understanding cybercrime laws, IT Act compliance, 
              and navigating the digital legal landscape with confidence and precision.
            </p>
            
            {/* CTA Buttons - Vibrant & Colorful */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <Link 
                href="/auth/signup" 
                className="group bg-gradient-primary text-primary-50 px-12 py-6 rounded-2xl font-bold text-xl shadow-large hover:shadow-glow transition-all duration-300 transform hover:scale-105"
              >
                <span className="flex items-center">
                  Start Legal Chat
                  <ArrowRight className="ml-3 w-6 h-6 group-hover:translate-x-1 transition-transform duration-300" />
                </span>
              </Link>
              <Link 
                href="#features" 
                className="bg-primary-100 text-primary-800 px-12 py-6 rounded-2xl font-bold text-xl shadow-soft hover:bg-primary-200 transition-all duration-300 transform hover:scale-105"
              >
                Explore Features
              </Link>
            </div>
          </div>

          {/* Features Section - Colorful Cards */}
          <div className="grid md:grid-cols-3 gap-12 mb-24" id="features">
            {/* Feature 1 */}
            <div className="group text-center p-12 bg-surface-200/80 backdrop-blur-sm rounded-3xl shadow-soft hover:shadow-medium transition-all duration-300 transform hover:-translate-y-2 border border-surface-300">
              <div className="w-20 h-20 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-glow group-hover:scale-110 transition-transform duration-300">
                <MessageCircle className="w-10 h-10 text-primary-50" />
              </div>
              <h3 className="text-2xl font-bold text-primary-800 mb-6">Ask & Learn</h3>
              <p className="text-primary-600 text-lg leading-relaxed font-medium">
                Get instant answers to cybercrime law questions from our intelligent AI assistant with real-time guidance.
              </p>
            </div>
            
            {/* Feature 2 */}
            <div className="group text-center p-12 bg-surface-300/80 backdrop-blur-sm rounded-3xl shadow-soft hover:shadow-medium transition-all duration-300 transform hover:-translate-y-2 border border-surface-400">
              <div className="w-20 h-20 bg-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-glow group-hover:scale-110 transition-transform duration-300">
                <Shield className="w-10 h-10 text-primary-800" />
              </div>
              <h3 className="text-2xl font-bold text-primary-800 mb-6">Understand Laws</h3>
              <p className="text-primary-600 text-lg leading-relaxed font-medium">
                Navigate complex legal frameworks with simplified explanations and comprehensive expert insights.
              </p>
            </div>
            
            {/* Feature 3 */}
            <div className="group text-center p-12 bg-surface-400/80 backdrop-blur-sm rounded-3xl shadow-soft hover:shadow-medium transition-all duration-300 transform hover:-translate-y-2 border border-surface-500">
              <div className="w-20 h-20 bg-gradient-to-r from-primary-400 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-glow group-hover:scale-110 transition-transform duration-300">
                <Scale className="w-10 h-10 text-primary-50" />
              </div>
              <h3 className="text-2xl font-bold text-primary-800 mb-6">Take Action</h3>
              <p className="text-primary-600 text-lg leading-relaxed font-medium">
                Get step-by-step guidance on legal procedures and cybercrime reporting processes.
              </p>
            </div>
          </div>

          {/* CTA Section - Vibrant */}
          <div className="text-center bg-gradient-primary rounded-3xl p-20 shadow-large">
            <Users className="w-24 h-24 mx-auto mb-12 text-primary-50 opacity-90" />
            <h2 className="text-4xl md:text-5xl font-bold mb-8 text-primary-50">Ready to Get Started?</h2>
            <p className="text-primary-100 mb-12 max-w-3xl mx-auto text-xl leading-relaxed font-medium">
              Join thousands who trust CyberLaw AI for reliable legal guidance and expert insights.
            </p>
            <Link 
              href="/auth/signup" 
              className="inline-flex items-center bg-primary-100 text-primary-800 px-16 py-8 rounded-2xl font-bold text-xl shadow-large hover:bg-primary-200 transition-all duration-300 transform hover:scale-105"
            >
              Start Your Journey Today
              <ArrowRight className="ml-3 w-6 h-6" />
            </Link>
          </div>
        </main>

        {/* Footer - Clean, Professional */}
        <footer className="mt-24">
          <div className="container mx-auto px-6 py-12">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center shadow-glow">
                  <Scale className="w-6 h-6 text-primary-50" />
                </div>
                <span className="text-lg font-semibold text-primary-800">CyberLaw AI</span>
              </div>
              <nav className="flex items-center gap-6 text-primary-700">
                <Link href="#features" className="hover:text-primary-900">Features</Link>
                <Link href="/auth/signup" className="hover:text-primary-900">Get Started</Link>
                <Link href="/auth/login" className="hover:text-primary-900">Sign In</Link>
              </nav>
              <p className="text-primary-700">© 2025 CyberLaw AI Assistant</p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}