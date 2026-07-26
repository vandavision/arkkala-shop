.PHONY: help dev-up dev-down dev-logs dev-shell dev-migrate dev-build \
        prod-up prod-down prod-logs prod-shell prod-migrate prod-build \
        deploy dev-backup dev-restore backup restore ps clean

COMPOSE_DEV := docker-compose -f development.yml --env-file .env.dev
COMPOSE_PROD := docker-compose -f production.yml --env-file .env.prod

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev-up: ## Start dev stack
	$(COMPOSE_DEV) up -d --build

dev-down: ## Stop dev stack
	$(COMPOSE_DEV) down

dev-down-v: ## Stop dev stack -v
	$(COMPOSE_DEV) down -v

dev-logs: ## Tail dev logs
	$(COMPOSE_DEV) logs -f --tail=200

dev-shell: ## Django shell inside dev container
	$(COMPOSE_DEV) exec django python manage.py shell

dev-migrate: ## Run migrations in dev
	$(COMPOSE_DEV) exec django python manage.py makemigrations
	$(COMPOSE_DEV) exec django python manage.py migrate

dev-build: ## Rebuild dev images
	$(COMPOSE_DEV) build --no-cache

prod-up: ## Start prod stack
	$(COMPOSE_PROD) up -d --build

prod-down: ## Stop prod stack
	$(COMPOSE_PROD) down

prod-logs: ## Tail prod logs
	$(COMPOSE_PROD) logs -f --tail=200

prod-shell: ## Django shell inside prod container
	$(COMPOSE_PROD) exec django python manage.py shell

prod-migrate: ## Run migrate only
	$(COMPOSE_PROD) exec django python manage.py migrate

prod-build: ## Rebuild prod images
	$(COMPOSE_PROD) build --no-cache

deploy: ## Deploy using deploy.sh script
	./deploy.sh

dev-backup: ## Backup the development database
	$(COMPOSE_DEV) exec -T postgres sh -c 'pg_dump -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -F c -f /var/lib/postgresql/data/backup_$$(date +%Y%m%d_%H%M%S).dump'

dev-restore: ## Restore the development database
	$(COMPOSE_DEV) exec -T postgres sh -c 'pg_restore -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -1 -c /var/lib/postgresql/data/$(FILE)'

backup: ## Backup the production database
	$(COMPOSE_PROD) exec -T postgres sh -c 'pg_dump -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -F c -f /backups/backup_$$(date +%Y%m%d_%H%M%S).dump'

restore: ## Restore the production database
	$(COMPOSE_PROD) exec -T postgres sh -c 'pg_restore -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -1 -c /backups/$(FILE)'

ps: ## Show running prod containers
	$(COMPOSE_PROD) ps

clean: ## Remove dangling images and build cache
	docker image prune -f
	docker builder prune -f