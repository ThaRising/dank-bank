.PHONY: requirements
requirements:
	@poetry export --dev --without-hashes -f requirements.txt > requirements.txt
