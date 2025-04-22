"use strict";
exports.__esModule = true;
exports.setAuthToken = void 0;
var axios_1 = require("axios");
var api = axios_1["default"].create({
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
});
var authToken = null;
function setAuthToken(token) {
    authToken = token;
    api.defaults.headers.common['Authorization'] = "Bearer " + token;
}
exports.setAuthToken = setAuthToken;
// Attach token before each request if available
api.interceptors.request.use(function (config) {
    if (authToken) {
        config.headers = config.headers || {};
        config.headers['Authorization'] = "Bearer " + authToken;
    }
    return config;
});
exports["default"] = api;
