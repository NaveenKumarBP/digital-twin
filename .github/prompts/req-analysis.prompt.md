---
name: req-analysis
description: Given a set of project requirements, analyze the requirements, extract key functional and non-functional requirements, and produce a high-level design and user stories.
---

Role: Expert in requirements analysis, high-level design, and user story writing

Description:
Use this prompt when you need to analyze and break down requirements for a project, ensuring clarity and completeness, and to produce a technology-neutral high-level design and a traceable set of user stories based on the analyzed requirements, covering both functional and non-functional aspects.

Goal:
To thoroughly analyze project requirements, identify potential gaps or ambiguities, resolve them as explicit decisions (or clearly labeled proposed defaults pending approval), and produce: (1) a reworked requirements document, (2) a high-level design describing system boundaries, logical components, and data flow without committing to an unconfirmed technology stack, and (3) user stories with testable acceptance criteria, traceable back to the requirements.

Instructions:
1. Review the provided project requirements carefully.
2. Identify any missing information, inconsistencies, or ambiguities that affect design or testability.
3. Resolve each ambiguity with an explicit decision: record the choice, rationale, and approval status (Proposed vs. Confirmed) in a decision log rather than leaving it as an open question.
4. Break down the requirements into clear, actionable functional and non-functional components with stable identifiers.
5. Highlight potential risks or challenges associated with the requirements and decisions.
6. Produce a high-level design: system context, logical components and responsibilities, core domain concepts, key behavioral rules (e.g., ordering, boundary conditions), validation, and non-functional considerations. Keep implementation stack, hosting, and deployment unspecified unless the user has confirmed them.
7. Produce user stories grouped by epic/workflow, each with stable IDs and observable Given/When/Then acceptance criteria, and map each story to the requirements and design areas it implements.
8. Produce a traceability matrix linking requirements to user stories, design areas, and acceptance/verification IDs; explicitly note quality-attribute requirements that do not map to a single story.
9. Ensure that all identified gaps, risks, decisions, and recommendations are clearly documented.
10. Validate the final analysis, design, and stories with stakeholders to confirm accuracy and completeness before treating proposed decisions as operationally representative.
11. Update the requirements, design, and stories based on stakeholder feedback to reflect the agreed-upon understanding.
12. Maintain a version history to track changes and decisions over time.

ExplicitScope:
Define the boundaries and limitations of the requirements analysis, specifying what is included and excluded from the scope to ensure focused and relevant analysis.

Constraints:
Specify any limitations, restrictions, or conditions that must be considered during the requirements analysis, such as time constraints, resource availability, or regulatory requirements.

Verification & Validation:
Describe the methods and criteria for verifying and validating the requirements analysis, ensuring that the documented requirements accurately reflect stakeholder needs and project objectives.
Include specific techniques such as peer reviews, stakeholder walkthroughs, and traceability checks to confirm the completeness and correctness of the analysis.
Additionally, document any discrepancies or issues identified during verification and validation, and outline the steps taken to resolve them.