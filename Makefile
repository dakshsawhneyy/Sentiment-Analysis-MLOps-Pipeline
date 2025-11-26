run-pipeline:
	docker compose run --rm ingestor 
	docker compose run --rm processor
	docker compose run --rm trainer
	docker compose run --rm validator