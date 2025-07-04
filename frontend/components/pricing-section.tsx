"use client"

import { Button } from "@/components/ui/button"
import { Mail, Zap, Users, Star } from "lucide-react"
import { useState } from "react"

export function PricingSection() {
  const [email, setEmail] = useState("")
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (email) {
      setIsSubmitted(true)
      // Here you would typically send the email to your backend
      console.log("Email submitted:", email)
    }
  }

  return (
    <section className="py-20 bg-gradient-to-br from-gold-20 via-purple-20 to-blue-20">
      <div className="container mx-auto px-4 md:px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-dark mb-4">
            Be Among the First to Experience <span className="text-gold">Xyra</span>
          </h2>
          <p className="text-xl text-gray-60 max-w-3xl mx-auto">
            Join our exclusive waitlist and get early access to the future of outcome-based pricing
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Main Waitlist Card */}
          <div className="relative bg-gradient-to-br from-gold/10 to-purple/10 rounded-2xl p-8 md:p-12 border border-gold/8 shadow-xl ring-1 ring-gold/5">
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
              <div className="bg-gold text-white px-6 py-2 rounded-full font-bold text-sm">EARLY ACCESS</div>
            </div>

            <div className="text-center mb-12 mt-4">
              <div className="text-6xl mb-6"></div>
              <h3 className="text-3xl font-bold text-gray-dark mb-4">
                Ready to Transform Your Pricing Strategy?
              </h3>
              <p className="text-lg text-gray-60 max-w-2xl mx-auto">
                Join our waitlist to be notified when we go live and get exclusive early access benefits.
              </p>
            </div>

            {/* Benefits */}
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <div className="text-center p-6 bg-white/50 rounded-xl">
                <Star className="h-8 w-8 text-gold mx-auto mb-3" />
                <h4 className="font-bold text-gray-dark mb-2">Early Access</h4>
                <p className="text-sm text-gray-60">Be the first to try Xyra before public launch</p>
              </div>
              <div className="text-center p-6 bg-white/50 rounded-xl">
                <Users className="h-8 w-8 text-purple mx-auto mb-3" />
                <h4 className="font-bold text-gray-dark mb-2">Exclusive Community</h4>
                <p className="text-sm text-gray-60">Join our private community of pricing innovators</p>
              </div>
              <div className="text-center p-6 bg-white/50 rounded-xl">
                <Zap className="h-8 w-8 text-blue mx-auto mb-3" />
                <h4 className="font-bold text-gray-dark mb-2">Special Pricing</h4>
                <p className="text-sm text-gray-60">Get exclusive launch pricing for early supporters</p>
              </div>
            </div>

            {/* Email Signup */}
            {!isSubmitted ? (
              <form onSubmit={handleSubmit} className="max-w-md mx-auto">
                <div className="flex flex-col sm:flex-row items-stretch gap-3">
                  <div className="flex-1">
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email address"
                      className="w-full h-full px-4 py-3 rounded-xl border border-gray/20 focus:border-gold focus:outline-none focus:ring-2 focus:ring-gold/20 bg-white/80 backdrop-blur-sm"
                      required
                    />
                  </div>
                  <Button 
                    type="submit"
                    className="h-full bg-gradient-to-r from-gold to-gold-dark hover:from-gold-dark hover:to-gold text-white font-bold px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center"
                  >
                    <Mail className="mr-2 h-5 w-5" />
                    Join Waitlist
                  </Button>
                </div>
              </form>
            ) : (
              <div className="text-center max-w-md mx-auto">
                <div className="text-6xl mb-4"></div>
                <h4 className="text-2xl font-bold text-gray-dark mb-2">You're on the list!</h4>
                <p className="text-gray-60">
                  Thank you for joining our waitlist. We'll notify you as soon as Xyra is ready for early access.
                </p>
              </div>
            )}

            {/* Social Proof */}
            <div className="text-center mt-8 pt-8 border-t border-gray/10">
              <div className="text-sm text-gray-60 mb-2">
                Join <span className="font-bold text-gold">500+</span> pricing professionals already on the waitlist
              </div>
              <div className="flex justify-center items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 text-gold fill-gold" />
                ))}
                <span className="text-sm text-gray-60 ml-2">Rated 4.9/5 by beta testers</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
