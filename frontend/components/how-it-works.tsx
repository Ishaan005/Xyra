import { FileText, Settings, BarChart, FileSpreadsheet } from "lucide-react"

export function HowItWorks() {
  return (
    <section className="bg-white py-20">
      <div className="container mx-auto px-4 md:px-6">
        <div className="mx-auto max-w-[800px] text-center">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Drop-in. Sync. Bill. Grow.</h2>
          <p className="mt-4 text-lg text-gray-dark">
            Implementing Business Engine is straightforward and non-disruptive to your existing architecture.
          </p>
        </div>
        <div className="mt-16 relative">
          {/* Connection line */}
          <div className="absolute left-1/2 top-0 h-full w-0.5 -translate-x-1/2 bg-gold-40 hidden md:block"></div>

          <div className="grid gap-12 md:gap-24">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div className="order-2 md:order-1">
                <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
                  <h3 className="text-xl font-bold">1. Ingest Logs</h3>
                  <p className="mt-2 text-gray-dark">
                    Connect data from your agents or API. Our SDK automatically captures usage, costs, and outcomes with
                    minimal code changes.
                  </p>
                </div>
              </div>
              <div className="flex justify-center order-1 md:order-2">
                <div className="relative">
                  <div className="absolute -inset-4 bg-gold/10 rounded-full blur-xl"></div>
                  <div className="relative h-24 w-24 rounded-full bg-white flex items-center justify-center border border-gold shadow-sm">
                    <FileText className="h-12 w-12 text-gold" />
                  </div>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div className="flex justify-center">
                <div className="relative">
                  <div className="absolute -inset-4 bg-blue/10 rounded-full blur-xl"></div>
                  <div className="relative h-24 w-24 rounded-full bg-white flex items-center justify-center border border-blue shadow-sm">
                    <Settings className="h-12 w-12 text-blue" />
                  </div>
                </div>
              </div>
              <div>
                <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
                  <h3 className="text-xl font-bold">2. Define Pricing</h3>
                  <p className="mt-2 text-gray-dark">
                    Use our visual builder or import from Stripe. Create hybrid pricing models that combine usage,
                    seats, and outcome-based logic.
                  </p>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div className="order-2 md:order-1">
                <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
                  <h3 className="text-xl font-bold">3. Track Margins</h3>
                  <p className="mt-2 text-gray-dark">
                    Get real-time cost vs. revenue insights. See profitability by customer, feature, or agent and
                    optimize your pricing strategy.
                  </p>
                </div>
              </div>
              <div className="flex justify-center order-1 md:order-2">
                <div className="relative">
                  <div className="absolute -inset-4 bg-purple/10 rounded-full blur-xl"></div>
                  <div className="relative h-24 w-24 rounded-full bg-white flex items-center justify-center border border-purple shadow-sm">
                    <BarChart className="h-12 w-12 text-purple" />
                  </div>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div className="flex justify-center">
                <div className="relative">
                  <div className="absolute -inset-4 bg-teal/10 rounded-full blur-xl"></div>
                  <div className="relative h-24 w-24 rounded-full bg-white flex items-center justify-center border border-teal shadow-sm">
                    <FileSpreadsheet className="h-12 w-12 text-teal" />
                  </div>
                </div>
              </div>
              <div>
                <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
                  <h3 className="text-xl font-bold">4. Send Invoices & ROI Reports</h3>
                  <p className="mt-2 text-gray-dark">
                    Fully automated, customizable billing and reporting. Show customers their usage, costs, and the
                    value they're getting.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
