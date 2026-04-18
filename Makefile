# Place your local stuff in Makefile.local
-include .env
-include vendors/deps-pipelines/shared/Makefile
-include Makefile.local

APP_NAME = ocr-api-gateway
CURRENT_UID := $(shell id -u):$(shell id -g)
HASH := $(shell git rev-parse HEAD)
DATE := $(shell date)
TAG = $(shell git describe || echo "latest")

NO_DEV_DOCKER_IMAGE = $(APP_NAME)
DEV_DOCKER_IMAGE = ocr-api-gateway-dev

.PHONY: config
## Show current docker compose config
config:
	docker compose -f docker-compose.yml config

.PHONY: config-test
## Show docker compose test config
config-test:
	docker compose -f docker-compose.yml -f docker-compose.test.yml config

.PHONY: install
## Install default environment settings
install:
	cp .env.example .env

.PHONY: login
## Login in docker registry
login:
	docker login $(repository)

.PHONY: prereq
prereq:
	test -f .env || echo >> .env
	docker network create deps-network || true

.PHONY: prereq-tests
prereq-tests: | prereq
	docker compose -f docker-compose.yml -f docker-compose.test.yml down -v

.PHONY: run
## Run service
run: | prereq
	docker compose up -d

.PHONY: logs
## Open service logs
logs:
	docker compose logs -f

.PHONY: status
## Get running status information
status:
	docker compose ps

.PHONY: stop
## Stop runned services
stop:
	docker compose stop

.PHONY: build
## Build containers
build:
	docker compose build \
	--build-arg BUILD_HASH=$(HASH) \
	--build-arg BUILD_TAG=$(TAG) \
	--build-arg BUILD_DATE="$(DATE)"

.PHONY: shell-app
## Open shell in API container
shell-app:
	docker compose exec -u root $(APP_NAME) /bin/sh

.PHONY: format
## Apply black & isort code formatting
format:
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) black --config pyproject.toml .
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) isort --settings-path /app/setup.cfg .

.PHONY: format-check
## Check for correct code format
format-check:
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) black --config pyproject.toml --check .
	docker compose run --rm --no-deps -u "$(CURRENT_UID)" $(APP_NAME) isort --settings-path /app/setup.cfg --check-only .


.PHONY: lint
## Check code using linters
lint:
	docker compose run --rm --no-deps $(APP_NAME) flake8 .

.PHONY: mypy
## Check code using mypy
mypy:
	docker compose run --rm --no-deps $(APP_NAME) mypy .

.PHONY: tests-unit
## Run unit tests
tests-unit:
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --user="root" --rm --no-deps $(APP_NAME) coverage run -a -m pytest -vv -x tests/unit


.PHONY: tests-integration
## Run integration tests
tests-integration:
	docker compose -f docker-compose.yml -f docker-compose.test.yml rm -f
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --user="root" --rm $(APP_NAME) coverage run	-a -m pytest -vv -x tests/integration
	docker compose -f docker-compose.yml -f docker-compose.test.yml rm -f



.PHONY: tests
## Run unit & integration tests
tests:
	docker compose -f docker-compose.yml -f docker-compose.test.yml rm -f
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --user="root" --rm $(APP_NAME) coverage run -a -m pytest -vv -x --junitxml=junit-report.xml tests
	docker compose -f docker-compose.yml -f docker-compose.test.yml rm -f

.PHONY: coverage
## Get code coverage report
coverage:
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm $(APP_NAME) coverage report -i --rcfile=/app/setup.cfg

.PHONY: coverage-xml
## Generate xml coverage report
coverage-xml:
	docker compose -f docker-compose.yml -f docker-compose.test.yml run --rm $(APP_NAME) coverage xml -i --rcfile=/app/setup.cfg -o /app/tests/coverage.xml

.PHONY: ci
## Run CI checks
ci: | prereq-tests format-check lint mypy tests coverage prereq-tests
	@if [ "$(version)" == "ci" ]; then \
		make coverage-xml;\
	else \
	  	make requirements-lock; \
	fi


.PHONY: build-prod
## Build images for production
build-prod:
	$(call build_service,$(DEV_DOCKER_IMAGE),./etc/deps-ocr-api-gateway/Dockerfile,,develop)
	$(call build_service,$(NO_DEV_DOCKER_IMAGE),./etc/deps-ocr-api-gateway/Dockerfile,,,$(DEV_DOCKER_IMAGE))

.PHONY: build-prod-aws-textract
build-prod-aws-textract:
	$(call build_service,$(DEV_DOCKER_IMAGE)-aws-textract,./etc/deps-ocr-api-gateway/engines/aws_textract.Dockerfile,,develop)
	$(call build_service,$(NO_DEV_DOCKER_IMAGE)-aws-textract,./etc/deps-ocr-api-gateway/engines/aws_textract.Dockerfile,,,$(DEV_DOCKER_IMAGE)-aws-textract)

.PHONY: build-prod-azure-form-recognizer
build-prod-azure-form-recognizer:
	$(call build_service,$(DEV_DOCKER_IMAGE)-azure-form-recognizer,./etc/deps-ocr-api-gateway/engines/azure_form_recognizer.Dockerfile,,develop)
	$(call build_service,$(NO_DEV_DOCKER_IMAGE)-azure-form-recognizer,./etc/deps-ocr-api-gateway/engines/azure_form_recognizer.Dockerfile,,,$(DEV_DOCKER_IMAGE)-azure-form-recognizer)

.PHONY: build-prod-gcp-vision
build-prod-gcp-vision:
	$(call build_service,$(DEV_DOCKER_IMAGE)-gcp-vision,./etc/deps-ocr-api-gateway/engines/gcp_vision.Dockerfile,,develop)
	$(call build_service,$(NO_DEV_DOCKER_IMAGE)-gcp-vision,./etc/deps-ocr-api-gateway/engines/gcp_vision.Dockerfile,,,$(DEV_DOCKER_IMAGE)-gcp-vision)

.PHONY: build-prod-tesseract
build-prod-tesseract:
	$(call build_service,$(DEV_DOCKER_IMAGE)-tesseract,./etc/deps-ocr-api-gateway/engines/tesseract.Dockerfile,,develop)
	$(call build_service,$(NO_DEV_DOCKER_IMAGE)-tesseract,./etc/deps-ocr-api-gateway/engines/tesseract.Dockerfile,,,$(DEV_DOCKER_IMAGE)-tesseract)


.PHONY: push
## Push images to registry
push:
	$(call push_service,$(NO_DEV_DOCKER_IMAGE)$(name))
	$(call push_service,$(DEV_DOCKER_IMAGE)$(name))
#	$(call push_service,$(NO_DEV_DOCKER_IMAGE)-aws-textract)
#	$(call push_service,$(DEV_DOCKER_IMAGE)-aws-textract)
#	$(call push_service,$(NO_DEV_DOCKER_IMAGE)-azure-form-recognizer)
#	$(call push_service,$(DEV_DOCKER_IMAGE)-azure-form-recognizer)
#	$(call push_service,$(NO_DEV_DOCKER_IMAGE)-gcp-vision)
#	$(call push_service,$(DEV_DOCKER_IMAGE)-gcp-vision)
#	$(call push_service,$(NO_DEV_DOCKER_IMAGE)-tesseract)
#	$(call push_service,$(DEV_DOCKER_IMAGE)-tesseract)


.PHONY: deliver
## Build prod images and push to registry
deliver: | build-prod push

.PHONY: tag
## Retag built services
tag:
	$(call tag_service,$(NO_DEV_DOCKER_IMAGE)$(name))
	$(call tag_service,$(DEV_DOCKER_IMAGE)$(name))
#	$(call tag_service,$(NO_DEV_DOCKER_IMAGE)-aws-textract)
#	$(call tag_service,$(DEV_DOCKER_IMAGE)-aws-textract)
#	$(call tag_service,$(NO_DEV_DOCKER_IMAGE)-azure-form-recognizer)
#	$(call tag_service,$(DEV_DOCKER_IMAGE)-azure-form-recognizer)
#	$(call tag_service,$(NO_DEV_DOCKER_IMAGE)-gcp-vision)
#	$(call tag_service,$(DEV_DOCKER_IMAGE)-gcp-vision)
#	$(call tag_service,$(NO_DEV_DOCKER_IMAGE)-tesseract)
#	$(call tag_service,$(DEV_DOCKER_IMAGE)-tesseract)

.PHONY: pull
## Pull service images from docker registry
pull:
	$(call pull_service,$(NO_DEV_DOCKER_IMAGE)$(name))
	$(call pull_service,$(DEV_DOCKER_IMAGE)$(name))
#	$(call pull_service,$(NO_DEV_DOCKER_IMAGE)-aws-textract)
#	$(call pull_service,$(DEV_DOCKER_IMAGE)-aws-textract)
#	$(call pull_service,$(NO_DEV_DOCKER_IMAGE)-azure-form-recognizer)
#	$(call pull_service,$(DEV_DOCKER_IMAGE)-azure-form-recognizer)
#	$(call pull_service,$(NO_DEV_DOCKER_IMAGE)-gcp-vision)
#	$(call pull_service,$(DEV_DOCKER_IMAGE)-gcp-vision)
#	$(call pull_service,$(NO_DEV_DOCKER_IMAGE)-tesseract)
#	$(call pull_service,$(DEV_DOCKER_IMAGE)-tesseract)

.PHONY: push-diff
## Push images to registry
push-diff:
	$(call push_service,$(NO_DEV_DOCKER_IMAGE)$(name))
	$(call push_service,$(DEV_DOCKER_IMAGE)$(name))

.PHONY: tag-diff
## Retag built services
tag-diff:
	$(call tag_service,$(NO_DEV_DOCKER_IMAGE)$(name))
	$(call tag_service,$(DEV_DOCKER_IMAGE)$(name))

.PHONY: pull-diff
## Pull service images from docker registry
pull-diff:
	$(call pull_service,$(NO_DEV_DOCKER_IMAGE)$(name))
	$(call pull_service,$(DEV_DOCKER_IMAGE)$(name))

.PHONY: helm-upgrade-service
helm-upgrade-service:
	helm upgrade --install $(CI_PROJECT_NAME) .helm/services \
		--values .helm/services/values.yaml $(ADDITIONAL_VALUES) \
		--set registry=$(REPOSITORY_URL) \
		--set ocr_api_gateway.image.tag=$(CI_COMMIT_SHORT_SHA) \
		--set ocr_api_gateway_consumer.image.tag=$(CI_COMMIT_SHORT_SHA) \
		--set ocr_api_gateway_aws_textract.image.tag=$(CI_COMMIT_SHORT_SHA) \
		--set ocr_api_gateway_azure_form_recognizer.image.tag=$(CI_COMMIT_SHORT_SHA) \
		--set ocr_api_gateway_gcp_vision.image.tag=$(CI_COMMIT_SHORT_SHA) \
		--set ocr_api_gateway_tesseract.image.tag=$(CI_COMMIT_SHORT_SHA) \
		--set vault_settings.enabled=$(VAULT_ENABLE) \
		--timeout 900s \
		--atomic \
		--wait \
		--debug \
		--namespace $(NAMESPACE)

.PHONY: helm-upgrade
helm-upgrade:
	make helm-upgrade-service

.PHONY: helm-deployment-rollback
helm-deployment-rollback:
	helm rollback --namespace $(NAMESPACE) $(CI_PROJECT_NAME) 0

.PHONY: helm-rollback
helm-rollback:
	make helm-deployment-rollback

testdkube := $(shell kubectl config current-context)
ifeq ($(testdkube), rancher-desktop)
.PHONY: skaffold
skaffold:
	cd skaffold && skaffold run -f skaffold.yaml
endif

.PHONY: build-no-dev
build-no-dev:
	$(call build_service,$(NO_DEV_DOCKER_IMAGE),./etc/deps-ocr-api-gateway/Dockerfile,,build,$(DEV_DOCKER_IMAGE))
	# $(call build_service,$(NO_DEV_DOCKER_IMAGE)-aws-textract,./etc/deps-ocr-api-gateway/engines/aws_textract.Dockerfile,,build,$(DEV_DOCKER_IMAGE)-aws-textract)
	# $(call build_service,$(NO_DEV_DOCKER_IMAGE)-azure-form-recognizer,./etc/deps-ocr-api-gateway/engines/azure_form_recognizer.Dockerfile,,build,$(DEV_DOCKER_IMAGE)-azure-form-recognizer)
	# $(call build_service,$(NO_DEV_DOCKER_IMAGE)-gcp-vision,./etc/deps-ocr-api-gateway/engines/gcp_vision.Dockerfile,,build,$(DEV_DOCKER_IMAGE)-gcp-vision)
	# $(call build_service,$(NO_DEV_DOCKER_IMAGE)-tesseract,./etc/deps-ocr-api-gateway/engines/tesseract.Dockerfile,,build,$(DEV_DOCKER_IMAGE)-tesseract)

