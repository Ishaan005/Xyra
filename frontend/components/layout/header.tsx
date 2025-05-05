"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Zap } from "lucide-react"

interface HeaderProps {
  children?: React.ReactNode
}

export function Header({ children }: HeaderProps) {
  const pathname = usePathname()

  // Skip header on landing page and login page
  if (pathname === "/" || pathname === "/login" || pathname === "/signup") {
    return null
  }

  const getPageTitle = () => {
    switch (pathname) {
      case "/dashboard":
        return "Dashboard"
      case "/pricing":
        return "Pricing Models"
      case "/agents":
        return "Agents"
      case "/customers":
        return "Customers"
      case "/reports":
        return "Reports"
      case "/settings":
        return "Settings"
      default:
        return "Business Engine"
    }
  }

  return (
    <header className="sticky top-0 z-40 border-b bg-background">
      <div className="container flex h-16 items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-2">
          {children}
          <Link href="/" className="flex items-center gap-2 md:hidden">
            <div className="rounded-md bg-gold p-1">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold">Business Engine</span>
          </Link>
        </div>
        <div className="flex items-center gap-2">{/* Add header actions here if needed */}</div>
      </div>
    </header>
  )
}
