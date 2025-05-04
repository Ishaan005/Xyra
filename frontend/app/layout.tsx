// layout is a server component
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { Providers } from "./providers"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Xyra- Monetize Your AI Platform Smarter",
  description:
    "Xyra is the plug-and-play monetization layer for AI SaaS. Drop it into your backend to unlock dynamic pricing, margin analytics, and outcome-based billing.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        {/* Clientside providers */}
        <Providers>
          <DashboardLayout>{children}</DashboardLayout>
        </Providers>
      </body>
    </html>
  )
}
