"use strict";
exports.__esModule = true;
exports.CTASection = void 0;
var button_1 = require("@/components/ui/button");
var lucide_react_1 = require("lucide-react");
function CTASection() {
    return (React.createElement("section", { className: "bg-gradient-to-b from-white to-gold-20 py-20" },
        React.createElement("div", { className: "container px-4 md:px-6" },
            React.createElement("div", { className: "mx-auto max-w-[800px] text-center" },
                React.createElement("h2", { className: "text-3xl font-bold tracking-tighter text-foreground sm:text-4xl md:text-5xl" }, "Ready to make your AI SaaS more profitable?"),
                React.createElement("p", { className: "mt-4 text-lg text-gray-dark" }, "Get started with Business Engine today and transform how you monetize your AI platform."),
                React.createElement("div", { className: "mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center" },
                    React.createElement(button_1.Button, { size: "lg", className: "gap-2 font-bold" },
                        React.createElement(lucide_react_1.Search, { className: "h-5 w-5" }),
                        "Explore the Docs"),
                    React.createElement(button_1.Button, { size: "lg", variant: "secondary", className: "gap-2 font-bold" },
                        React.createElement(lucide_react_1.Phone, { className: "h-5 w-5" }),
                        "Book a Demo"),
                    React.createElement(button_1.Button, { size: "lg", variant: "outline", className: "gap-2 font-bold" },
                        React.createElement(lucide_react_1.FileText, { className: "h-5 w-5" }),
                        "Get Early Access"))))));
}
exports.CTASection = CTASection;
