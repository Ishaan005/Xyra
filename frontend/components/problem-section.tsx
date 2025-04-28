import { AlertTriangle, TrendingDown, Eye, FileQuestion } from "lucide-react"

export function ProblemSection() {
  return (
    <section className="bg-white py-20">
      <div className="container mx-auto px-4 md:px-6">
        <div className="mx-auto max-w-[800px] text-center">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            Your AI platform is powerful—but are you pricing it intelligently?
          </h2>
        </div>
        <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <div className="flex flex-col items-center gap-2 rounded-xl border border-border bg-white p-6 text-center shadow-sm">
            <div className="rounded-full bg-destructive/10 p-3">
              <TrendingDown className="h-6 w-6 text-destructive text-gold" />
            </div>
            <h3 className="text-xl font-bold">Static pricing limits revenue</h3>
            <p className="text-gray-dark">
              One-size-fits-all pricing fails to capture value from power users and high-ROI use cases.
            </p>
          </div>
          <div className="flex flex-col items-center gap-2 rounded-xl border border-border bg-white p-6 text-center shadow-sm">
            <div className="rounded-full bg-destructive/10 p-3">
              <Eye className="h-6 w-6 text-destructive text-blue" />
            </div>
            <h3 className="text-xl font-bold">You're flying blind on margins</h3>
            <p className="text-gray-dark">
              Without real-time cost tracking, you can't optimize pricing or identify unprofitable customers.
            </p>
          </div>
          <div className="flex flex-col items-center gap-2 rounded-xl border border-border bg-white p-6 text-center shadow-sm">
            <div className="rounded-full bg-destructive/10 p-3">
              <FileQuestion className="h-6 w-6 text-destructive text-purple" />
            </div>
            <h3 className="text-xl font-bold">ROI reporting is manual</h3>
            <p className="text-gray-dark">
              Customers demand proof of value, but creating ROI reports is time-consuming and inconsistent.
            </p>
          </div>
          <div className="flex flex-col items-center gap-2 rounded-xl border border-border bg-white p-6 text-center shadow-sm">
            <div className="rounded-full bg-destructive/10 p-3">
              <AlertTriangle className="h-6 w-6 text-destructive text-teal" />
            </div>
            <h3 className="text-xl font-bold">Customers want transparency</h3>
            <p className="text-gray-dark">
              Modern buyers expect value-aligned pricing and clear visibility into what they're paying for.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}