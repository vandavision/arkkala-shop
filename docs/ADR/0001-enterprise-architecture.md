# ADR 0001: Enterprise Architecture Transition

## Status
Accepted

## Context
The previous architecture tightly coupled business logic to the Django ORM and framework. This hindered scalability, team collaboration, and testability.

## Decision
We are adopting a DDD-aligned approach using CQRS and the Repository Pattern:
1. **Domain Layer**: Django Models (acting purely as entities).
2. **Repository Layer**: Abstracts database access.
3. **Application Layer (CQRS)**: Divided into `commands/` (writes) and `queries/` (reads).
4. **Event Layer**: Domain events published to an Event Broker.
5. **Presentation Layer**: DRF Views with OpenAPI (Swagger) specifications.