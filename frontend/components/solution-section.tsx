import { DollarSign, BarChart2, PieChart, Plug } from "lucide-react"

export function SolutionSection() {
  return (
    <section className="bg-gradient-to-b from-gold-20 to-white py-20">
      <div className="container mx-auto px-4 md:px-6">
        <div className="mx-auto max-w-[800px] text-center">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Business Engine gives you...</h2>
        </div>
        <div className="mt-16 grid gap-8 md:grid-cols-2">
          <div className="flex gap-4 rounded-xl border border-border bg-white p-6 shadow-sm">
            <div className="rounded-full bg-gold/10 p-3 h-fit">
              <DollarSign className="h-6 w-6 text-gold-dark" />
            </div>
            <div>
              <h3 className="text-xl font-bold"> Hybrid Pricing</h3>
              <p className="mt-2 text-gray-dark">
                Combine usage-based, seat-based, and outcome-based pricing models to maximize revenue while keeping
                customers happy.
              </p>
            </div>
          </div>
          <div className="flex gap-4 rounded-xl border border-border bg-white p-6 shadow-sm">
            <div className="rounded-full bg-blue/10 p-3 h-fit">
              <BarChart2 className="h-6 w-6 text-blue" />
            </div>
            <div>
              <h3 className="text-xl font-bold">Live Margin Tracking</h3>
              <p className="mt-2 text-gray-dark">
                Know your profit per customer, feature, or agent in real-time. Identify opportunities to optimize
                pricing and reduce costs.
              </p>
            </div>
          </div>
          <div className="flex gap-4 rounded-xl border border-border bg-white p-6 shadow-sm">
            <div className="rounded-full bg-purple/10 p-3 h-fit">
              <PieChart className="h-6 w-6 text-purple" />
            </div>
            <div>
              <h3 className="text-xl font-bold">ROI Dashboards</h3>
              <p className="mt-2 text-gray-dark">
                Auto-generated reports that show customers the value they're getting. Make renewal conversations about
                value, not cost.
              </p>
            </div>
          </div>
          <div className="flex gap-4 rounded-xl border border-border bg-white p-6 shadow-sm">
            <div className="rounded-full bg-teal/10 p-3 h-fit">
              <Plug className="h-6 w-6 text-teal" />
            </div>
            <div>
              <h3 className="text-xl font-bold">Plug & Play API</h3>
              <p className="mt-2 text-gray-dark">
                Works with your current stack, no major rewrites. Compatible with Python, Node.js, FastAPI, Stripe,
                Postgres, Snowflake, and more.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
