"use client"

import * as React from "react"
import { PanelLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent } from "@/components/ui/sheet"

// Constants for sidebar configuration
const SIDEBAR_WIDTH = "16rem"
const SIDEBAR_WIDTH_COLLAPSED = "4rem"
const SIDEBAR_MOBILE_WIDTH = "18rem"

// Custom hook to detect mobile viewport
function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState(false)

  React.useEffect(() => {
    const checkIsMobile = () => setIsMobile(window.innerWidth < 768)

    // Initial check
    checkIsMobile()

    // Add event listener for window resize
    window.addEventListener("resize", checkIsMobile)

    // Cleanup
    return () => window.removeEventListener("resize", checkIsMobile)
  }, [])

  return isMobile
}

// Types for the sidebar context
type SidebarContextType = {
  expanded: boolean
  setExpanded: React.Dispatch<React.SetStateAction<boolean>>
  mobileOpen: boolean
  setMobileOpen: React.Dispatch<React.SetStateAction<boolean>>
  isMobile: boolean
  toggleSidebar: () => void
}

// Create context for sidebar state
const SidebarContext = React.createContext<SidebarContextType | undefined>(undefined)

// Custom hook to use sidebar context
export function useSidebar() {
  const context = React.useContext(SidebarContext)
  if (!context) {
    throw new Error("useSidebar must be used within a SidebarProvider")
  }
  return context
}

// Sidebar provider component
interface SidebarProviderProps {
  children: React.ReactNode
  defaultExpanded?: boolean
}

export function SidebarProvider({ children, defaultExpanded = true }: SidebarProviderProps) {
  const [expanded, setExpanded] = React.useState(defaultExpanded)
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const isMobile = useIsMobile()

  // Toggle sidebar based on device
  const toggleSidebar = React.useCallback(() => {
    if (isMobile) {
      setMobileOpen((prev) => !prev)
    } else {
      setExpanded((prev) => !prev)
    }
  }, [isMobile])

  // Save sidebar state in localStorage
  React.useEffect(() => {
    if (!isMobile) {
      localStorage.setItem("sidebar-expanded", expanded.toString())
    }
  }, [expanded, isMobile])

  // Load sidebar state from localStorage
  React.useEffect(() => {
    const savedState = localStorage.getItem("sidebar-expanded")
    if (savedState !== null && !isMobile) {
      setExpanded(savedState === "true")
    }
  }, [isMobile])

  const value = React.useMemo(
    () => ({
      expanded,
      setExpanded,
      mobileOpen,
      setMobileOpen,
      isMobile,
      toggleSidebar,
    }),
    [expanded, mobileOpen, isMobile, toggleSidebar],
  )

  return (
    <SidebarContext.Provider value={value}>
      <div
        className="flex min-h-screen w-full"
        style={
          {
            "--sidebar-width": SIDEBAR_WIDTH,
            "--sidebar-width-collapsed": SIDEBAR_WIDTH_COLLAPSED,
            "--sidebar-mobile-width": SIDEBAR_MOBILE_WIDTH,
          } as React.CSSProperties
        }
      >
        {children}
      </div>
    </SidebarContext.Provider>
  )
}

// Sidebar component
interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function Sidebar({ children, className, ...props }: SidebarProps) {
  const { expanded, mobileOpen, setMobileOpen, isMobile } = useSidebar()

  // Mobile sidebar using Sheet component
  if (isMobile) {
    return (
      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent side="left" className="w-[var(--sidebar-mobile-width)] p-0 border border-white/10 rounded-2xl shadow-[0_0_20px_rgba(255,255,255,0.05)] backdrop-blur-md">
          <div className="flex h-full flex-col bg-sidebar text-sidebar-foreground">{children}</div>
        </SheetContent>
      </Sheet>
    )
  }

  // Desktop sidebar
  return (
    <div
      className={cn(
        "h-screen fixed top-0 left-0 z-30 flex flex-col border-r border-white/10 bg-sidebar text-sidebar-foreground transition-all duration-300 ease-in-out shadow-[0_0_25px_rgba(255,255,255,0.05)] backdrop-blur-md",
        expanded ? "w-[var(--sidebar-width)]" : "w-[var(--sidebar-width-collapsed)]",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// Sidebar header component
interface SidebarHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function SidebarHeader({ children, className, ...props }: SidebarHeaderProps) {
  return (
    <div className={cn("flex h-16 shrink-0 items-center border-b border-white/10 px-4", className)} {...props}>
      {children}
    </div>
  )
}

// Sidebar content component
interface SidebarContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function SidebarContent({ children, className, ...props }: SidebarContentProps) {
  return (
    <div className={cn("flex-1 overflow-auto py-2", className)} {...props}>
      {children}
    </div>
  )
}

// Sidebar footer component
interface SidebarFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function SidebarFooter({ children, className, ...props }: SidebarFooterProps) {
  return (
    <div className={cn("mt-auto border-t border-white/10 p-4", className)} {...props}>
      {children}
    </div>
  )
}

// Sidebar nav component
interface SidebarNavProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode
}

export function SidebarNav({ children, className, ...props }: SidebarNavProps) {
  return (
    <nav className={cn("flex flex-col gap-1 px-2", className)} {...props}>
      {children}
    </nav>
  )
}

// Sidebar nav item component
interface SidebarNavItemProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: React.ReactNode
  title: string
  isActive?: boolean
  children?: React.ReactNode
}

export function SidebarNavItem({ icon, title, isActive = false, children, className, ...props }: SidebarNavItemProps) {
  const { expanded } = useSidebar()

  return (
    <div
      className={cn(
        "group relative flex items-center rounded-md px-2 py-2 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors",
        isActive && "bg-sidebar-accent text-sidebar-accent-foreground font-medium",
        className,
      )}
      {...props}
    >
      {icon && <div className="mr-2 h-5 w-5 shrink-0">{icon}</div>}
      {expanded && <span>{title}</span>}
      {!expanded && (
        <div className="absolute left-full ml-2 hidden rounded-md bg-popover px-2 py-1 text-sm text-popover-foreground shadow-md group-hover:block">
          {title}
        </div>
      )}
      {children}
    </div>
  )
}

// Sidebar trigger component
interface SidebarTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export function SidebarTrigger({ className, ...props }: SidebarTriggerProps) {
  const { toggleSidebar } = useSidebar()

  return (
    <Button variant="ghost" size="icon" className={cn("h-9 w-9", className)} onClick={toggleSidebar} {...props}>
      <PanelLeft className="h-5 w-5" />
      <span className="sr-only">Toggle sidebar</span>
    </Button>
  )
}

// Main content component that works with the sidebar
interface MainContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function MainContent({ children, className, ...props }: MainContentProps) {
  const { expanded, isMobile } = useSidebar()

  return (
    <main
      className={cn(
        "flex-1 transition-all duration-300 ease-in-out",
        isMobile ? "ml-0" : expanded ? "ml-[var(--sidebar-width)]" : "ml-[var(--sidebar-width-collapsed)]",
        className,
      )}
      {...props}
    >
      {children}
    </main>
  )
}
