"use client";
"use strict";
exports.__esModule = true;
exports.Header = void 0;
var react_1 = require("react");
var link_1 = require("next/link");
var navigation_1 = require("next/navigation");
var lucide_react_1 = require("lucide-react");
var button_1 = require("@/components/ui/button");
var theme_toggle_1 = require("@/components/theme-toggle");
var avatar_1 = require("@/components/ui/avatar");
var dropdown_menu_1 = require("@/components/ui/dropdown-menu");
var sheet_1 = require("@/components/ui/sheet");
var sidebar_nav_1 = require("@/components/layout/sidebar-nav");
function Header() {
    var pathname = navigation_1.usePathname();
    var _a = react_1.useState(false), mobileMenuOpen = _a[0], setMobileMenuOpen = _a[1];
    // Skip header on landing page and login page
    if (pathname === "/" || pathname === "/login") {
        return null;
    }
    var getPageTitle = function () {
        switch (pathname) {
            case "/dashboard":
                return "Dashboard";
            case "/pricing":
                return "Pricing Models";
            case "/agents":
                return "Agents";
            case "/customers":
                return "Customers";
            case "/reports":
                return "Reports";
            case "/settings":
                return "Settings";
            default:
                return "Business Engine";
        }
    };
    return (React.createElement("header", { className: "sticky top-0 z-50 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6" },
        React.createElement(sheet_1.Sheet, { open: mobileMenuOpen, onOpenChange: setMobileMenuOpen },
            React.createElement(sheet_1.SheetTrigger, { asChild: true },
                React.createElement(button_1.Button, { variant: "outline", size: "icon", className: "md:hidden" },
                    React.createElement(lucide_react_1.Menu, { className: "h-5 w-5" }),
                    React.createElement("span", { className: "sr-only" }, "Toggle menu"))),
            React.createElement(sheet_1.SheetContent, { side: "left", className: "p-0" },
                React.createElement(sidebar_nav_1.SidebarNav, null))),
        React.createElement("div", { className: "flex items-center gap-2 md:hidden" },
            React.createElement(link_1["default"], { href: "/", className: "flex items-center gap-2" },
                React.createElement("div", { className: "rounded-md bg-gold p-1" },
                    React.createElement(lucide_react_1.Zap, { className: "h-5 w-5 text-white" })),
                React.createElement("span", { className: "text-xl font-bold" }, "Business Engine"))),
        React.createElement("div", { className: "flex-1 md:ml-2" },
            React.createElement("h1", { className: "text-xl font-bold" }, getPageTitle())),
        React.createElement("div", { className: "flex items-center gap-4" },
            React.createElement(button_1.Button, { variant: "ghost", size: "icon", className: "relative" },
                React.createElement(lucide_react_1.Bell, { className: "h-5 w-5" }),
                React.createElement("span", { className: "absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] font-medium text-destructive-foreground" }, "3"),
                React.createElement("span", { className: "sr-only" }, "Notifications")),
            React.createElement(theme_toggle_1.ThemeToggle, null),
            React.createElement(dropdown_menu_1.DropdownMenu, null,
                React.createElement(dropdown_menu_1.DropdownMenuTrigger, { asChild: true },
                    React.createElement(button_1.Button, { variant: "ghost", className: "relative h-8 w-8 rounded-full" },
                        React.createElement(avatar_1.Avatar, { className: "h-8 w-8" },
                            React.createElement(avatar_1.AvatarImage, { src: "/placeholder.svg?height=32&width=32", alt: "User" }),
                            React.createElement(avatar_1.AvatarFallback, null, "JD")))),
                React.createElement(dropdown_menu_1.DropdownMenuContent, { align: "end" },
                    React.createElement(dropdown_menu_1.DropdownMenuLabel, null, "My Account"),
                    React.createElement(dropdown_menu_1.DropdownMenuSeparator, null),
                    React.createElement(dropdown_menu_1.DropdownMenuItem, null,
                        React.createElement("span", null, "Profile")),
                    React.createElement(dropdown_menu_1.DropdownMenuItem, null,
                        React.createElement("span", null, "Settings")),
                    React.createElement(dropdown_menu_1.DropdownMenuItem, null,
                        React.createElement("span", null, "Help")),
                    React.createElement(dropdown_menu_1.DropdownMenuSeparator, null),
                    React.createElement(dropdown_menu_1.DropdownMenuItem, null,
                        React.createElement("span", null, "Log out")))))));
}
exports.Header = Header;
