"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight, Zap } from "lucide-react"
import { useEffect, useState } from "react"

export function HeroSection() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
  }, [])

  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-white via-gold-20 to-purple-20 py-20 md:py-32">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-gold/10 blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-purple/10 blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 h-60 w-60 rounded-full bg-blue/5 blur-2xl animate-bounce delay-500"></div>
      </div>

      <div className="container mx-auto relative px-4 md:px-6">
        <div className="mx-auto max-w-4xl text-center">
          {/* Animated badge with rocket effect */}
          <div
            className={`inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-gold/10 to-gold/20 px-4 py-2 text-sm font-medium text-gold-dark mb-8 transition-all duration-1000 border border-gold/30 shadow-md hover:shadow-lg ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}
          >
            <div className="relative">
              <Zap className="h-4 w-4 animate-pulse" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-gold rounded-full animate-ping"></div>
            </div>
            <span className="bg-gradient-to-r from-gold-dark to-gold bg-clip-text text-transparent font-semibold">
              Stop Charging for Seats Nobody Uses
            </span>
          </div>

          {/* Main headline with staggered animation */}
          <h1
            className={`text-4xl font-bold tracking-tight sm:text-6xl md:text-7xl lg:text-8xl mb-8 transition-all duration-1000 delay-200 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            <span className="block text-gray-dark">Start Charging for</span>
            <span className="block bg-gradient-to-r from-gold via-purple to-blue bg-clip-text text-transparent animate-pulse">
              Results That Matter
            </span>
          </h1>

          {/* Subheader */}
          <p
            className={`text-xl md:text-2xl text-gray-dark mb-12 max-w-3xl mx-auto transition-all duration-1000 delay-400 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            Your AI agents are worth more than a monthly subscription fee.{" "}
            <span className="font-bold text-purple">Xyra</span> helps you charge for what your AI actually
            accomplishes — <span className="font-bold text-gold-dark">boosting revenue by 32% on average</span> while
            your customers only pay for real value.
          </p>

          {/* Problem statement with animation */}
          <div
            className={`bg-white/80 backdrop-blur-sm rounded-2xl p-8 mb-12 border border-gold/20 shadow-lg transition-all duration-1000 delay-600 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            <h2 className="text-2xl font-bold text-gray-dark mb-4">
              <span className="relative inline-block">
                The old way of pricing AI is
                <span className="relative mx-2">
                  <span className="relative z-10 text-destructive line-through decoration-4 decoration-destructive/70 animate-pulse">
                    broken
                  </span>
                  <div className="absolute inset-0 bg-destructive/10 transform rotate-1 rounded-md -z-10"></div>
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-destructive/20 rounded-full animate-bounce delay-300"></div>
                  <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-destructive/30 rounded-full animate-bounce delay-500"></div>
                </span>
              </span>
            </h2>
            <div className="text-lg text-gray-dark mb-4">
              You built an amazing AI agent. Then you slapped a per-seat price on it because... that's what everyone
              does?
            </div>
            <div className="grid md:grid-cols-2 gap-6 mt-6">
              <div className="text-left relative">
                <div className="absolute -left-4 top-0 w-1 h-full bg-gradient-to-b from-destructive to-destructive/50 rounded-full"></div>
                <div className="font-bold text-destructive mb-2 flex items-center gap-2">
                  <div className="relative w-6 h-6">
                    {/* Cross/X mark for "broken" */}
                    <div className="absolute inset-1 w-4 h-0.5 bg-destructive rounded-full transform rotate-45"></div>
                    <div className="absolute inset-1 w-4 h-0.5 bg-destructive rounded-full transform -rotate-45"></div>
                    <div className="absolute inset-0 border-2 border-destructive rounded-full animate-pulse"></div>
                  </div>
                  Here's the problem:
                </div>
                <div className="text-gray-dark">
                  Your customers are paying the same whether your AI crushes it or naps on the job.
                </div>
              </div>
              <div className="text-left relative">
                <div className="absolute -left-4 top-0 w-1 h-full bg-gradient-to-b from-destructive via-orange-500 to-yellow-500 rounded-full animate-pulse"></div>
                <div className="font-bold text-destructive mb-2 flex items-center gap-2">
                  <div className="relative w-6 h-6">
                    {/* Money/cash leaving animation */}
                    <div className="absolute inset-0">
                      <div className="w-4 h-3 bg-gradient-to-r from-green-500 to-green-600 rounded-sm"></div>
                      <div className="absolute top-0 left-4 w-1 h-1 bg-green-500 rounded-full animate-ping"></div>
                      <div className="absolute top-1 left-5 w-0.5 h-0.5 bg-green-400 rounded-full animate-ping delay-200"></div>
                      <div className="text-xs text-green-600 absolute -bottom-2 left-0">$$$</div>
                    </div>
                  </div>
                  Here's the bigger problem:
                </div>
                <div className="text-gray-dark">You're leaving piles of cash on the table.</div>
              </div>
            </div>
          </div>

          {/* Solution statement */}
          <div
            className={`bg-gradient-to-r from-gold/10 to-purple/10 rounded-2xl p-8 mb-12 border border-purple/20 transition-all duration-1000 delay-800 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            <div className="text-xl text-gray-dark mb-4">
              <span className="font-bold text-purple">Xyra</span> is like having a financial advisor, data
              scientist, and billing expert working 24/7 to monetize your AI based on the actual outcomes it delivers.
            </div>
            <div className="text-lg font-bold text-gold-dark flex items-center justify-center gap-3">
              Think Stripe and Google Analytics had a baby that's obsessed with making your AI profitable.
              <div className="relative">
                {/* Baby/fusion animation - representing the "baby" metaphor */}
                <div className="flex items-center gap-1">
                  {/* Stripe (payment) representation */}
                  <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full animate-bounce"></div>
                  {/* Plus sign */}
                  <div className="text-xs text-gray-500">+</div>
                  {/* Analytics representation */}
                  <div className="w-3 h-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-full animate-bounce delay-200"></div>
                  {/* Equals sign */}
                  <div className="text-xs text-gray-500">=</div>
                  {/* Result (geometric heart shape) */}
                  <div className="relative">
                    <div className="w-3 h-3 bg-gradient-to-br from-gold to-purple rounded-full animate-bounce delay-300"></div>
                    <div className="absolute -top-0.5 -left-0.5 w-2 h-2 bg-gradient-to-br from-purple to-gold rounded-full animate-pulse delay-500"></div>
                    <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-gradient-to-br from-gold to-purple rounded-full animate-pulse delay-500"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* CTA buttons */}
          <div
            className={`flex flex-col sm:flex-row gap-4 justify-center transition-all duration-1000 delay-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            <Button
              size="lg"
              className="bg-gradient-to-r from-gold to-gold-dark hover:from-gold-dark hover:to-gold text-white font-bold text-lg px-8 py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
            >
              Get Lifetime Access Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-2 border-purple text-purple hover:bg-purple hover:text-white font-bold text-lg px-8 py-4 rounded-xl transition-all duration-300 transform hover:scale-105"
            >
              Watch Demo
            </Button>
          </div>

          {/* Stats */}
          <div
            className={`grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 transition-all duration-1000 delay-1200 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
          >
            <div className="text-center">
              <div className="text-3xl font-bold text-gold-dark mb-2">32%</div>
              <div className="text-gray-dark">Average Revenue Increase</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple mb-2">68%</div>
              <div className="text-gray-dark">Fewer Pricing Objections</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue mb-2">2.4x</div>
              <div className="text-gray-dark">Longer Customer Retention</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
