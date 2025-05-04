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
  if (pathname === "/" || pathname === "/login" || pathname === "/signup") {
    return <>{children}</>
  }

  return (
      <div className="flex flex-col">
        <Header />
        <div className="flex flex-1 w-full">
          <SidebarProvider>
              <SidebarNav />
          </SidebarProvider>
          <main>
            <div className="px-4 md:px-6">{children}</div>
          </main>
        </div>
      </div>

  )
}
