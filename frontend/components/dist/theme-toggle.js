"use client";
"use strict";
exports.__esModule = true;
exports.ThemeToggle = void 0;
var lucide_react_1 = require("lucide-react");
var next_themes_1 = require("next-themes");
var button_1 = require("@/components/ui/button");
function ThemeToggle() {
    var _a = next_themes_1.useTheme(), theme = _a.theme, setTheme = _a.setTheme;
    return (React.createElement(button_1.Button, { variant: "outline", size: "icon", onClick: function () { return setTheme(theme === "dark" ? "light" : "dark"); }, className: "rounded-full" },
        React.createElement(lucide_react_1.Sun, { className: "h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" }),
        React.createElement(lucide_react_1.Moon, { className: "absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" }),
        React.createElement("span", { className: "sr-only" }, "Toggle theme")));
}
exports.ThemeToggle = ThemeToggle;
