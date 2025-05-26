"use client"

import { Star, Quote } from "lucide-react"
import { useEffect, useRef, useState } from "react"

export function SocialProofSection() {
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

  const testimonials = [
    {
      quote:
        "We switched from seat-based to outcome-based pricing and saw a 47% revenue increase in 90 days. Our sales cycle also dropped from 45 days to 12. OutcomeAI paid for itself in the first week.",
      author: "Sarah J.",
      title: "CEO of PhantomWriter.io",
      color: "gold",
      delay: 0,
    },
    {
      quote:
        "I was skeptical about outcome-based pricing until our customers started ASKING to pay more because they could finally see the ROI. Implementation took 3 days and the OutcomeAI team was with us every step.",
      author: "Mark T.",
      title: "CRO at DataSynthAI",
      color: "purple",
      delay: 200,
    },
    {
      quote:
        "We were charging $99/seat and struggling to grow. With OutcomeAI, we now charge $0.50 per successful customer interaction plus $10 per conversion. Our revenue is up 62% and customers are happier.",
      author: "Priya M.",
      title: "Founder of SupportGPT",
      color: "blue",
      delay: 400,
    },
  ]

  return (
    <section ref={sectionRef} className="py-20 bg-white">
      <div className="container mx-auto px-4 md:px-6">
        <div
          className={`text-center mb-16 transition-all duration-1000 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
        >
          <h2 className="text-4xl md:text-5xl font-bold text-gray-dark mb-4 flex items-center justify-center gap-4">
            <div className="relative">
              {/* Speech bubble with stars - represents testimonials/reviews */}
              <div className="w-12 h-12 bg-gradient-to-br from-purple/20 to-purple/40 rounded-2xl flex items-center justify-center border border-purple/8 ring-1 ring-purple/5 relative">
                {/* Speech bubble tail */}
                <div className="absolute -bottom-1 left-3 w-2 h-2 bg-gradient-to-br from-purple/20 to-purple/40 transform rotate-45 border-r border-b border-purple/8"></div>
                {/* Stars inside bubble */}
                <div className="flex gap-0.5">
                  <div className="w-1.5 h-1.5 bg-gold transform rotate-45 animate-pulse"></div>
                  <div className="w-1.5 h-1.5 bg-gold transform rotate-45 animate-pulse delay-100"></div>
                  <div className="w-1.5 h-1.5 bg-gold transform rotate-45 animate-pulse delay-200"></div>
                </div>
              </div>
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-purple/50 rounded-full animate-bounce"></div>
              <div className="absolute -bottom-1 -left-1 w-3 h-3 bg-purple/30 rounded-full animate-bounce delay-200"></div>
            </div>
            <span className="text-purple">Real Results</span> from Real Customers
          </h2>
          <p className="text-xl text-gray-dark">Don't just take our word for it...</p>
        </div>

        <div className="grid gap-8 md:grid-cols-3 max-w-6xl mx-auto">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className={`group relative overflow-hidden rounded-2xl border border-${testimonial.color}/8 bg-gradient-to-br from-white to-${testimonial.color}-20 p-8 shadow-lg transition-all duration-1000 hover:shadow-xl hover:scale-105 ring-1 ring-${testimonial.color}/5 hover:ring-${testimonial.color}/10 ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
              }`}
              style={{ transitionDelay: `${testimonial.delay}ms` }}
            >
              <div className="absolute top-4 right-4 opacity-10">
                <Quote className="h-16 w-16" />
              </div>

              <div className="flex mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className={`h-5 w-5 fill-${testimonial.color} text-${testimonial.color}`} />
                ))}
              </div>

              <blockquote className="text-lg text-gray-dark mb-6 italic leading-relaxed">
                "{testimonial.quote}"
              </blockquote>

              <div className="flex items-center gap-4">
                <div className={`h-12 w-12 rounded-full bg-${testimonial.color}/20 flex items-center justify-center`}>
                  <span className={`text-xl font-bold text-${testimonial.color}`}>{testimonial.author.charAt(0)}</span>
                </div>
                <div>
                  <div className="font-bold text-gray-dark">{testimonial.author}</div>
                  <div className="text-sm text-gray-60">{testimonial.title}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Trust indicators */}
        <div
          className={`text-center mt-16 transition-all duration-1000 delay-600 ${isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`}
        >
          <div className="inline-flex items-center gap-4 bg-gradient-to-r from-gold/10 to-purple/10 rounded-full px-8 py-4 border border-gold/8 ring-1 ring-gold/5 hover:ring-gold/10 transition-all duration-300">
            <div className="relative">
              {/* Trophy/achievement formation */}
              <div className="w-8 h-8 relative">
                {/* Trophy cup */}
                <div className="w-6 h-4 bg-gradient-to-b from-gold to-yellow-500 rounded-t-full mx-auto"></div>
                {/* Trophy base */}
                <div className="w-4 h-1 bg-gold mx-auto mt-0.5"></div>
                <div className="w-6 h-1 bg-gold-dark mx-auto mt-0.5"></div>
                {/* Trophy handles */}
                <div className="absolute top-1 left-0 w-1 h-2 border-l-2 border-gold rounded-l-full"></div>
                <div className="absolute top-1 right-0 w-1 h-2 border-r-2 border-gold rounded-r-full"></div>
                {/* Shine effect */}
                <div className="absolute top-1 left-2 w-1 h-1 bg-white rounded-full animate-pulse"></div>
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-gold rounded-full animate-ping"></div>
            </div>
            <div className="text-lg font-bold text-gray-dark">
              Join 300+ AI companies already crushing it with outcome-based pricing
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
