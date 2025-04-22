import { Button } from "@/components/ui/button"
import Image from "next/image"

export function PrototypeSection() {
  return (
    <section className="bg-gradient-to-b from-white to-gold-20 py-20">
      <div className="container px-4 md:px-6">
        <div className="mx-auto max-w-[800px] text-center">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Live Prototype & Screenshots</h2>
          <p className="mt-4 text-lg text-gray-dark">
            See Business Engine in action with our interactive prototype and real-world examples.
          </p>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2">
          <div className="rounded-xl border border-border bg-white p-4 shadow-sm overflow-hidden">
            <div className="aspect-video relative rounded-lg overflow-hidden border border-border">
              <Image
                src="/placeholder.svg?height=600&width=800"
                alt="Pricing Rule Builder"
                width={800}
                height={600}
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent flex items-end">
                <div className="p-4 text-white">
                  <h3 className="text-xl font-bold">Pricing Rule Builder</h3>
                  <p>Create complex pricing rules with our visual editor</p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-white p-4 shadow-sm overflow-hidden">
            <div className="aspect-video relative rounded-lg overflow-hidden border border-border">
              <Image
                src="/placeholder.svg?height=600&width=800"
                alt="Margin Analytics Dashboard"
                width={800}
                height={600}
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent flex items-end">
                <div className="p-4 text-white">
                  <h3 className="text-xl font-bold">Margin Analytics Dashboard</h3>
                  <p>Track profitability in real-time across your business</p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-white p-4 shadow-sm overflow-hidden">
            <div className="aspect-video relative rounded-lg overflow-hidden border border-border">
              <Image
                src="/placeholder.svg?height=600&width=800"
                alt="ROI Summary Report"
                width={800}
                height={600}
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent flex items-end">
                <div className="p-4 text-white">
                  <h3 className="text-xl font-bold">ROI Summary Report</h3>
                  <p>Show customers the value they're getting from your platform</p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-white p-4 shadow-sm overflow-hidden">
            <div className="aspect-video relative rounded-lg overflow-hidden border border-border">
              <Image
                src="/placeholder.svg?height=600&width=800"
                alt="Invoicing View"
                width={800}
                height={600}
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent flex items-end">
                <div className="p-4 text-white">
                  <h3 className="text-xl font-bold">Invoicing View</h3>
                  <p>Automated billing with Stripe integration</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 text-center">
          <p className="text-lg font-bold mb-4">💬 Test it live in the sandbox with your own agent data.</p>
          <Button size="lg" className="font-bold">
            Try Prototype
          </Button>
        </div>
      </div>
    </section>
  )
}
