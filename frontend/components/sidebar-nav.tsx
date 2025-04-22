"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, CreditCard, Settings, Users, LogOut, HelpCircle, FileText, Zap, User } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
  SidebarSeparator,
} from "@/components/ui/sidebar"
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
// Removed ThemeToggle import

export function SidebarNav() {
  const pathname = usePathname()

  const routes = [
    {
      href: "/dashboard",
      icon: BarChart3,
      title: "Dashboard",
    },
    {
      href: "/pricing",
      icon: CreditCard,
      title: "Pricing Models",
    },
    {
      href: "/agents",
      icon: Zap,
      title: "Agents",
    },
    {
      href: "/customers",
      icon: Users,
      title: "Customers",
    },
    {
      href: "/reports",
      icon: FileText,
      title: "Reports",
    },
    {
      href: "/settings",
      icon: Settings,
      title: "Settings",
    },
  ]

  return (
    <Sidebar>
      <SidebarHeader className="border-b py-4">
        <Link href="/" className="flex items-center gap-2 px-4">
          <div className="rounded-md bg-gold p-1">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold">Business Engine</span>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          {routes.map((route) => (
            <SidebarMenuItem key={route.href}>
              <SidebarMenuButton asChild isActive={pathname === route.href} tooltip={route.title}>
                <Link href={route.href}>
                  <route.icon className="h-5 w-5" />
                  <span>{route.title}</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarContent>
      <SidebarSeparator />
      <SidebarFooter className="p-4">
        <div className="flex items-center justify-between">
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
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          {/* ThemeToggle removed */}
        </div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
