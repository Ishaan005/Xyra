"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight, Shield, Zap } from "lucide-react"

export function CTASection() {
  return (
    <section className="py-20 bg-gradient-to-br from-gold via-purple to-blue relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-white/10 blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-white/10 blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div className="container mx-auto relative px-4 md:px-6">
        <div className="text-center text-white">
          <h2 className="text-4xl md:text-6xl font-bold mb-8 flex items-center justify-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                <div className="w-8 h-8 bg-gradient-to-tr from-white via-gold to-purple rounded-full animate-bounce"></div>
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-white/30 rounded-full animate-ping"></div>
              <div className="absolute -bottom-1 -left-2 w-4 h-4 bg-gold/50 rounded-full animate-pulse delay-500"></div>
            </div>
            Stop leaving money on the table.
          </h2>
          <p className="text-2xl md:text-3xl mb-12 opacity-90">Start charging what your AI is actually worth.</p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
            <Button
              size="lg"
              className="bg-white text-gray-dark hover:bg-gray-20 font-bold text-xl px-12 py-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
            >
              <Zap className="mr-2 h-6 w-6" />
              Get Lifetime Access Now
              <ArrowRight className="ml-2 h-6 w-6" />
            </Button>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 max-w-2xl mx-auto border border-white/20">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Shield className="h-8 w-8" />
              <h3 className="text-2xl font-bold">60-Day Money-Back Guarantee</h3>
            </div>
            <p className="text-lg opacity-90">
              If OutcomeAI doesn't help you increase your revenue within 60 days, we'll refund every penny. We're that
              confident.
            </p>
          </div>

          <div className="mt-12">
            <p className="text-lg opacity-75 mb-4">
              P.S. Remember, only 47 codes left at this price. When they're gone, they're gone for good!
            </p>
          </div>
        </div>
      </div>

      {/* Bottom banner */}
      <div className="absolute bottom-0 left-0 right-0 bg-gray-dark text-white py-6">
        <div className="container mx-auto px-4 md:px-6">
          <div className="text-center">
            <p className="text-xl font-bold mb-4 flex items-center justify-center gap-3">
              <div className="relative">
                <div className="w-8 h-8 bg-gradient-to-r from-gold via-yellow-500 to-orange-500 rounded-full animate-bounce"></div>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-gold rounded-full animate-ping"></div>
                <div className="absolute top-1 left-1 w-2 h-2 bg-white rounded-full animate-pulse"></div>
              </div>
              Join 300+ AI companies already crushing it with outcome-based pricing
            </p>
            <Button className="bg-gold hover:bg-gold-dark text-white font-bold text-lg px-8 py-3 rounded-xl transition-all duration-300 transform hover:scale-105">
              Claim Your Lifetime Deal Before It's Gone
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
