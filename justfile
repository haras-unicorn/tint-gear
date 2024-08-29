set windows-shell := ["nu.exe", "-c"]
set shell := ["nu", "-c"]

root_path := justfile_directory()

format:
  yapf --recursive --in-place --parallel "{{root_path}}"
  prettier --write "{{root_path}}"

lint:
  ruff check "{{root_path}}"

test:
  pytest -n auto "{{root_path}}"

run *args:
  cd "{{root_path}}"; python -m tint_gear.main {{args}}
