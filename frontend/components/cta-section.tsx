import { Button } from "@/components/ui/button"
import { Search, Phone, FileText } from "lucide-react"

export function CTASection() {
  return (
    <section className="bg-gradient-to-b from-white to-gold-20 py-20">
      <div className="container px-4 md:px-6">
        <div className="mx-auto max-w-[800px] text-center">
          <h2 className="text-3xl font-bold tracking-tighter text-foreground sm:text-4xl md:text-5xl">
            Ready to make your AI SaaS more profitable?
          </h2>
          <p className="mt-4 text-lg text-gray-dark">
            Get started with Business Engine today and transform how you monetize your AI platform.
          </p>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Button size="lg" className="gap-2 font-bold">
              <Search className="h-5 w-5" />
              Explore the Docs
            </Button>
            <Button size="lg" variant="secondary" className="gap-2 font-bold">
              <Phone className="h-5 w-5" />
              Book a Demo
            </Button>
            <Button size="lg" variant="outline" className="gap-2 font-bold">
              <FileText className="h-5 w-5" />
              Get Early Access
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}
