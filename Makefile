IMAGE_NAME=ipo-pulse-api
DEV_VERSION_FILE=versions/dev_version.txt
DOCKER_VERSION_FILE=versions/docker_version.txt
DOCKER_USER_NAME=amangoyal8110

define dev_read_version
	$(shell if [ -f $(DEV_VERSION_FILE) ]; then cat $(DEV_VERSION_FILE); else echo 0; fi)
endef

define dev_increment_version
	$(shell new_version=$$(($(call dev_read_version)+1)); echo $$new_version > $(DEV_VERSION_FILE); echo $$new_version)
endef

define docker_read_version
	$(shell if [ -f $(DOCKER_VERSION_FILE) ]; then cat $(DOCKER_VERSION_FILE); else echo 0; fi)
endef

define docker_increment_version
	$(shell new_version=$$(($(call docker_read_version)+1)); echo $$new_version > $(DOCKER_VERSION_FILE); echo $$new_version)
endef

docker-build:
	$(eval dev_version=$(call dev_increment_version))
	docker build -t $(IMAGE_NAME):$(dev_version) .

docker-push:
	@docker login
	$(eval dev_version=$(call dev_read_version))
	$(eval docker_version=$(call docker_increment_version))

	@echo "Tagging image..."
	docker tag "$(IMAGE_NAME):$(dev_version)" "$(DOCKER_USER_NAME)/$(IMAGE_NAME):$(docker_version)"
	docker tag "$(IMAGE_NAME):$(dev_version)" "$(DOCKER_USER_NAME)/$(IMAGE_NAME):latest"

	@echo "Pushing images..."
	docker push "$(DOCKER_USER_NAME)/$(IMAGE_NAME):$(docker_version)"
	docker push "$(DOCKER_USER_NAME)/$(IMAGE_NAME):latest"
