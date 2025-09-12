'use client'

import { useState } from 'react'
import Link from 'next/link'
import { 
  Scale, 
  Gavel, 
  Shield, 
  BookOpen, 
  Users, 
  Award, 
  ArrowRight, 
  Menu, 
  X, 
  CheckCircle,
  TrendingUp,
  Globe,
  Lock,
  MessageCircle,
  Star,
  Zap
} from 'lucide-react'

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const features = [
    {
      icon: Scale,
      title: "Legal Compliance",
      description: "Ensure your digital activities comply with cybercrime laws and IT Act provisions."
    },
    {
      icon: Shield,
      title: "Data Protection",
      description: "Understand GDPR, Digital Personal Data Protection Act, and privacy regulations."
    },
    {
      icon: BookOpen,
      title: "Case Studies",
      description: "Learn from real cybercrime cases and legal precedents in Indian courts."
    },
    {
      icon: Gavel,
      title: "Legal Procedures",
      description: "Step-by-step guidance for filing FIR, evidence collection, and court procedures."
    }
  ]

  const stats = [
    { number: "99%", label: "Legal Accuracy", description: "AI-powered legal guidance" },
    { number: "10K+", label: "Cases Analyzed", description: "Comprehensive case database" },
    { number: "50+", label: "Legal Topics", description: "Cybercrime law coverage" },
    { number: "24/7", label: "AI Support", description: "Always available assistance" }
  ]

  const testimonials = [
    {
      name: "Advocate Sarah Patel",
      role: "Cyber Crime Lawyer",
      content: "Cyberlex AI has revolutionized how I research cybercrime cases. The instant access to relevant laws and precedents saves hours of research time.",
      rating: 5
    },
    {
      name: "Dr. Rajesh Kumar",
      role: "Legal Consultant",
      content: "Perfect for understanding complex IT Act provisions. The AI explanations are clear and practically applicable.",
      rating: 5
    },
    {
      name: "Priya Sharma",
      role: "Compliance Officer",
      content: "Essential tool for our company's legal compliance. Helps us stay updated with latest cybersecurity regulations.",
      rating: 5
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-hero">
      {/* Navigation */}
      <nav className="bg-white/90 backdrop-blur-xl border-b border-surface-200 sticky top-0 z-50 shadow-soft">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center shadow-medium">
                <Scale className="w-6 h-6 text-white" />
              </div>
              <div>
                <span className="font-bold text-xl text-surface-900">Cyberlex AI</span>
                <p className="text-sm text-surface-600 font-medium">Legal Assistant</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#features" className="text-surface-700 hover:text-primary-600 font-medium transition-colors">
                Features
              </Link>
              <Link href="#about" className="text-surface-700 hover:text-primary-600 font-medium transition-colors">
                About
              </Link>
              <Link href="#testimonials" className="text-surface-700 hover:text-primary-600 font-medium transition-colors">
                Reviews
              </Link>
              <Link href="#contact" className="text-surface-700 hover:text-primary-600 font-medium transition-colors">
                Contact
              </Link>
              <Link 
                href="/auth/login" 
                className="text-surface-700 hover:text-primary-600 font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link 
                href="/auth/signup" 
                className="bg-gradient-primary text-white px-6 py-2 rounded-xl font-semibold hover:shadow-glow transition-all duration-300 transform hover:scale-105"
              >
                Get Started
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-surface-700 hover:text-primary-600"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-surface-200">
              <div className="flex flex-col space-y-4">
                <Link href="#features" className="text-surface-700 hover:text-primary-600 font-medium">
                  Features
                </Link>
                <Link href="#about" className="text-surface-700 hover:text-primary-600 font-medium">
                  About
                </Link>
                <Link href="#testimonials" className="text-surface-700 hover:text-primary-600 font-medium">
                  Reviews
                </Link>
                <Link href="#contact" className="text-surface-700 hover:text-primary-600 font-medium">
                  Contact
                </Link>
                <Link href="/auth/login" className="text-surface-700 hover:text-primary-600 font-medium">
                  Sign In
                </Link>
                <Link 
                  href="/auth/signup" 
                  className="bg-gradient-primary text-white px-6 py-3 rounded-xl font-semibold text-center"
                >
                  Get Started
                </Link>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32">
        <div className="absolute inset-0 bg-gradient-mesh opacity-60"></div>
        <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-primary-300/30 to-transparent rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-0 w-80 h-80 bg-gradient-to-br from-primary-200/30 to-transparent rounded-full blur-3xl"></div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex justify-center mb-8">
              <div className="flex items-center space-x-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full border border-primary-200">
                <Zap className="w-4 h-4 text-primary-600" />
                <span className="text-sm font-semibold text-primary-700">AI-Powered Legal Guidance</span>
              </div>
            </div>
            
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-surface-900 mb-6 leading-tight">
              Smart Legal Solutions for
              <span className="block text-transparent bg-clip-text bg-gradient-primary">
                Everyone
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-surface-700 mb-10 max-w-4xl mx-auto leading-relaxed">
              Cyberlex AI uses advanced artificial intelligence to help you navigate cybercrime laws, 
              IT Act provisions, and data protection regulations with confidence and clarity.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link 
                href="/auth/signup" 
                className="bg-gradient-primary text-white px-8 py-4 rounded-xl font-bold text-lg shadow-large hover:shadow-glow transition-all duration-300 transform hover:scale-105 flex items-center space-x-2"
              >
                <span>Get Started Free</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link 
                href="/auth/login" 
                className="text-surface-800 hover:text-primary-600 font-semibold text-lg transition-colors flex items-center space-x-2"
              >
                <span>Sign In</span>
              </Link>
            </div>
            
            {/* Stats Preview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-16 max-w-4xl mx-auto">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl md:text-4xl font-bold text-surface-900 mb-2">{stat.number}</div>
                  <div className="text-sm font-semibold text-surface-700 mb-1">{stat.label}</div>
                  <div className="text-xs text-surface-600">{stat.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="flex justify-center mb-4">
              <div className="w-12 h-12 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-medium">
                <Scale className="w-7 h-7 text-white" />
              </div>
            </div>
            <h2 className="text-3xl md:text-5xl font-bold text-surface-900 mb-6">
              Comprehensive Legal Guidance
            </h2>
            <p className="text-xl text-surface-600 max-w-3xl mx-auto">
              From cybercrime reporting to data protection compliance, get expert legal assistance 
              powered by AI technology and extensive case law databases.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div 
                key={index} 
                className="bg-gradient-card p-8 rounded-2xl border border-surface-200 hover:shadow-large transition-all duration-300 transform hover:-translate-y-2 group"
              >
                <div className="w-14 h-14 bg-gradient-primary rounded-2xl flex items-center justify-center mb-6 shadow-medium group-hover:shadow-glow transition-all duration-300">
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-surface-900 mb-4">{feature.title}</h3>
                <p className="text-surface-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 bg-gradient-to-r from-primary-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <div className="flex items-center space-x-2 mb-6">
                <Gavel className="w-6 h-6 text-primary-600" />
                <span className="text-primary-600 font-semibold text-lg">About Cyberlex AI</span>
              </div>
              
              <h2 className="text-3xl md:text-5xl font-bold text-surface-900 mb-6">
                Legal Technology for the Digital Age
              </h2>
              
              <p className="text-lg text-surface-600 mb-8 leading-relaxed">
                Cyberlex AI bridges the gap between complex legal frameworks and practical understanding. 
                Our platform combines artificial intelligence with comprehensive legal databases to provide 
                accurate, timely, and actionable legal guidance.
              </p>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-6 h-6 text-secondary-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-surface-900">IT Act 2000 Expertise</h4>
                    <p className="text-surface-600">Complete coverage of cybercrime laws and amendments</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-6 h-6 text-secondary-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-surface-900">Data Protection Compliance</h4>
                    <p className="text-surface-600">GDPR, DPDPA 2023, and privacy regulation guidance</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <CheckCircle className="w-6 h-6 text-secondary-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-surface-900">Real Case Analysis</h4>
                    <p className="text-surface-600">Learn from actual cybercrime cases and precedents</p>
                  </div>
                </div>
              </div>
              
              <Link 
                href="/auth/signup" 
                className="bg-gradient-primary text-white px-8 py-4 rounded-xl font-bold text-lg shadow-medium hover:shadow-glow transition-all duration-300 transform hover:scale-105 inline-flex items-center space-x-2"
              >
                <span>Start Learning</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
            
            <div className="lg:pl-8">
              <div className="bg-white rounded-3xl p-8 shadow-large border border-surface-200">
                <div className="space-y-6">
                  <div className="flex items-center justify-between p-4 bg-primary-50 rounded-xl">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-surface-900">Legal Accuracy</h4>
                        <p className="text-surface-600 text-sm">AI-powered precision</p>
                      </div>
                    </div>
                    <span className="text-2xl font-bold text-primary-600">99%</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-secondary-50 rounded-xl">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-secondary-500 rounded-full flex items-center justify-center">
                        <Globe className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-surface-900">Cases Analyzed</h4>
                        <p className="text-surface-600 text-sm">Comprehensive database</p>
                      </div>
                    </div>
                    <span className="text-2xl font-bold text-secondary-600">10K+</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 bg-surface-50 rounded-xl">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-surface-500 rounded-full flex items-center justify-center">
                        <Lock className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-surface-900">Data Security</h4>
                        <p className="text-surface-600 text-sm">Enterprise-grade protection</p>
                      </div>
                    </div>
                    <span className="text-2xl font-bold text-surface-600">100%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="flex justify-center mb-4">
              <div className="w-12 h-12 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-medium">
                <Users className="w-7 h-7 text-white" />
              </div>
            </div>
            <h2 className="text-3xl md:text-5xl font-bold text-surface-900 mb-6">
              Trusted by Legal Professionals
            </h2>
            <p className="text-xl text-surface-600 max-w-3xl mx-auto">
              Join thousands of lawyers, consultants, and compliance officers who rely on 
              Cyberlex AI for accurate legal guidance.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div 
                key={index} 
                className="bg-gradient-card p-8 rounded-2xl border border-surface-200 hover:shadow-large transition-all duration-300"
              >
                <div className="flex items-center space-x-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-primary-500 fill-current" />
                  ))}
                </div>
                <p className="text-surface-700 mb-6 leading-relaxed italic">
                  "{testimonial.content}"
                </p>
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gradient-primary rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold text-lg">
                      {testimonial.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-surface-900">{testimonial.name}</h4>
                    <p className="text-surface-600 text-sm">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-primary">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
              Ready to Navigate CyberLaw with Confidence?
            </h2>
            <p className="text-xl text-primary-100 mb-10 leading-relaxed">
              Join thousands of legal professionals who trust Cyberlex AI for accurate, 
              timely legal guidance. Start your free trial today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link 
                href="/auth/signup" 
                className="bg-white text-primary-600 px-8 py-4 rounded-xl font-bold text-lg shadow-large hover:shadow-glow transition-all duration-300 transform hover:scale-105 flex items-center space-x-2"
              >
                <span>Get Started Free</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link 
                href="/auth/login" 
                className="text-white hover:text-primary-100 font-semibold text-lg transition-colors flex items-center space-x-2 border border-white/20 px-8 py-4 rounded-xl hover:bg-white/10"
              >
                <MessageCircle className="w-5 h-5" />
                <span>Try Demo</span>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer id="contact" className="bg-surface-900 text-surface-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Logo and Description */}
            <div className="md:col-span-2">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-12 h-12 bg-gradient-primary rounded-xl flex items-center justify-center shadow-medium">
                  <Scale className="w-7 h-7 text-white" />
                </div>
                <div>
                  <span className="font-bold text-2xl text-white">Cyberlex AI</span>
                  <p className="text-surface-400 font-medium">Legal Assistant</p>
                </div>
              </div>
              <p className="text-surface-400 leading-relaxed max-w-md">
                Empowering legal professionals and individuals with AI-powered cybercrime law guidance, 
                data protection compliance, and comprehensive legal research tools.
              </p>
            </div>
            
            {/* Legal Topics */}
            <div>
              <h3 className="font-bold text-white mb-4">Legal Topics</h3>
              <ul className="space-y-3">
                <li><Link href="#" className="hover:text-primary-400 transition-colors">IT Act 2000</Link></li>
                <li><Link href="#" className="hover:text-primary-400 transition-colors">Cybercrime Laws</Link></li>
                <li><Link href="#" className="hover:text-primary-400 transition-colors">Data Protection</Link></li>
                <li><Link href="#" className="hover:text-primary-400 transition-colors">Privacy Rights</Link></li>
                <li><Link href="#" className="hover:text-primary-400 transition-colors">Legal Procedures</Link></li>
              </ul>
            </div>
            
            {/* Company */}
            <div>
              <h3 className="font-bold text-white mb-4">Company</h3>
              <ul className="space-y-3">
                <li><Link href="#about" className="hover:text-primary-400 transition-colors">About Us</Link></li>
                <li><Link href="#features" className="hover:text-primary-400 transition-colors">Features</Link></li>
                <li><Link href="#testimonials" className="hover:text-primary-400 transition-colors">Reviews</Link></li>
                <li><Link href="/auth/signup" className="hover:text-primary-400 transition-colors">Get Started</Link></li>
                <li><Link href="/auth/login" className="hover:text-primary-400 transition-colors">Sign In</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-surface-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-surface-500 text-sm">
              © 2025 Cyberlex AI. All rights reserved. Empowering legal clarity.
            </p>
            <div className="flex items-center space-x-6 mt-4 md:mt-0">
              <Link href="#" className="text-surface-500 hover:text-primary-400 transition-colors text-sm">
                Privacy Policy
              </Link>
              <Link href="#" className="text-surface-500 hover:text-primary-400 transition-colors text-sm">
                Terms of Service
              </Link>
              <Link href="#" className="text-surface-500 hover:text-primary-400 transition-colors text-sm">
                Legal Disclaimer
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}