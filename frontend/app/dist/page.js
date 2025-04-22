"use strict";
exports.__esModule = true;
var hero_section_1 = require("@/components/hero-section");
var problem_section_1 = require("@/components/problem-section");
var solution_section_1 = require("@/components/solution-section");
var how_it_works_1 = require("@/components/how-it-works");
var prototype_section_1 = require("@/components/prototype-section");
var teams_section_1 = require("@/components/teams-section");
var integration_section_1 = require("@/components/integration-section");
var testimonials_section_1 = require("@/components/testimonials-section");
var cta_section_1 = require("@/components/cta-section");
var footer_1 = require("@/components/footer");
function Home() {
    return (React.createElement("div", { className: "flex min-h-screen flex-col" },
        React.createElement("main", { className: "flex-1" },
            React.createElement(hero_section_1.HeroSection, null),
            React.createElement(problem_section_1.ProblemSection, null),
            React.createElement(solution_section_1.SolutionSection, null),
            React.createElement(how_it_works_1.HowItWorks, null),
            React.createElement(prototype_section_1.PrototypeSection, null),
            React.createElement(teams_section_1.TeamsSection, null),
            React.createElement(integration_section_1.IntegrationSection, null),
            React.createElement(testimonials_section_1.TestimonialsSection, null),
            React.createElement(cta_section_1.CTASection, null)),
        React.createElement(footer_1.Footer, null)));
}
exports["default"] = Home;
