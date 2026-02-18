.PHONY: up test

up:
	mkdir -p _inputs _outputs _audit _tmp
	docker compose -f infra/docker-compose.yml up --build --abort-on-container-exit

test:
	mkdir -p _inputs _outputs _audit _tmp
	docker compose -f infra/docker-compose.yml run --rm --entrypoint pytest pack-factory -q
