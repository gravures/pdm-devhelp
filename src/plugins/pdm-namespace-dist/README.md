# Pdm-namespace-dist

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm-project.org)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fgravures%2Fpdm-devhelp%2Fmain%2Fpyproject.toml)
![Tests](https://github.com/gravures/pdm-devhelp/actions/workflows/main.yml/badge.svg)![Endpoint Badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/gravures/pdm-devhelp/python-coverage/endpoint.json&logo=codecov&label=coverage) ![GitHub License](https://img.shields.io/github/license/gravures/pdm-devhelp)

A [PDM](https://https://pdm-project.org/en/latest/) plugin to build sub-packages or modules as standalone distributions (`sdist` and `wheel` packages).

## Getting started

### Installation

This is a `pdm-backend` plugin and it should be appended to the `requires` build table as follow:    

```toml
[build-system]
build-backend = "pdm.backend"
requires = ["pdm-backend", "pdm-namespace-dist"]
```

### Usage

Say you want to publish on `pypi` a package belonging to a larger library, you should declare it in your `pyproject.toml` as a `namespace.package`, it then could be build as a standalone wheel with `pdm build -C namespace=mypackage`.The resulting wheels will be installed as [namespaces packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/).

All configuration items goes under `pdm.tool.namespace` prefix.

```toml
[build-system]
build-backend = "pdm.backend"
requires = ["pdm-backend", "pdm-namespace-dist"]

[project]
name = "cheese-shop"
version = "0.8.2"
...

[tool.pdm.namespace]
override = false  # this is the default

[tool.pdm.namespace.packages.cheddar]
includes = ["src/cheese_shope/cheddar"]
excludes = ["tests"]
project.name = "cheese-shop-cheddar"
project.version = "0.2.1"
project.description = "A tasty cheese."
project.keywords = ["cheese"]

[tool.pdm.namespace.packages.gouda]
includes = ["src/cheese_shope/gouda.py"]
excludes = ["tests"]
name = "cheese-shop-gouda"
...
```

this will build as usual:

```bash
pdm build --no-sdist

>>> dist/dstcheese_chope-0.8.2-py3-none-any.whl
```

to publish only cheddar:

```bash
pdm build --no-sdist -C namespace=cheddar
pdm publish --no-build

>>> dist/cheese_shop_cheddar-0.2.1-py3-none-any.whl
```

> **Note**: override = false (the default), will deeply merge metadata of namespace into project metadata, otherwise a shallow merge will be done.

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://github.com/gravures/pdm-devhelp/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://github.com/gravures/pdm-devhelp/contributing.md) and [Code of Conduct](https://github.com/gravures/pdm-devhelp/code_of_conduct.md).

## Similar Projects

* [pdm-mina](https://github.com/GreyElaina/Mina)
* [using uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/)

## License

Use of this repository is authorized under the [GPL-3.0](https://github.com/gravures/pdm-devhelp/LICENSE).
