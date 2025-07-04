"use client"

import { Clock, Link, Eye } from "lucide-react"
import { useEffect, useRef, useState } from "react"

export function HowItWorksSection() {
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

  const steps = [
    {
      icon: Clock,
      title: "1. Define Your Outcomes",
      subtitle: "(10 minutes)",
      description:
        "Tell us what success looks like for your AI agent. Is it generating leads? Saving time? Closing deals? We'll help you define and track it.",
      color: "gold",
      delay: 0,
    },
    {
      icon: Link,
      title: "2. Connect Your Systems",
      subtitle: "(1 hour)",
      description: "Plug Xyra into your existing stack with our no-code connectors. We play nice with everyone.",
      color: "purple",
      delay: 200,
    },
    {
      icon: Eye,
      title: "3. Watch the Magic Happen",
      subtitle: "(forever)",
      description:
        "Our platform tracks outcomes, attributes results, calculates charges, and shows beautiful dashboards to you and your customers.",
      color: "blue",
      delay: 400,
    },
  ]

  return (
    <section ref={sectionRef} className="py-20 bg-gradient-to-br from-blue-20 via-teal-20 to-purple-20">
      <div className="container mx-auto px-4 md:px-6">
        <div
          className={`text-center mb-16 transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-dark mb-4 flex items-center justify-center gap-4">
            <div className="relative">
              {/* Step-by-step workflow visualization */}
              <div className="w-12 h-12 bg-gradient-to-br from-blue/20 to-teal/40 rounded-lg flex items-center justify-center border border-blue/8 ring-1 ring-blue/5">
                <div className="flex items-center gap-1">
                  {/* Step 1: Clock (Define) */}
                  <div className="relative w-2 h-2">
                    <div className="w-2 h-2 bg-gold rounded-full animate-pulse"></div>
                    <div className="absolute top-0.5 left-0.5 w-0.5 h-0.5 bg-white rounded-full"></div>
                  </div>
                  {/* Arrow */}
                  <div className="w-1 h-0.5 bg-gradient-to-r from-gold to-purple animate-pulse delay-200"></div>
                  {/* Step 2: Link (Connect) */}
                  <div className="w-2 h-2 border border-purple rounded-full animate-pulse delay-400 flex items-center justify-center">
                    <div className="w-1 h-1 bg-purple rounded-full"></div>
                  </div>
                  {/* Arrow */}
                  <div className="w-1 h-0.5 bg-gradient-to-r from-purple to-blue animate-pulse delay-600"></div>
                  {/* Step 3: Eye (Watch) */}
                  <div className="relative w-2 h-1 bg-blue rounded-full animate-pulse delay-800">
                    <div className="absolute top-0 left-0.5 w-1 h-1 bg-white rounded-full"></div>
                  </div>
                </div>
              </div>
              <div className="absolute -top-2 -right-2 w-3 h-3 bg-blue/60 rounded-full animate-ping"></div>
              <div className="absolute -bottom-1 -left-2 w-2 h-2 bg-teal/50 rounded-full animate-bounce delay-300"></div>
            </div>
            How It Works <span className="text-blue">(It's Ridiculously Simple)</span>
          </h2>
        </div>

        <div className="max-w-4xl mx-auto">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`relative mb-12 last:mb-0 transition-all duration-1000 ${
                isVisible ? "opacity-100 translate-x-0" : "opacity-0 translate-x-8"
              }`}
              style={{ transitionDelay: `${step.delay}ms` }}
            >
              {/* Connection line */}
              {index < steps.length - 1 && (
                <div className="absolute left-8 top-20 h-16 w-0.5 bg-gradient-to-b from-gray-40 to-transparent hidden md:block"></div>
              )}

              <div className="flex flex-col md:flex-row items-start gap-8">
                <div
                  className={`flex-shrink-0 h-16 w-16 rounded-full bg-${step.color}/10 flex items-center justify-center border border-${step.color}/8 ring-1 ring-${step.color}/5 relative`}
                >
                  <step.icon className={`h-8 w-8 text-${step.color}`} />
                  {/* Content-specific animations for each step */}
                  {step.color === "gold" && (
                    <>
                      {/* Clock hands moving for "Define" */}
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-3 h-0.5 bg-gold/50 absolute transform rotate-45 origin-left animate-spin"></div>
                        <div className="w-2 h-0.5 bg-gold/70 absolute transform rotate-90 origin-left animate-pulse"></div>
                      </div>
                    </>
                  )}
                  {step.color === "purple" && (
                    <>
                      {/* Chain links connecting for "Connect" */}
                      <div className="absolute -top-2 -right-2 w-3 h-3 border border-purple/15 rounded-full animate-pulse"></div>
                      <div className="absolute -bottom-2 -left-2 w-3 h-3 border border-purple/15 rounded-full animate-pulse delay-200"></div>
                      <div className="absolute top-1 right-1 w-1 h-1 bg-purple/50 rounded-full animate-bounce"></div>
                    </>
                  )}
                  {step.color === "blue" && (
                    <>
                      {/* Eye blinking for "Watch" */}
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-1 h-1 bg-blue rounded-full animate-ping delay-1000"></div>
                      </div>
                      <div className="absolute -top-1 -right-1 w-2 h-2 bg-blue/30 rounded-full animate-pulse"></div>
                    </>
                  )}
                </div>

                <div className="flex-1">
                  <div
                    className={`bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-${step.color}/8 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 ring-1 ring-${step.color}/5 hover:ring-${step.color}/10`}
                  >
                    <h3 className="text-2xl font-bold text-gray-dark mb-2">{step.title}</h3>
                    <div className={`text-lg font-medium text-${step.color} mb-4`}>{step.subtitle}</div>
                    <p className="text-lg text-gray-dark leading-relaxed">{step.description}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
