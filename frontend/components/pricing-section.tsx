"use client"

import { Button } from "@/components/ui/button"
import { Check, Clock, Zap } from "lucide-react"
import { useEffect, useState } from "react"

export function PricingSection() {
  const [timeLeft, setTimeLeft] = useState({
    days: 2,
    hours: 7,
    minutes: 23,
    seconds: 45,
  })

  const [codesLeft] = useState(47)

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev.seconds > 0) {
          return { ...prev, seconds: prev.seconds - 1 }
        } else if (prev.minutes > 0) {
          return { ...prev, minutes: prev.minutes - 1, seconds: 59 }
        } else if (prev.hours > 0) {
          return { ...prev, hours: prev.hours - 1, minutes: 59, seconds: 59 }
        } else if (prev.days > 0) {
          return { ...prev, days: prev.days - 1, hours: 23, minutes: 59, seconds: 59 }
        }
        return prev
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  return (
    <section className="py-20 bg-gradient-to-br from-gold-20 via-purple-20 to-blue-20">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-dark mb-4">
            💰 What You'd Normally Pay vs. <span className="text-gold">What You'll Pay Today</span>
          </h2>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
          {/* Normal Pricing */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-gray/15 shadow-lg ring-1 ring-gray/10">
            <h3 className="text-2xl font-bold text-gray-dark mb-6">What You'd Normally Pay:</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center py-3 border-b border-gray/10">
                <span className="text-gray-dark">Enterprise pricing platforms:</span>
                <span className="font-bold text-destructive">$50K+ per year</span>
              </div>
              <div className="flex justify-between items-center py-3 border-b border-gray/10">
                <span className="text-gray-dark">Custom development:</span>
                <span className="font-bold text-destructive">$200K+ and 6 months</span>
              </div>
              <div className="flex justify-between items-center py-3">
                <span className="text-gray-dark">Hiring a pricing consultant:</span>
                <span className="font-bold text-destructive">$25K per engagement</span>
              </div>
            </div>
          </div>

          {/* Our Pricing */}
          <div className="relative bg-gradient-to-br from-gold/10 to-purple/10 rounded-2xl p-8 border border-gold/8 shadow-xl transform hover:scale-105 transition-all duration-300 ring-1 ring-gold/5 hover:ring-gold/10">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
              <div className="bg-gold text-white px-6 py-2 rounded-full font-bold text-sm">🔥 LIMITED TIME OFFER</div>
            </div>

            <h3 className="text-2xl font-bold text-gray-dark mb-6 mt-4">What You'll Pay Today:</h3>

            <div className="text-center mb-8">
              <div className="text-6xl font-bold text-gold mb-2">$499</div>
              <div className="text-xl text-gray-dark">one-time payment for lifetime access!</div>
              <div className="text-sm text-gray-60 line-through mt-2">Regular price: $999</div>
            </div>

            {/* Countdown Timer */}
            <div className="bg-white/80 rounded-xl p-6 mb-8 border border-gold/15 ring-1 ring-gold/5">
              <div className="flex items-center justify-center gap-2 mb-4">
                <Clock className="h-5 w-5 text-gold" />
                <span className="font-bold text-gray-dark">Deal expires in:</span>
              </div>
              <div className="grid grid-cols-4 gap-2 text-center">
                <div className="bg-gold/10 rounded-lg p-3">
                  <div className="text-2xl font-bold text-gold">{timeLeft.days}</div>
                  <div className="text-xs text-gray-dark">Days</div>
                </div>
                <div className="bg-gold/10 rounded-lg p-3">
                  <div className="text-2xl font-bold text-gold">{timeLeft.hours}</div>
                  <div className="text-xs text-gray-dark">Hours</div>
                </div>
                <div className="bg-gold/10 rounded-lg p-3">
                  <div className="text-2xl font-bold text-gold">{timeLeft.minutes}</div>
                  <div className="text-xs text-gray-dark">Minutes</div>
                </div>
                <div className="bg-gold/10 rounded-lg p-3">
                  <div className="text-2xl font-bold text-gold">{timeLeft.seconds}</div>
                  <div className="text-xs text-gray-dark">Seconds</div>
                </div>
              </div>
            </div>

            {/* Includes */}
            <div className="mb-8">
              <h4 className="font-bold text-gray-dark mb-4">Includes:</h4>
              <div className="space-y-3">
                {[
                  "Core OutcomeAI platform",
                  "Unlimited outcome definitions",
                  "Customer-facing dashboards",
                  "5 standard integrations",
                  "Up to 10,000 monthly outcomes",
                ].map((feature, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <Check className="h-5 w-5 text-success" />
                    <span className="text-gray-dark">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Bonuses */}
            <div className="bg-white/60 rounded-xl p-6 mb-8">
              <h4 className="font-bold text-purple mb-4">🎁 Plus, we're throwing in:</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-dark">Implementation support</span>
                  <span className="font-bold text-purple">$2,500 value</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-dark">Outcome definition workshop</span>
                  <span className="font-bold text-purple">$1,500 value</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-dark">12 months premium support</span>
                  <span className="font-bold text-purple">$1,200 value</span>
                </div>
              </div>
            </div>

            {/* Urgency */}
            <div className="text-center mb-6">
              <div className="text-sm text-destructive font-bold mb-2">⚡ Only {codesLeft} codes remaining!</div>
              <div className="text-sm text-gray-dark">
                First 20 buyers get a free 1-hour pricing strategy session ($500 value)
              </div>
            </div>

            <Button className="w-full bg-gradient-to-r from-gold to-gold-dark hover:from-gold-dark hover:to-gold text-white font-bold text-lg py-4 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
              <Zap className="mr-2 h-5 w-5" />
              Claim Your Lifetime Deal Now
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
