import { HeroSection } from "@/components/hero-section"
import { ProblemSection } from "@/components/problem-section"
import { SolutionSection } from "@/components/solution-section"
import { HowItWorks } from "@/components/how-it-works"
import { PrototypeSection } from "@/components/prototype-section"
import { TeamsSection } from "@/components/teams-section"
import { IntegrationSection } from "@/components/integration-section"
import { TestimonialsSection } from "@/components/testimonials-section"
import { CTASection } from "@/components/cta-section"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex-1">
        <HeroSection />
        <ProblemSection />
        <SolutionSection />
        <HowItWorks />
        <PrototypeSection />
        <TeamsSection />
        <IntegrationSection />
        <TestimonialsSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  )
}
