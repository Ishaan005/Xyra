import { Users, TrendingUp, BarChart4, Code } from "lucide-react"

export function TeamsSection() {
  return (
    <section className="bg-white py-20">
      <div className="container px-4 md:px-6">
        <div className="mx-auto max-w-[800px] text-center">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Built for AI SaaS Teams</h2>
          <p className="mt-4 text-lg text-gray-dark">
            Business Engine is designed for modern AI companies looking to optimize their monetization strategy.
          </p>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <div className="flex flex-col items-center gap-2 rounded-xl border border-border bg-white p-6 text-center shadow-sm">
            <div className="rounded-full bg-gold/10 p-3">
              <Users className="h-6 w-6 text-gold-dark" />
            </div>
            <h3 className="text-xl font-bold">Founders</h3>
            <p className="text-gray-dark">
              Scaling from free to paid with intelligent pricing models that maximize revenue.
            </p>
          </div>
          <div className="flex flex-col items-center gap-2 rounded-xl border border-border bg-white p-6 text-center shadow-sm">
            <div className="rounded-full bg-blue/10 p-3">
              <TrendingUp className="h-6 w-6 text-blue" />
            </div>
            <h3 className="text-xl font-bold">Product Teams</h3>
            <p className="text-gray-dark">
              Building monetization flows that align with customer value and usage patterns.
            </p>
          </div>
          <div className="flex flex-col items-center gap-2 rounded-xl border border-border bg-white p-6 text-center shadow-sm">
            <div className="rounded-full bg-purple/10 p-3">
              <BarChart4 className="h-6 w-6 text-purple" />
            </div>
            <h3 className="text-xl font-bold">CFOs</h3>
            <p className="text-gray-dark">
              Looking for clear margins and profitability insights across customers and features.
            </p>
          </div>
          <div className="flex flex-col items-center gap-2 rounded-xl border border-border bg-white p-6 text-center shadow-sm">
            <div className="rounded-full bg-teal/10 p-3">
              <Code className="h-6 w-6 text-teal" />
            </div>
            <h3 className="text-xl font-bold">Developers</h3>
            <p className="text-gray-dark">
              Needing painless integration with existing systems and minimal maintenance overhead.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
