"use client"

import { DollarSign, Settings, TrendingUp, Brain } from "lucide-react"
import { useEffect, useRef, useState } from "react"

export function BenefitsSection() {
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.1 },
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => observer.disconnect()
  }, [])

  const benefits = [
    {
      icon: DollarSign,
      title: "Charge for Results, Not Access",
      before: '"That\'ll be $49/month per user, please!"',
      after: '"We\'ll take a small cut when our AI saves you $10K in operational costs."',
      color: "gold",
      delay: 0,
    },
    {
      icon: Settings,
      title: "Zero Technical Headaches",
      points: [
        "Track outcomes automatically without rebuilding your entire stack",
        "Implement in days, not months (our record is 4 days!)",
        "Pre-built integrations with Stripe, Salesforce, HubSpot, and 20+ more",
      ],
      color: "blue",
      delay: 200,
    },
    {
      icon: TrendingUp,
      title: "Watch Your Revenue Skyrocket",
      points: [
        "Our customers see 32% higher revenue on average",
        "68% reduction in pricing objections during sales calls",
        "2.4x longer customer retention (they stay when they're paying for value!)",
      ],
      color: "purple",
      delay: 400,
    },
    {
      icon: Brain,
      title: "AI-Native Attribution That Actually Works",
      points: [
        "Multi-factor attribution that connects AI actions to real business outcomes",
        "No more guessing which AI interaction led to that conversion",
        "Built by the same folks who designed attribution for [redacted big tech company]",
      ],
      color: "teal",
      delay: 600,
    },
  ]

  return (
    <>
      <style jsx>{`
        @keyframes drawCheck {
          0% { stroke-dashoffset: 20; }
          50% { stroke-dashoffset: 0; }
          100% { stroke-dashoffset: 20; }
        }
        .reverse-spin {
          animation: spin 1s linear infinite reverse;
        }
      `}</style>
      <section ref={sectionRef} className="py-20 bg-white">
      <div className="container mx-auto px-4 md:px-6">
        <div
          className={`text-center mb-16 transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-dark mb-4 flex items-center justify-center gap-4">
            <div className="relative">
              {/* Checkmark animation - represents "benefits verified" */}
              <div className="w-12 h-12 bg-gradient-to-r from-success/20 to-success/40 rounded-full flex items-center justify-center border border-success/8 ring-1 ring-success/5">
                <svg className="w-6 h-6 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={3} 
                    d="M5 13l4 4L19 7"
                    className="animate-pulse"
                    strokeDasharray="20"
                    strokeDashoffset="20"
                    style={{
                      animation: 'drawCheck 2s ease-in-out infinite'
                    }}
                  />
                </svg>
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-success/50 rounded-full animate-bounce"></div>
              <div className="absolute -bottom-1 -left-1 w-3 h-3 bg-success/30 rounded-full animate-bounce delay-200"></div>
            </div>
            Why Xyra?
          </h2>
        </div>

        <div className="grid gap-8 md:grid-cols-2">
          {benefits.map((benefit, index) => (
            <div
              key={index}
              className={`group relative overflow-hidden rounded-2xl border ${
                benefit.color === "gold" ? "border-gold/8 bg-gradient-to-br from-white to-gold-20" :
                benefit.color === "blue" ? "border-blue/8 bg-gradient-to-br from-white to-blue-20" :
                benefit.color === "purple" ? "border-purple/8 bg-gradient-to-br from-white to-purple-20" :
                benefit.color === "teal" ? "border-teal/8 bg-gradient-to-br from-white to-teal-20" : 
                "border-gray/8 bg-gradient-to-br from-white to-gray-20"
              } p-8 shadow-lg transition-all duration-1000 hover:shadow-xl hover:scale-105 ring-1 ${
                benefit.color === "gold" ? "ring-gold/5 hover:ring-gold/10" :
                benefit.color === "blue" ? "ring-blue/5 hover:ring-blue/10" :
                benefit.color === "purple" ? "ring-purple/5 hover:ring-purple/10" :
                benefit.color === "teal" ? "ring-teal/5 hover:ring-teal/10" : 
                "ring-gray/5 hover:ring-gray/10"
              } ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
              }`}
              style={{ transitionDelay: `${benefit.delay}ms` }}
            >
              <div className="absolute top-0 right-0 h-32 w-32 translate-x-8 -translate-y-8 rounded-full bg-gradient-to-br from-transparent to-white/20"></div>

              <div
                className={`mb-6 inline-flex h-16 w-16 items-center justify-center rounded-full ${
                  benefit.color === "gold" ? "bg-gold/10" :
                  benefit.color === "blue" ? "bg-blue/10" :
                  benefit.color === "purple" ? "bg-purple/10" :
                  benefit.color === "teal" ? "bg-teal/10" : 
                  "bg-gray/10"
                }`}
              >
                <benefit.icon className={`h-8 w-8 ${
                  benefit.color === "gold" ? "text-gold" :
                  benefit.color === "blue" ? "text-blue" :
                  benefit.color === "purple" ? "text-purple" :
                  benefit.color === "teal" ? "text-teal" : 
                  "text-gray"
                }`} />
              </div>

              <h3 className="text-2xl font-bold text-gray-dark mb-4 flex items-center gap-3">
                {benefit.color === "gold" && (
                  <div className="relative">
                    {/* Money/Revenue growing animation */}
                    <div className="flex items-end gap-1">
                      <div className="w-2 h-4 bg-gradient-to-t from-gold to-yellow-500 rounded-sm animate-pulse"></div>
                      <div className="w-2 h-6 bg-gradient-to-t from-gold to-yellow-500 rounded-sm animate-pulse delay-100"></div>
                      <div className="w-2 h-8 bg-gradient-to-t from-gold to-yellow-500 rounded-sm animate-pulse delay-200"></div>
                    </div>
                    <div className="absolute -top-1 -right-1 text-xs text-gold animate-bounce">$</div>
                  </div>
                )}
                {benefit.color === "blue" && (
                  <div className="relative">
                    {/* Gears/automation working */}
                    <div className="w-6 h-6 relative">
                      <div className="absolute inset-0 border-2 border-blue rounded-full animate-spin"></div>
                      <div className="absolute top-1 left-1 w-4 h-4 border-2 border-blue-dark rounded-full animate-spin reverse-spin"></div>
                      <div className="absolute top-2 left-2 w-2 h-2 bg-blue rounded-full"></div>
                    </div>
                  </div>
                )}
                {benefit.color === "purple" && (
                  <div className="relative">
                    {/* Rocket/growth trajectory */}
                    <div className="w-6 h-6 transform rotate-45 relative">
                      <div className="w-4 h-6 bg-gradient-to-t from-purple to-purple-light rounded-t-full relative">
                        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-1 h-2 bg-orange-400 rounded-full animate-pulse"></div>
                      </div>
                      <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-purple/30 rounded-full animate-ping"></div>
                    </div>
                  </div>
                )}
                {benefit.color === "teal" && (
                  <div className="relative">
                    {/* Brain/neural network */}
                    <div className="w-6 h-6 relative">
                      <div className="absolute top-1 left-1 w-2 h-2 bg-teal rounded-full animate-pulse"></div>
                      <div className="absolute top-1 right-1 w-2 h-2 bg-teal rounded-full animate-pulse delay-200"></div>
                      <div className="absolute bottom-1 left-2 w-2 h-2 bg-teal rounded-full animate-pulse delay-400"></div>
                      {/* Neural connections */}
                      <div className="absolute top-2 left-2 w-2 h-0.5 bg-teal/50 transform rotate-45 animate-pulse delay-100"></div>
                      <div className="absolute top-2 right-2 w-2 h-0.5 bg-teal/50 transform -rotate-45 animate-pulse delay-300"></div>
                    </div>
                  </div>
                )}
                {benefit.title}
              </h3>

              {benefit.before && benefit.after ? (
                <div className="space-y-4">
                  <div className="rounded-lg bg-destructive/10 p-4 border-l-4 border-destructive">
                    <p className="font-medium text-destructive mb-1">Before:</p>
                    <p className="text-gray-dark italic">{benefit.before}</p>
                  </div>
                  <div className="rounded-lg bg-success/10 p-4 border-l-4 border-success">
                    <p className="font-medium text-success mb-1">After:</p>
                    <p className="text-gray-dark italic">{benefit.after}</p>
                  </div>
                </div>
              ) : (
                <ul className="space-y-3">
                  {benefit.points?.map((point, pointIndex) => (
                    <li key={pointIndex} className="flex items-start gap-3">
                      <div className={`mt-1 h-2 w-2 rounded-full flex-shrink-0 ${
                        benefit.color === "gold" ? "bg-gold" :
                        benefit.color === "blue" ? "bg-blue" :
                        benefit.color === "purple" ? "bg-purple" :
                        benefit.color === "teal" ? "bg-teal" : 
                        "bg-gray"
                      }`}></div>
                      <p className="text-gray-dark">{point}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
    </>
  )
}
