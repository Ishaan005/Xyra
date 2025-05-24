"use client"

import type React from "react"
import { usePathname } from "next/navigation"

import { SidebarProvider, MainContent, SidebarTrigger } from "@/components/ui/custom-sidebar"
import { SidebarNav } from "@/components/layout/sidebar-nav"
import { Header } from "@/components/layout/header"

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
    <SidebarProvider>
      <SidebarNav />
      <MainContent>
        <div className="flex min-h-screen flex-col">
            <SidebarTrigger className="md:hidden" />

          <div className="flex-1 p-4 md:p-6">
            <div className="max-w-[1400px] mx-auto w-full">{children}</div>
          </div>
        </div>
      </MainContent>
    </SidebarProvider>
  )
}
