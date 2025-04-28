import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"

export function IntegrationSection() {
  return (
    <section className="bg-gradient-to-b from-gold-20 to-white py-20">
      <div className="container mx-auto px-4 md:px-6">
        <div className="mx-auto max-w-[800px] text-center">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Technical Integration</h2>
          <p className="mt-4 text-lg text-gray-dark">
            Business Engine is designed to work with your existing stack, with minimal code changes.
          </p>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2">
          <div className="rounded-xl border border-border bg-gray-dark p-6 shadow-sm">
            <pre className="font-mono text-sm text-white overflow-x-auto">
              <code>{`from paid_engine import BusinessEngine

engine.ingest(logs=Logs.objects.filter(date=today))
engine.define_pricing(model="hybrid", rules={
  "seat": 10, 
  "activity": 0.05, 
  "outcome": "1%"
})
`}</code>
            </pre>
          </div>

          <div className="flex flex-col justify-center space-y-4">
            <div className="flex items-center gap-2">
              <Check className="h-5 w-5 text-success" />
              <span className="font-bold">FastAPI-compatible</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="h-5 w-5 text-success" />
              <span className="font-bold">CLI + SDKs (Python, Node.js, Go)</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="h-5 w-5 text-success" />
              <span className="font-bold">Stripe + Salesforce Connectors</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="h-5 w-5 text-success" />
              <span className="font-bold">Works with Postgres, Snowflake, and more</span>
            </div>

            <Button size="lg" className="mt-4 font-bold">
              Read the Integration Guide
            </Button>
          </div>
        </div>
      </div>
    </section>
  )
}