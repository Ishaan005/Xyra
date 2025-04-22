"use client";
"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
exports.__esModule = true;
var react_1 = require("react");
var navigation_1 = require("next/navigation");
var api_1 = require("@/utils/api");
var card_1 = require("@/components/ui/card");
var button_1 = require("@/components/ui/button");
var input_1 = require("@/components/ui/input");
var label_1 = require("@/components/ui/label");
var lucide_react_1 = require("lucide-react");
var link_1 = require("next/link");
function LoginPage() {
    var _this = this;
    var router = navigation_1.useRouter();
    var _a = react_1.useState(""), email = _a[0], setEmail = _a[1];
    var _b = react_1.useState(""), password = _b[0], setPassword = _b[1];
    var _c = react_1.useState(null), error = _c[0], setError = _c[1];
    var _d = react_1.useState(false), isLoading = _d[0], setIsLoading = _d[1];
    var handleSubmit = function (e) { return __awaiter(_this, void 0, void 0, function () {
        var params, res, token, err_1;
        var _a, _b;
        return __generator(this, function (_c) {
            switch (_c.label) {
                case 0:
                    e.preventDefault();
                    setError(null);
                    setIsLoading(true);
                    _c.label = 1;
                case 1:
                    _c.trys.push([1, 3, 4, 5]);
                    params = new URLSearchParams();
                    params.append("username", email);
                    params.append("password", password);
                    return [4 /*yield*/, api_1["default"].post("/auth/login", params, {
                            headers: { "Content-Type": "application/x-www-form-urlencoded" }
                        })];
                case 2:
                    res = _c.sent();
                    token = res.data.access_token;
                    localStorage.setItem("token", token);
                    api_1.setAuthToken(token);
                    router.push("/dashboard");
                    return [3 /*break*/, 5];
                case 3:
                    err_1 = _c.sent();
                    setError(((_b = (_a = err_1.response) === null || _a === void 0 ? void 0 : _a.data) === null || _b === void 0 ? void 0 : _b.detail) || err_1.message);
                    return [3 /*break*/, 5];
                case 4:
                    setIsLoading(false);
                    return [7 /*endfinally*/];
                case 5: return [2 /*return*/];
            }
        });
    }); };
    return (React.createElement("div", { className: "min-h-screen flex items-center justify-center bg-gradient-to-b from-white to-gold-20 p-4" },
        React.createElement("div", { className: "w-full max-w-md" },
            React.createElement("div", { className: "text-center mb-8" },
                React.createElement("h1", { className: "text-3xl font-bold" }, "Business Engine"),
                React.createElement("p", { className: "text-gray-dark mt-2" }, "Sign in to your account")),
            React.createElement(card_1.Card, null,
                React.createElement(card_1.CardHeader, null,
                    React.createElement(card_1.CardTitle, null, "Sign In"),
                    React.createElement(card_1.CardDescription, null, "Enter your credentials to access your account")),
                React.createElement(card_1.CardContent, null,
                    error && (React.createElement("div", { className: "bg-destructive/10 text-destructive rounded-lg p-3 flex items-start gap-2 mb-4" },
                        React.createElement(lucide_react_1.AlertCircle, { className: "h-5 w-5 mt-0.5 flex-shrink-0" }),
                        React.createElement("p", { className: "text-sm" }, error))),
                    React.createElement("form", { onSubmit: handleSubmit, className: "space-y-4" },
                        React.createElement("div", { className: "space-y-2" },
                            React.createElement(label_1.Label, { htmlFor: "email" }, "Email"),
                            React.createElement("div", { className: "relative" },
                                React.createElement(lucide_react_1.Mail, { className: "absolute left-3 top-3 h-4 w-4 text-gray-dark" }),
                                React.createElement(input_1.Input, { id: "email", type: "email", placeholder: "name@company.com", value: email, onChange: function (e) { return setEmail(e.target.value); }, className: "pl-10", required: true }))),
                        React.createElement("div", { className: "space-y-2" },
                            React.createElement("div", { className: "flex items-center justify-between" },
                                React.createElement(label_1.Label, { htmlFor: "password" }, "Password"),
                                React.createElement(link_1["default"], { href: "/forgot-password", className: "text-xs text-primary hover:underline" }, "Forgot password?")),
                            React.createElement("div", { className: "relative" },
                                React.createElement(lucide_react_1.Lock, { className: "absolute left-3 top-3 h-4 w-4 text-gray-dark" }),
                                React.createElement(input_1.Input, { id: "password", type: "password", placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", value: password, onChange: function (e) { return setPassword(e.target.value); }, className: "pl-10", required: true }))),
                        React.createElement(button_1.Button, { type: "submit", className: "w-full", disabled: isLoading }, isLoading ? "Signing in..." : "Sign In"))),
                React.createElement(card_1.CardFooter, { className: "flex flex-col space-y-4" },
                    React.createElement("div", { className: "text-center text-sm" },
                        React.createElement("span", { className: "text-gray-dark" }, "Don't have an account? "),
                        React.createElement(link_1["default"], { href: "/signup", className: "text-primary font-medium hover:underline" }, "Sign up")),
                    React.createElement("div", { className: "text-center text-xs text-gray-dark" },
                        "By signing in, you agree to our",
                        React.createElement(link_1["default"], { href: "/terms", className: "text-primary hover:underline mx-1" }, "Terms of Service"),
                        "and",
                        React.createElement(link_1["default"], { href: "/privacy", className: "text-primary hover:underline ml-1" }, "Privacy Policy")))))));
}
exports["default"] = LoginPage;
