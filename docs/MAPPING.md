# SmartAIPlatForm Documentation Mapping & Index

**Last Updated:** February 1, 2026

**Review Reminder:** Review and update this mapping after each major milestone or quarterly.

## Table of Contents
1. [Overview](#overview)
2. [Mapping Table](#mapping-table)
3. [How to Use](#how-to-use)
4. [Glossary](#glossary)
5. [Change History](#change-history)

## Overview
_This table maps each major technology/component to its coverage in the core documentation files for easy navigation, traceability, and review._

## Accessibility
All tables and links include descriptive text for accessibility. Use alt text for any added visuals.

## Mapping Table

Below, each ✓ links directly to the relevant section in the respective document for that technology/component.

| Technology/Component      | Architecture.md | Infrastructure.md | Technology-Comparison.md | Requirements.md |
|--------------------------|:---------------:|:-----------------:|:-----------------------:|:---------------:|
| Frontend (React)         | [✓](architecture.md#frontend) | [✓](infrastructure.md#frontend) | [✓](technology-comparison.md#frontend) | [✓](requirements.md#frontend) |
| Backend (FastAPI)        | [✓](architecture.md#backend) | [✓](infrastructure.md#backend) | [✓](technology-comparison.md#backend) | [✓](requirements.md#backend) |
| Database (PostgreSQL)    | [✓](architecture.md#database) | [✓](infrastructure.md#postgresql) | [✓](technology-comparison.md#database) | [✓](requirements.md#database) |
| State Management         | [✓](architecture.md#state-management-frontend) | [✓](infrastructure.md#component-table) | [✓](technology-comparison.md#state-management-frontend) | [✓](requirements.md#frontend) |
| UI Libraries (MUI, etc.) | [✓](architecture.md#ui-libraries) | [✓](infrastructure.md#component-table) | [✓](technology-comparison.md#ui-libraries) | [✓](requirements.md#frontend) |
| Containerization         | [✓](architecture.md#containerization) | [✓](infrastructure.md#docker) | [✓](technology-comparison.md#containerization) | [✓](requirements.md#containerization--orchestration) |
| CI/CD                    | [✓](architecture.md#cicd-pipeline) | [✓](infrastructure.md#cicd-pipeline) | [✓](technology-comparison.md#cicd) | [✓](requirements.md#cicd--automation) |
| Task Queues              | [✓](architecture.md#task-queues) | [✓](infrastructure.md#component-table) | [✓](technology-comparison.md#task-queues) | [✓](requirements.md#backend) |
| Environment Management   | [✓](architecture.md#python-environment) | [✓](infrastructure.md#python-environment) | [✓](technology-comparison.md#environment-management) | [✓](requirements.md#environment-management) |
| File Storage (S3/MinIO)  | [✓](architecture.md#file-storage) | [✓](infrastructure.md#component-table) | [✓](technology-comparison.md#file-storage) | [✓](requirements.md#file-handling) |
| Monitoring/Observability | [✓](architecture.md#monitoringobservability) | [✓](infrastructure.md#component-table) | [✓](technology-comparison.md#monitoringobservability) | [✓](requirements.md#health--monitoring) |
| Linting/Automation       | [✓](architecture.md#git-automation--validation) | [✓](infrastructure.md#git-automation--validation) | [✓](technology-comparison.md#lintingautomation) | [✓](requirements.md#cicd--automation) |
| Git Automation           | [✓](architecture.md#git-automation--validation) | [✓](infrastructure.md#git-automation--validation) | [✓](technology-comparison.md#lintingautomation) | [✓](requirements.md#cicd--automation) |
| Security/Backup/Resilience| [✓](architecture.md#security) | [✓](infrastructure.md#component-table) | [✓](technology-comparison.md#component-table) | [✓](requirements.md#security) |
| AI/MCP Integration       | [✓](architecture.md#aimcp-assistant) | [✓](infrastructure.md#component-table) | [✓](technology-comparison.md#ai-mcp-assistant) | [✓](requirements.md#ai-mcp-assistant) |
| Testing Strategy         | [✓](architecture.md#testing) | [✓](infrastructure.md#component-table) | [✓](technology-comparison.md#testing) | [✓](requirements.md#testing) |
| Accessibility/i18n       | [✓](architecture.md#accessibility) | [✓](infrastructure.md#component-table) | [✓](technology-comparison.md#component-table) | [✓](requirements.md#accessibility) |


> ✓ = This topic is covered in the respective document. For details, see the relevant section in each file.

## Glossary
- **Traceability:** Ability to map requirements, code, and documentation for audit and review.
- **Alt text:** Textual description for images to support accessibility.

## Change History
| Date | Change | Author |
|------|--------|--------|
| 2026-02-01 | Major cleanup, TOC, glossary, accessibility, review reminder | GitHub Copilot |

---


## Automation & Cross-Referencing Best Practices
- All core documentation is cross-linked at the section level for rapid navigation.
- Use the mapping table above to jump directly to the relevant section in any doc.
- Each document's "See Also" section links to all other core docs.
- For automation, see [github-setup.md](github-setup.md#project-progress-tracking--automation) for issue-driven progress tracking and [progress.md](progress.md) for actionable task lists.

**How to Use:**
- Use this table to quickly locate and jump to the exact section for each technology or architectural concern.
- For deep dives, follow the "See Also" links at the top of each document.
