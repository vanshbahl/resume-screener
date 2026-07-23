# 25. Communication & Notification Hub

## Overview
The Communication & Notification Hub is a centralized platform for managing all communications across the Recruitment Intelligence Platform. Instead of domains sending emails, SMS, or webhooks directly, domains publish communication events which the Hub processes.

## Architecture
The platform is organized into the following layers:
- **Models & Schemas**: Centralized entities (`CommunicationNotification`, `NotificationTemplate`, `CommunicationPreference`, etc.) designed for multi-tenancy.
- **Providers**: Strategy pattern used for Email, SMS, Push, and Webhooks. A mock provider handles local environments.
- **Queue Processor**: Background workers to batch process notifications.
- **Templates**: Jinja2-backed template engine for text and HTML bodies.

## Event Flow
1. A domain publishes an event via `CommunicationService.publish_event()`.
2. The event is persisted as a `CommunicationNotification` and added to the `NotificationQueue`.
3. The background `QueueProcessor` picks up the pending items in batches.
4. It resolves the recipient's `CommunicationPreference` to check if the channel is enabled.
5. If enabled, the `TemplateService` renders the content using Jinja2.
6. The appropriate `Provider` attempts delivery, creating a `DeliveryAttempt` with the status.

## Fixes & Updates (RC2)
- Fixed SQLAlchemy collision by renaming `Notification` to `CommunicationNotification` to avoid conflicting with the `WorkspaceNotification` model.
- Integrated test coverage for queue processing, template rendering, and preference override logic using `testcontainers`.
- Updated test dependency injection for `QueueProcessor` to support isolated `Session` contexts.
