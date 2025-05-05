"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, CreditCard, Settings, Users, LogOut, HelpCircle, FileText, Zap, User } from "lucide-react"

import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarNav as Nav,
  SidebarNavItem,
} from "@/components/ui/custom-sidebar"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ThemeToggle } from "@/components/theme-toggle"
import { Separator } from "@/components/ui/separator"

export function SidebarNav() {
  const pathname = usePathname()

  const routes = [
    {
      href: "/dashboard",
      icon: <BarChart3 className="h-5 w-5" />,
      title: "Dashboard",
    },
    {
      href: "/pricing",
      icon: <CreditCard className="h-5 w-5" />,
      title: "Pricing Models",
    },
    {
      href: "/agents",
      icon: <Zap className="h-5 w-5" />,
      title: "Agents",
    },
    {
      href: "/settings",
      icon: <Settings className="h-5 w-5" />,
      title: "Settings",
    },
  ]

  return (
    <Sidebar>
      <SidebarHeader>
        <Link href="/" className="flex items-center gap-2">
          <div className="rounded-md bg-gold p-1">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold">Xyra</span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <Nav>
          {routes.map((route) => (
            <Link href={route.href} key={route.href} className="block">
              <SidebarNavItem icon={route.icon} title={route.title} isActive={pathname === route.href} />
            </Link>
          ))}
        </Nav>
      </SidebarContent>
      <Separator className="mx-2" />
      <SidebarFooter>
        <div className="flex items-center justify-between bg-white">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/placeholder.svg?height=32&width=32" alt="User" />
                  <AvatarFallback>JD</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="mr-2 h-4 w-4" />
                <span>Profile</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </DropdownMenuItem>
              <DropdownMenuItem>
                <HelpCircle className="mr-2 h-4 w-4" />
                <span>Help</span>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <LogOut className="mr-2 h-4 w-4" />
                <span onClick={() => (window.location.href = "/login")}>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <ThemeToggle />
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
