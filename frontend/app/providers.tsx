"use client"

import React from "react"
import { Toaster } from "react-hot-toast"
import { SessionProvider } from "next-auth/react"
import { OrganizationProvider } from "@/contexts/OrganizationContext"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Toaster />
      <SessionProvider>
        <OrganizationProvider>
          {children}
        </OrganizationProvider>
      </SessionProvider>
    </>
  )
}