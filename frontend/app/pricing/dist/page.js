"use client";
"use strict";
var __spreadArrays = (this && this.__spreadArrays) || function () {
    for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
    for (var r = Array(s), k = 0, i = 0; i < il; i++)
        for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
            r[k] = a[j];
    return r;
};
exports.__esModule = true;
var react_1 = require("react");
var navigation_1 = require("next/navigation");
var api_1 = require("../../utils/api");
var card_1 = require("@/components/ui/card");
var tabs_1 = require("@/components/ui/tabs");
var button_1 = require("@/components/ui/button");
var badge_1 = require("@/components/ui/badge");
var skeleton_1 = require("@/components/ui/skeleton");
var lucide_react_1 = require("lucide-react");
function PricingPage() {
    var router = navigation_1.useRouter();
    var _a = react_1.useState([]), models = _a[0], setModels = _a[1];
    var _b = react_1.useState(true), loading = _b[0], setLoading = _b[1];
    var _c = react_1.useState(null), error = _c[0], setError = _c[1];
    var _d = react_1.useState("all"), activeTab = _d[0], setActiveTab = _d[1];
    react_1.useEffect(function () {
        var token = localStorage.getItem("token");
        if (!token) {
            router.push("/login");
            return;
        }
        api_1.setAuthToken(token);
        // fetch current user to get organization_id
        api_1["default"]
            .get("/auth/me")
            .then(function (res) {
            var orgId = res.data.organization_id;
            return api_1["default"].get("/billing-models?org_id=" + orgId);
        })
            .then(function (res) { return setModels(res.data); })["catch"](function (err) { var _a, _b; return setError(((_b = (_a = err.response) === null || _a === void 0 ? void 0 : _a.data) === null || _b === void 0 ? void 0 : _b.detail) || err.message); })["finally"](function () { return setLoading(false); });
    }, [router]);
    var getModelIcon = function (type) {
        switch (type.toLowerCase()) {
            case "usage":
                return React.createElement(lucide_react_1.BarChart, { className: "h-5 w-5" });
            case "seat":
                return React.createElement(lucide_react_1.Users, { className: "h-5 w-5" });
            case "hybrid":
                return React.createElement(lucide_react_1.Zap, { className: "h-5 w-5" });
            default:
                return React.createElement(lucide_react_1.DollarSign, { className: "h-5 w-5" });
        }
    };
    var getModelTypeColor = function (type) {
        switch (type.toLowerCase()) {
            case "usage":
                return "bg-blue-20 text-blue border-blue";
            case "seat":
                return "bg-purple-20 text-purple border-purple";
            case "hybrid":
                return "bg-gold-20 text-gold-dark border-gold";
            default:
                return "bg-teal-20 text-teal border-teal";
        }
    };
    var filteredModels = activeTab === "all" ? models : models.filter(function (model) { return model.model_type.toLowerCase() === activeTab; });
    if (loading) {
        return (React.createElement("div", { className: "p-8 space-y-6 max-w-[1200px] mx-auto" },
            React.createElement("div", { className: "flex items-center justify-between" },
                React.createElement(skeleton_1.Skeleton, { className: "h-10 w-[250px]" }),
                React.createElement(skeleton_1.Skeleton, { className: "h-10 w-[120px]" })),
            React.createElement(skeleton_1.Skeleton, { className: "h-12 w-[400px] rounded-lg" }),
            React.createElement("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" }, __spreadArrays(Array(3)).map(function (_, i) { return (React.createElement(skeleton_1.Skeleton, { key: i, className: "h-[300px] w-full rounded-xl" })); }))));
    }
    if (error) {
        return (React.createElement("div", { className: "p-8 flex flex-col items-center justify-center min-h-[50vh] text-center" },
            React.createElement("div", { className: "rounded-full bg-destructive/10 p-4 mb-4" },
                React.createElement(lucide_react_1.AlertCircle, { className: "h-8 w-8 text-destructive" })),
            React.createElement("h2", { className: "text-2xl font-bold mb-2" }, "Error Loading Pricing Models"),
            React.createElement("p", { className: "text-gray-dark mb-4" }, error),
            React.createElement(button_1.Button, { onClick: function () { return window.location.reload(); } }, "Try Again")));
    }
    return (React.createElement("div", { className: "p-4 md:p-8 space-y-8 max-w-[1200px] mx-auto" },
        React.createElement("div", { className: "flex flex-col md:flex-row justify-between items-start md:items-center gap-4" },
            React.createElement("div", null,
                React.createElement("h1", { className: "text-3xl font-bold" }, "Pricing Models"),
                React.createElement("p", { className: "text-gray-dark" }, "Manage your pricing strategies and billing configurations")),
            React.createElement(button_1.Button, { className: "gap-2" },
                React.createElement(lucide_react_1.Plus, { className: "h-4 w-4" }),
                "Create New Model")),
        React.createElement(tabs_1.Tabs, { defaultValue: "all", value: activeTab, onValueChange: setActiveTab, className: "w-full" },
            React.createElement(tabs_1.TabsList, { className: "grid grid-cols-4 w-full max-w-md" },
                React.createElement(tabs_1.TabsTrigger, { value: "all" }, "All"),
                React.createElement(tabs_1.TabsTrigger, { value: "usage" }, "Usage"),
                React.createElement(tabs_1.TabsTrigger, { value: "seat" }, "Seat"),
                React.createElement(tabs_1.TabsTrigger, { value: "hybrid" }, "Hybrid"))),
        filteredModels.length === 0 ? (React.createElement("div", { className: "flex flex-col items-center justify-center py-12 text-center" },
            React.createElement("div", { className: "rounded-full bg-muted p-4 mb-4" },
                React.createElement(lucide_react_1.Settings, { className: "h-8 w-8 text-muted-foreground" })),
            React.createElement("h2", { className: "text-xl font-bold mb-2" }, "No pricing models found"),
            React.createElement("p", { className: "text-gray-dark mb-4" }, "Create your first pricing model to get started"),
            React.createElement(button_1.Button, { className: "gap-2" },
                React.createElement(lucide_react_1.Plus, { className: "h-4 w-4" }),
                "Create New Model"))) : (React.createElement("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" }, filteredModels.map(function (model) { return (React.createElement(card_1.Card, { key: model.id, className: "overflow-hidden" },
            React.createElement(card_1.CardHeader, { className: "pb-4" },
                React.createElement("div", { className: "flex justify-between items-start" },
                    React.createElement(badge_1.Badge, { className: getModelTypeColor(model.model_type) + " px-2 py-0.5 text-xs font-medium" }, model.model_type),
                    React.createElement("div", { className: "flex gap-1" },
                        React.createElement(button_1.Button, { className: "h-8 w-8" },
                            React.createElement(lucide_react_1.Edit, { className: "h-4 w-4" })),
                        React.createElement(button_1.Button, { className: "h-8 w-8 text-destructive" },
                            React.createElement(lucide_react_1.Trash2, { className: "h-4 w-4" })))),
                React.createElement("div", { className: "flex items-center gap-2 mt-2" },
                    React.createElement("div", { className: "rounded-full p-2 " + getModelTypeColor(model.model_type) }, getModelIcon(model.model_type)),
                    React.createElement(card_1.CardTitle, null, model.name)),
                React.createElement(card_1.CardDescription, null, model.description || "A " + model.model_type.toLowerCase() + " pricing model for your services")),
            React.createElement(card_1.CardContent, { className: "pb-4" },
                React.createElement("div", { className: "bg-gray-20 rounded-lg p-3 overflow-auto max-h-[200px]" },
                    React.createElement("pre", { className: "text-xs font-mono" }, JSON.stringify(model.config, null, 2)))),
            React.createElement(card_1.CardFooter, { className: "flex justify-between border-t pt-4" },
                React.createElement("div", { className: "flex items-center text-sm" },
                    React.createElement(lucide_react_1.CheckCircle2, { className: "h-4 w-4 text-success mr-1" }),
                    "Active"),
                React.createElement(button_1.Button, { className: "gap-1 text-sm" },
                    React.createElement(lucide_react_1.Copy, { className: "h-3 w-3" }),
                    "Duplicate")))); })))));
}
exports["default"] = PricingPage;
