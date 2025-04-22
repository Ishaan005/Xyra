"use client";
"use strict";
exports.__esModule = true;
exports.DashboardLayout = void 0;
var sidebar_1 = require("@/components/ui/sidebar");
var sidebar_nav_1 = require("@/components/layout/sidebar-nav");
var header_1 = require("@/components/layout/header");
var navigation_1 = require("next/navigation");
function DashboardLayout(_a) {
    var children = _a.children;
    var pathname = navigation_1.usePathname();
    // Don't show dashboard layout on landing page and login page
    if (pathname === "/" || pathname === "/login") {
        return React.createElement(React.Fragment, null, children);
    }
    return (React.createElement(sidebar_1.SidebarProvider, null,
        React.createElement("div", { className: "flex min-h-screen flex-col" },
            React.createElement(header_1.Header, null),
            React.createElement("div", { className: "flex flex-1" },
                React.createElement("div", { className: "hidden md:block" },
                    React.createElement(sidebar_nav_1.SidebarNav, null)),
                React.createElement("main", { className: "flex-1" }, children)))));
}
exports.DashboardLayout = DashboardLayout;
