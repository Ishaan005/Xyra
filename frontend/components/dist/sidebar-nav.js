"use client";
"use strict";
exports.__esModule = true;
exports.SidebarNav = void 0;
var link_1 = require("next/link");
var navigation_1 = require("next/navigation");
var lucide_react_1 = require("lucide-react");
var sidebar_1 = require("@/components/ui/sidebar");
var avatar_1 = require("@/components/ui/avatar");
var button_1 = require("@/components/ui/button");
var dropdown_menu_1 = require("@/components/ui/dropdown-menu");
// Removed ThemeToggle import
function SidebarNav() {
    var pathname = navigation_1.usePathname();
    var routes = [
        {
            href: "/dashboard",
            icon: lucide_react_1.BarChart3,
            title: "Dashboard"
        },
        {
            href: "/pricing",
            icon: lucide_react_1.CreditCard,
            title: "Pricing Models"
        },
        {
            href: "/agents",
            icon: lucide_react_1.Zap,
            title: "Agents"
        },
        {
            href: "/customers",
            icon: lucide_react_1.Users,
            title: "Customers"
        },
        {
            href: "/reports",
            icon: lucide_react_1.FileText,
            title: "Reports"
        },
        {
            href: "/settings",
            icon: lucide_react_1.Settings,
            title: "Settings"
        },
    ];
    return (React.createElement(sidebar_1.Sidebar, null,
        React.createElement(sidebar_1.SidebarHeader, { className: "border-b py-4" },
            React.createElement(link_1["default"], { href: "/", className: "flex items-center gap-2 px-4" },
                React.createElement("div", { className: "rounded-md bg-gold p-1" },
                    React.createElement(lucide_react_1.Zap, { className: "h-5 w-5 text-white" })),
                React.createElement("span", { className: "text-xl font-bold" }, "Business Engine"))),
        React.createElement(sidebar_1.SidebarContent, null,
            React.createElement(sidebar_1.SidebarMenu, null, routes.map(function (route) { return (React.createElement(sidebar_1.SidebarMenuItem, { key: route.href },
                React.createElement(sidebar_1.SidebarMenuButton, { asChild: true, isActive: pathname === route.href, tooltip: route.title },
                    React.createElement(link_1["default"], { href: route.href },
                        React.createElement(route.icon, { className: "h-5 w-5" }),
                        React.createElement("span", null, route.title))))); }))),
        React.createElement(sidebar_1.SidebarSeparator, null),
        React.createElement(sidebar_1.SidebarFooter, { className: "p-4" },
            React.createElement("div", { className: "flex items-center justify-between" },
                React.createElement(dropdown_menu_1.DropdownMenu, null,
                    React.createElement(dropdown_menu_1.DropdownMenuTrigger, { asChild: true },
                        React.createElement(button_1.Button, { variant: "ghost", className: "h-8 w-8 rounded-full" },
                            React.createElement(avatar_1.Avatar, { className: "h-8 w-8" },
                                React.createElement(avatar_1.AvatarImage, { src: "/placeholder.svg?height=32&width=32", alt: "User" }),
                                React.createElement(avatar_1.AvatarFallback, null, "JD")))),
                    React.createElement(dropdown_menu_1.DropdownMenuContent, { align: "end" },
                        React.createElement(dropdown_menu_1.DropdownMenuLabel, null, "My Account"),
                        React.createElement(dropdown_menu_1.DropdownMenuSeparator, null),
                        React.createElement(dropdown_menu_1.DropdownMenuItem, null,
                            React.createElement(lucide_react_1.User, { className: "mr-2 h-4 w-4" }),
                            React.createElement("span", null, "Profile")),
                        React.createElement(dropdown_menu_1.DropdownMenuItem, null,
                            React.createElement(lucide_react_1.Settings, { className: "mr-2 h-4 w-4" }),
                            React.createElement("span", null, "Settings")),
                        React.createElement(dropdown_menu_1.DropdownMenuItem, null,
                            React.createElement(lucide_react_1.HelpCircle, { className: "mr-2 h-4 w-4" }),
                            React.createElement("span", null, "Help")),
                        React.createElement(dropdown_menu_1.DropdownMenuSeparator, null),
                        React.createElement(dropdown_menu_1.DropdownMenuItem, null,
                            React.createElement(lucide_react_1.LogOut, { className: "mr-2 h-4 w-4" }),
                            React.createElement("span", null, "Log out")))))),
        React.createElement(sidebar_1.SidebarRail, null)));
}
exports.SidebarNav = SidebarNav;
