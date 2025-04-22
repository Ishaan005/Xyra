"use client"

import type React from "react"

import { SidebarProvider } from "@/components/ui/sidebar"
import { SidebarNav } from "@/components/layout/sidebar-nav"
import { Header } from "@/components/layout/header"
import { usePathname } from "next/navigation"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname()

  // Don't show dashboard layout on landing page and login page
  if (pathname === "/" || pathname === "/login") {
    return <>{children}</>
  }

  return (
    <SidebarProvider>
      <div className="flex min-h-screen flex-col">
        <Header />
        <div className="flex flex-1">
          <div className="hidden md:block">
            <SidebarNav />
          </div>
          <main className="flex-1">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  )
}
