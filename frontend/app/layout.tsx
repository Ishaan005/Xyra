import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { DashboardLayout } from "@/components/layout/dashboard-layout"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Business Engine - Monetize Your AI Platform Smarter",
  description:
    "Business Engine is the plug-and-play monetization layer for AI SaaS. Drop it into your backend to unlock dynamic pricing, margin analytics, and outcome-based billing.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <DashboardLayout>{children}</DashboardLayout>
      </body>
    </html>
  )
}
