"use strict";
exports.__esModule = true;
exports.metadata = void 0;
var google_1 = require("next/font/google");
require("./globals.css");
var dashboard_layout_1 = require("@/components/layout/dashboard-layout");
var inter = google_1.Inter({ subsets: ["latin"] });
exports.metadata = {
    title: "Business Engine - Monetize Your AI Platform Smarter",
    description: "Business Engine is the plug-and-play monetization layer for AI SaaS. Drop it into your backend to unlock dynamic pricing, margin analytics, and outcome-based billing."
};
function RootLayout(_a) {
    var children = _a.children;
    return (React.createElement("html", { lang: "en", suppressHydrationWarning: true },
        React.createElement("body", { className: inter.className },
            React.createElement(dashboard_layout_1.DashboardLayout, null, children))));
}
exports["default"] = RootLayout;
