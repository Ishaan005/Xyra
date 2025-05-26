"use client"

import { ChevronDown } from "lucide-react"
import { useState } from "react"

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  const faqs = [
    {
      question: "Is this just another analytics platform?",
      answer:
        "Nope! While we do provide killer analytics, OutcomeAI is a complete monetization platform that handles everything from outcome tracking to billing and revenue optimization.",
      color: "gold",
    },
    {
      question: "Do I need to change my pricing right away?",
      answer:
        "Not at all! Start with a hybrid model — keep your base subscription fee and add outcome-based components. We'll help you transition at your own pace.",
      color: "purple",
    },
    {
      question: "What if my customers don't want outcome-based pricing?",
      answer:
        "Our data shows 78% of customers prefer paying for results over access. But you can always offer both options and let them choose!",
      color: "blue",
    },
    {
      question: "Is this complicated to implement?",
      answer:
        "If you can install Google Analytics, you can implement OutcomeAI. Most customers are up and running in less than a week.",
      color: "teal",
    },
  ]

  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-dark mb-4 flex items-center justify-center gap-4">
            <div className="relative">
              {/* Question mark formation */}
              <div className="w-12 h-12 bg-gradient-to-br from-purple/20 to-purple/40 rounded-full flex items-center justify-center border border-purple/8 ring-1 ring-purple/5">
                <div className="relative">
                  {/* Question mark shape */}
                  <div className="w-4 h-4 relative">
                    {/* Top curve of question mark */}
                    <div className="absolute top-0 left-0 w-3 h-2 border-t-2 border-r-2 border-purple rounded-tr-full animate-pulse"></div>
                    {/* Middle vertical line */}
                    <div className="absolute top-1.5 right-0.5 w-0.5 h-1.5 bg-purple animate-pulse delay-200"></div>
                    {/* Bottom dot */}
                    <div className="absolute bottom-0 right-0.5 w-1 h-1 bg-purple rounded-full animate-pulse delay-400"></div>
                  </div>
                </div>
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple/50 rounded-full animate-bounce"></div>
              <div className="absolute top-2 left-2 w-2 h-2 bg-white rounded-full"></div>
            </div>
            <span className="text-purple">Frequently Asked Questions</span>
          </h2>
          <p className="text-xl text-gray-dark">We've got answers to your burning questions</p>
        </div>

        <div className="max-w-3xl mx-auto">
          {faqs.map((faq, index) => (
            <div
              key={index}
              className={`mb-4 rounded-2xl border border-${faq.color}/8 bg-gradient-to-r from-white to-${faq.color}-20 overflow-hidden shadow-lg ring-1 ring-${faq.color}/5 hover:ring-${faq.color}/10 transition-all duration-300`}
            >
              <button
                className="w-full px-8 py-6 text-left flex items-center justify-between hover:bg-white/50 transition-all duration-300"
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
              >
                <h3 className="text-xl font-bold text-gray-dark pr-4">{faq.question}</h3>
                <ChevronDown
                  className={`h-6 w-6 text-${faq.color} transition-transform duration-300 ${
                    openIndex === index ? "rotate-180" : ""
                  }`}
                />
              </button>

              <div
                className={`overflow-hidden transition-all duration-300 ${
                  openIndex === index ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
                }`}
              >
                <div className="px-8 pb-6">
                  <p className="text-lg text-gray-dark leading-relaxed">{faq.answer}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
