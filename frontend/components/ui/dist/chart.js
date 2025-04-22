"use client";
"use strict";
exports.__esModule = true;
exports.LineChart = exports.BarChart = void 0;
var react_chartjs_2_1 = require("react-chartjs-2");
var chart_js_1 = require("chart.js");
chart_js_1.Chart.register(chart_js_1.CategoryScale, chart_js_1.LinearScale, chart_js_1.BarElement, chart_js_1.Title, chart_js_1.Tooltip, chart_js_1.Legend, chart_js_1.PointElement, chart_js_1.LineElement, chart_js_1.Filler);
function BarChart(_a) {
    var data = _a.data, options = _a.options, className = _a.className;
    return (React.createElement("div", { className: className },
        React.createElement(react_chartjs_2_1.Bar, { data: data, options: options })));
}
exports.BarChart = BarChart;
function LineChart(_a) {
    var data = _a.data, options = _a.options, className = _a.className;
    return (React.createElement("div", { className: className },
        React.createElement(react_chartjs_2_1.Line, { data: data, options: options })));
}
exports.LineChart = LineChart;
