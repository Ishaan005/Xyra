import { Button } from "@/components/ui/button"
import { BarChart3, Zap } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-white to-gold-20 py-20 md:py-32">
      <div className="container mx-auto px-4 md:px-6">
        <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
          <div className="flex flex-col justify-center space-y-4">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
                 Monetize Your AI Platform Smarter. Automatically.
              </h1>
              <p className="max-w-[700px] text-lg text-gray-dark md:text-xl">
                Business Engine is the plug-and-play monetization layer for AI SaaS. Drop it into your backend to unlock
                dynamic pricing, margin analytics, and outcome-based billing—without changing your architecture.
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Button size="lg" className="font-bold bg-gold shadow-[0_0_15px_rgba(252,211,77,0.7)] animate-pulse">
                Book a Demo
              </Button>
              <Button size="lg" variant="outline" className="font-bold bg-teal-60">
                View Docs
              </Button>
              <Button size="lg" variant="secondary" className="font-bold bg-blue text-white">
                Try Prototype
              </Button>
            </div>
          </div>
          <div className="flex items-center justify-center">
            <div className="relative h-[350px] w-[350px] md:h-[400px] md:w-[400px] lg:h-[500px] lg:w-[500px]">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="h-full w-full rounded-full bg-gradient-to-br from-gold-light to-gold-dark opacity-20 blur-3xl"></div>
              </div>
              <div className="relative flex h-full w-full items-center justify-center rounded-xl border border-border bg-white/80 p-4 backdrop-blur-sm">
                <div className="grid gap-4">
                  <div className="flex items-center gap-2 rounded-lg bg-gold-20 p-3">
                    <BarChart3 className="h-5 w-5 text-gold-dark" />
                    <span className="font-bold">Margin Analytics</span>
                    <span className="ml-auto rounded-full bg-success px-2 py-0.5 text-xs text-white">+24%</span>
                  </div>
                  <div className="flex items-center gap-2 rounded-lg bg-blue-20 p-3">
                    <Zap className="h-5 w-5 text-blue" />
                    <span className="font-bold">Dynamic Pricing</span>
                    <span className="ml-auto rounded-full bg-success px-2 py-0.5 text-xs text-white">Active</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="rounded-lg bg-purple-20 p-3">
                      <div className="text-sm font-bold">Revenue</div>
                      <div className="text-xl font-bold text-purple">$12,450</div>
                    </div>
                    <div className="rounded-lg bg-teal-20 p-3">
                      <div className="text-sm font-bold">Margin</div>
                      <div className="text-xl font-bold text-teal">68.5%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
