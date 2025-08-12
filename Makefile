# 常用开发命令（需要 poetry 环境）

.PHONY: install test lint examples docs

install:
	poetry install

lint:
	poetry run python -c "import wp_python; print('import ok, version=', wp_python.__version__)"

test:
	poetry run python -m pytest -q

examples:
	@echo "运行示例：poetry run python examples/quick_start.py --dev"
	@echo "认证示例：poetry run python examples/auth_methods.py --method app_password"
	@echo "FastAPI：poetry run python examples/fastapi_plugin_example.py --start"
