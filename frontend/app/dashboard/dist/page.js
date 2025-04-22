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
var api_1 = require("@/utils/api");
var api_2 = require("@/utils/api");
var card_1 = require("@/components/ui/card");
var tabs_1 = require("@/components/ui/tabs");
var chart_1 = require("@/components/ui/chart");
var lucide_react_1 = require("lucide-react");
var button_1 = require("@/components/ui/button");
var skeleton_1 = require("@/components/ui/skeleton");
function DashboardPage() {
    var orgId = 1; // TODO: obtain dynamically
    var _a = react_1.useState(null), summary = _a[0], setSummary = _a[1];
    var _b = react_1.useState([]), topAgents = _b[0], setTopAgents = _b[1];
    var _c = react_1.useState(true), loading = _c[0], setLoading = _c[1];
    var _d = react_1.useState(null), error = _d[0], setError = _d[1];
    var _e = react_1.useState("month"), period = _e[0], setPeriod = _e[1];
    react_1.useEffect(function () {
        // Load token from localStorage if present
        var token = localStorage.getItem("token");
        if (token)
            api_1.setAuthToken(token);
        Promise.all([
            api_2["default"].get("/analytics/organization/" + orgId + "/summary"),
            api_2["default"].get("/analytics/organization/" + orgId + "/top-agents?limit=5"),
        ])
            .then(function (_a) {
            var sumRes = _a[0], topRes = _a[1];
            setSummary(sumRes.data);
            setTopAgents(topRes.data);
        })["catch"](function (err) { return setError(err.message); })["finally"](function () { return setLoading(false); });
    }, []);
    if (loading) {
        return (React.createElement("div", { className: "p-8 space-y-6" },
            React.createElement("div", { className: "flex items-center justify-between" },
                React.createElement(skeleton_1.Skeleton, { className: "h-10 w-[250px]" }),
                React.createElement(skeleton_1.Skeleton, { className: "h-10 w-[120px]" })),
            React.createElement("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-6" }, __spreadArrays(Array(6)).map(function (_, i) { return (React.createElement(skeleton_1.Skeleton, { key: i, className: "h-[120px] w-full rounded-xl" })); })),
            React.createElement(skeleton_1.Skeleton, { className: "h-[350px] w-full rounded-xl" })));
    }
    if (error) {
        return (React.createElement("div", { className: "p-8 flex flex-col items-center justify-center min-h-[50vh] text-center" },
            React.createElement("div", { className: "rounded-full bg-destructive/10 p-4 mb-4" },
                React.createElement(lucide_react_1.TrendingDown, { className: "h-8 w-8 text-destructive" })),
            React.createElement("h2", { className: "text-2xl font-bold mb-2" }, "Error Loading Dashboard"),
            React.createElement("p", { className: "text-gray-dark mb-4" }, error),
            React.createElement(button_1.Button, { onClick: function () { return window.location.reload(); } }, "Try Again")));
    }
    var agentLabels = topAgents.map(function (a) { return a.name; });
    var revenueData = topAgents.map(function (a) { return a.metrics.total_revenue; });
    var costData = topAgents.map(function (a) { return a.metrics.total_cost; });
    var marginData = topAgents.map(function (a) { return Math.round(a.metrics.margin * 100); });
    var barData = {
        labels: agentLabels,
        datasets: [
            {
                label: "Revenue",
                data: revenueData,
                backgroundColor: "#FFB500",
                borderColor: "#AF6D04",
                borderWidth: 1
            },
            {
                label: "Cost",
                data: costData,
                backgroundColor: "#B83C27",
                borderColor: "#8A2A1D",
                borderWidth: 1
            },
        ]
    };
    var marginChartData = {
        labels: agentLabels,
        datasets: [
            {
                label: "Margin %",
                data: marginData,
                borderColor: "#3A913F",
                backgroundColor: "rgba(58, 145, 63, 0.1)",
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: "#3A913F",
                pointRadius: 4
            },
        ]
    };
    var formatDate = function (dateString) {
        return new Date(dateString).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric"
        });
    };
    return (React.createElement("div", { className: "p-4 md:p-8 space-y-8 max-w-[1400px] mx-auto" },
        React.createElement("div", { className: "flex flex-col md:flex-row justify-between items-start md:items-center gap-4" },
            React.createElement("div", null,
                React.createElement("h1", { className: "text-3xl font-bold" }, "Organization Dashboard"),
                React.createElement("p", { className: "text-gray-dark" },
                    formatDate(summary.period.start_date),
                    " \u2013 ",
                    formatDate(summary.period.end_date))),
            React.createElement(tabs_1.Tabs, { defaultValue: "month", value: period, onValueChange: setPeriod, className: "w-full md:w-auto" },
                React.createElement(tabs_1.TabsList, { className: "grid grid-cols-3 w-full md:w-[300px]" },
                    React.createElement(tabs_1.TabsTrigger, { value: "week" }, "Week"),
                    React.createElement(tabs_1.TabsTrigger, { value: "month" }, "Month"),
                    React.createElement(tabs_1.TabsTrigger, { value: "quarter" }, "Quarter")))),
        React.createElement("div", { className: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" },
            React.createElement(card_1.Card, null,
                React.createElement(card_1.CardHeader, { className: "flex flex-row items-center justify-between pb-2" },
                    React.createElement(card_1.CardTitle, { className: "text-sm font-medium" }, "Total Revenue"),
                    React.createElement(lucide_react_1.DollarSign, { className: "h-4 w-4 text-gold-dark" })),
                React.createElement(card_1.CardContent, null,
                    React.createElement("div", { className: "text-2xl font-bold" },
                        "$",
                        summary.metrics.total_revenue.toFixed(2)),
                    React.createElement("p", { className: "text-xs text-gray-dark" }, "+12.5% from previous period"))),
            React.createElement(card_1.Card, null,
                React.createElement(card_1.CardHeader, { className: "flex flex-row items-center justify-between pb-2" },
                    React.createElement(card_1.CardTitle, { className: "text-sm font-medium" }, "Total Cost"),
                    React.createElement(lucide_react_1.CreditCard, { className: "h-4 w-4 text-destructive" })),
                React.createElement(card_1.CardContent, null,
                    React.createElement("div", { className: "text-2xl font-bold" },
                        "$",
                        summary.metrics.total_cost.toFixed(2)),
                    React.createElement("p", { className: "text-xs text-gray-dark" }, "+8.1% from previous period"))),
            React.createElement(card_1.Card, null,
                React.createElement(card_1.CardHeader, { className: "flex flex-row items-center justify-between pb-2" },
                    React.createElement(card_1.CardTitle, { className: "text-sm font-medium" }, "Margin %"),
                    React.createElement(lucide_react_1.Percent, { className: "h-4 w-4 text-success" })),
                React.createElement(card_1.CardContent, null,
                    React.createElement("div", { className: "text-2xl font-bold" },
                        (summary.metrics.margin * 100).toFixed(1),
                        "%"),
                    React.createElement("p", { className: "text-xs text-gray-dark" }, "+2.3% from previous period"))),
            React.createElement(card_1.Card, null,
                React.createElement(card_1.CardHeader, { className: "flex flex-row items-center justify-between pb-2" },
                    React.createElement(card_1.CardTitle, { className: "text-sm font-medium" }, "Activity Count"),
                    React.createElement(lucide_react_1.Activity, { className: "h-4 w-4 text-blue" })),
                React.createElement(card_1.CardContent, null,
                    React.createElement("div", { className: "text-2xl font-bold" }, summary.metrics.activity_count.toLocaleString()),
                    React.createElement("p", { className: "text-xs text-gray-dark" }, "+18.2% from previous period"))),
            React.createElement(card_1.Card, null,
                React.createElement(card_1.CardHeader, { className: "flex flex-row items-center justify-between pb-2" },
                    React.createElement(card_1.CardTitle, { className: "text-sm font-medium" }, "Total Agents"),
                    React.createElement(lucide_react_1.Users, { className: "h-4 w-4 text-purple" })),
                React.createElement(card_1.CardContent, null,
                    React.createElement("div", { className: "text-2xl font-bold" }, summary.agents.total),
                    React.createElement("p", { className: "text-xs text-gray-dark" },
                        summary.agents.active,
                        " active"))),
            React.createElement(card_1.Card, null,
                React.createElement(card_1.CardHeader, { className: "flex flex-row items-center justify-between pb-2" },
                    React.createElement(card_1.CardTitle, { className: "text-sm font-medium" }, "Growth Rate"),
                    React.createElement(lucide_react_1.TrendingUp, { className: "h-4 w-4 text-teal" })),
                React.createElement(card_1.CardContent, null,
                    React.createElement("div", { className: "text-2xl font-bold" }, "+15.4%"),
                    React.createElement("p", { className: "text-xs text-gray-dark" }, "Month over month")))),
        React.createElement("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-8" },
            React.createElement(card_1.Card, { className: "col-span-1" },
                React.createElement(card_1.CardHeader, null,
                    React.createElement(card_1.CardTitle, null, "Top Agents by Revenue & Cost"),
                    React.createElement(card_1.CardDescription, null, "Comparing revenue and costs across your top performing agents")),
                React.createElement(card_1.CardContent, { className: "pl-2" },
                    React.createElement(chart_1.BarChart, { data: barData, options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: "top"
                                },
                                tooltip: {
                                    mode: "index",
                                    intersect: false
                                }
                            },
                            scales: {
                                x: {
                                    grid: {
                                        display: false
                                    }
                                },
                                y: {
                                    beginAtZero: true,
                                    grid: {
                                        color: "rgba(0, 0, 0, 0.05)"
                                    }
                                }
                            }
                        }, className: "aspect-[4/3]" }))),
            React.createElement(card_1.Card, { className: "col-span-1" },
                React.createElement(card_1.CardHeader, null,
                    React.createElement(card_1.CardTitle, null, "Margin Analysis"),
                    React.createElement(card_1.CardDescription, null, "Profit margin percentage by agent")),
                React.createElement(card_1.CardContent, { className: "pl-2" },
                    React.createElement(chart_1.LineChart, { data: marginChartData, options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: "top"
                                },
                                tooltip: {
                                    mode: "index",
                                    intersect: false
                                }
                            },
                            scales: {
                                x: {
                                    grid: {
                                        display: false
                                    }
                                },
                                y: {
                                    beginAtZero: true,
                                    grid: {
                                        color: "rgba(0, 0, 0, 0.05)"
                                    },
                                    ticks: {
                                        callback: function (value) { return value + "%"; }
                                    }
                                }
                            }
                        }, className: "aspect-[4/3]" }))))));
}
exports["default"] = DashboardPage;
