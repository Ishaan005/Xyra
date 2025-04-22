"use strict";
exports.__esModule = true;
exports.HeroSection = void 0;
var button_1 = require("@/components/ui/button");
var lucide_react_1 = require("lucide-react");
function HeroSection() {
    return (React.createElement("section", { className: "relative overflow-hidden bg-gradient-to-b from-white to-gold-20 py-20 md:py-32" },
        React.createElement("div", { className: "container px-4 md:px-6" },
            React.createElement("div", { className: "grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]" },
                React.createElement("div", { className: "flex flex-col justify-center space-y-4" },
                    React.createElement("div", { className: "space-y-2" },
                        React.createElement("h1", { className: "text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl" },
                            React.createElement("span", { className: "inline-block text-primary" }, "\uD83D\uDCA1"),
                            " Monetize Your AI Platform Smarter. Automatically."),
                        React.createElement("p", { className: "max-w-[700px] text-lg text-gray-dark md:text-xl" }, "Business Engine is the plug-and-play monetization layer for AI SaaS. Drop it into your backend to unlock dynamic pricing, margin analytics, and outcome-based billing\u2014without changing your architecture.")),
                    React.createElement("div", { className: "flex flex-col gap-2 min-[400px]:flex-row" },
                        React.createElement(button_1.Button, { size: "lg", className: "font-bold" }, "Book a Demo"),
                        React.createElement(button_1.Button, { size: "lg", variant: "outline", className: "font-bold" }, "View Docs"),
                        React.createElement(button_1.Button, { size: "lg", variant: "secondary", className: "font-bold" }, "Try Prototype"))),
                React.createElement("div", { className: "flex items-center justify-center" },
                    React.createElement("div", { className: "relative h-[350px] w-[350px] md:h-[400px] md:w-[400px] lg:h-[500px] lg:w-[500px]" },
                        React.createElement("div", { className: "absolute inset-0 flex items-center justify-center" },
                            React.createElement("div", { className: "h-full w-full rounded-full bg-gradient-to-br from-gold-light to-gold-dark opacity-20 blur-3xl" })),
                        React.createElement("div", { className: "relative flex h-full w-full items-center justify-center rounded-xl border border-border bg-white/80 p-4 backdrop-blur-sm" },
                            React.createElement("div", { className: "grid gap-4" },
                                React.createElement("div", { className: "flex items-center gap-2 rounded-lg bg-gold-20 p-3" },
                                    React.createElement(lucide_react_1.BarChart3, { className: "h-5 w-5 text-gold-dark" }),
                                    React.createElement("span", { className: "font-bold" }, "Margin Analytics"),
                                    React.createElement("span", { className: "ml-auto rounded-full bg-success px-2 py-0.5 text-xs text-white" }, "+24%")),
                                React.createElement("div", { className: "flex items-center gap-2 rounded-lg bg-blue-20 p-3" },
                                    React.createElement(lucide_react_1.Zap, { className: "h-5 w-5 text-blue" }),
                                    React.createElement("span", { className: "font-bold" }, "Dynamic Pricing"),
                                    React.createElement("span", { className: "ml-auto rounded-full bg-success px-2 py-0.5 text-xs text-white" }, "Active")),
                                React.createElement("div", { className: "grid grid-cols-2 gap-2" },
                                    React.createElement("div", { className: "rounded-lg bg-purple-20 p-3" },
                                        React.createElement("div", { className: "text-sm font-bold" }, "Revenue"),
                                        React.createElement("div", { className: "text-xl font-bold text-purple" }, "$12,450")),
                                    React.createElement("div", { className: "rounded-lg bg-teal-20 p-3" },
                                        React.createElement("div", { className: "text-sm font-bold" }, "Margin"),
                                        React.createElement("div", { className: "text-xl font-bold text-teal" }, "68.5%")))))))))));
}
exports.HeroSection = HeroSection;
