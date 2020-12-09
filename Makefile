.PHONY: requirements
requirements:
	@poetry export --dev -f requirements.txt > requirements.txt
