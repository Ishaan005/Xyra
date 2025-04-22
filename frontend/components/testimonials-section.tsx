export function TestimonialsSection() {
  return (
    <section className="bg-white py-20">
      <div className="container px-4 md:px-6">
        <div className="mx-auto max-w-[800px] text-center">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Pilot Results</h2>
          <p className="mt-4 text-lg text-gray-dark">See what early adopters are saying about Business Engine.</p>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2">
          <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-gold-20 flex items-center justify-center">
                  <span className="text-xl font-bold text-gold-dark">A</span>
                </div>
                <div>
                  <h3 className="font-bold">AI Analytics SaaS</h3>
                  <p className="text-sm text-gray-dark">Early Pilot Partner</p>
                </div>
              </div>
              <blockquote className="text-lg italic">
                "Business Engine helped us 3x revenue per user with no extra effort. The margin insights were
                eye-opening."
              </blockquote>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-4">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 rounded-full bg-blue-20 flex items-center justify-center">
                  <span className="text-xl font-bold text-blue">B</span>
                </div>
                <div>
                  <h3 className="font-bold">B2B AI Platform</h3>
                  <p className="text-sm text-gray-dark">Beta Customer</p>
                </div>
              </div>
              <blockquote className="text-lg italic">
                "The ROI dashboards have transformed our customer conversations from cost to value. Renewals are now
                much easier."
              </blockquote>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
