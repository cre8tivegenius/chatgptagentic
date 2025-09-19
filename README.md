# Codex Prompt: Regenerate This MPC Stack 1000x Better

You are an expert in production-ready full stack development, security, and mathematical optimization. Your goal is to regenerate this Model Predictive Control (MPC) server stack, making it dramatically better and more robust in every respect.

## Current Stack

- **API Gateway:** Go, strict middleware (logging, CORS, rate limiting), healthchecks
- **Optimizer:** Python (Flask + CVXPY), linear problems, OSQP primary, SCS fallback, strict validation & error handling
- **Frontend:** Mobile-friendly `index.html` for quick testing
- **DevOps:** Docker Compose, healthchecks for all services

## Requirements

- Security: Harden all layers (auth, input validation, no code injection, CORS, rate limits, etc.)
- Observability: Add structured logging, request/response tracing, metrics (Prometheus, Grafana), alerting
- Testing: Unit, integration, e2e, and property-based tests for optimizer
- CI: Full build, test, lint, security scan, and deploy pipeline (GitHub Actions)
- Acceptance: Must pass all tests, healthchecks, and performance under load

## Acceptance Criteria

1. All services are containerized, with clear dependency management and healthchecks.
2. All endpoints are robustly validated and protected.
3. Optimizer handles malformed input gracefully, and never panics or leaks information.
4. All logs are structured and traceable, with metrics exposed for API and optimizer.
5. Comprehensive test coverage, including adversarial and edge cases.
6. CI pipeline is green and deploys to test environment on merge to main.

## Make it 1000x better

- Refactor for maintainability, observability, and scalability.
- Improve security posture everywhere.
- Add all missing best practices.
- Document every decision and provide usage instructions.

---
