PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
MAP ?= maps/easy/01_linear_path.txt

.PHONY: install run debug clean lint

install:
	$(PYTHON) -m pip install -r dependencies.txt

run:
	@$(PYTHON) cli.py $(MAP)

debug:
	$(PYTHON) -m pdb cli.py $(MAP)

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache
	rm -f flyin_preview.html mapa_test.html ui/visualizer/animacion_prueba.html

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
