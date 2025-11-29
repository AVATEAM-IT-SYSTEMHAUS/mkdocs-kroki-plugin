# mkdocs-kroki-plugin

[![PyPI version](https://badge.fury.io/py/mkdocs-kroki-plugin.svg)](https://badge.fury.io/py/mkdocs-kroki-plugin)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-kroki-plugin)](https://pypi.org/project/mkdocs-kroki-plugin/)
[![Test Status](https://github.com/AVATEAM-IT-SYSTEMHAUS/mkdocs-kroki-plugin/actions/workflows/test.yml/badge.svg)](https://github.com/AVATEAM-IT-SYSTEMHAUS/mkdocs-kroki-plugin/actions/workflows/test.yml)
[![Lint Status](https://github.com/AVATEAM-IT-SYSTEMHAUS/mkdocs-kroki-plugin/actions/workflows/lint.yml/badge.svg)](https://github.com/AVATEAM-IT-SYSTEMHAUS/mkdocs-kroki-plugin/actions/workflows/lint.yml)
[![Python versions](https://img.shields.io/pypi/pyversions/mkdocs-kroki-plugin.svg)](https://pypi.org/project/mkdocs-kroki-plugin/)

This is a MkDocs plugin to embed Kroki-Diagrams into your documentation.

## Setup

Install the plugin using pip:

`pip install mkdocs-kroki-plugin`

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
    ...
      - kroki:
```

## Config

| Key                 | Description                                                                                                                                   | Default                                       |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| `ServerURL`         | URL of your kroki-Server                                                                                                                      | `!ENV [KROKI_SERVER_URL, 'https://kroki.io']` |
| `FencePrefix`       | Diagram prefix, set to an empty string to render all diagrams using Kroki                                                                     | `kroki-`                                      |
| `EnableBlockDiag`   | Enable BlockDiag (and the related Diagrams)                                                                                                   | `true`                                        |
| `EnableBpmn`        | Enable BPMN                                                                                                                                   | `true`                                        |
| `EnableExcalidraw`  | Enable Excalidraw                                                                                                                             | `true`                                        |
| `EnableMermaid`     | Enable Mermaid                                                                                                                                | `true`                                        |
| `EnableDiagramsnet` | Enable diagrams.net (draw.io)                                                                                                                 | `false`                                       |
| `HttpMethod`        | Http method to use (`GET` or `POST`)<br> Note: On `POST` the retrieved images are stored next to the including page in the build directory    | `GET`                                         |
| `RequestTimeout`    | Timeout for HTTP requests in seconds. Increase this value if you encounter timeouts with large diagrams or overloaded kroki server instances. | `30`                                          |
| `UserAgent`         | User agent for requests to the kroki server                                                                                                   | `kroki.plugin/<version>`                      |
| `FileTypes`         | File types you want to use<br>Note: not all file formats work with all diagram types <https://kroki.io/#support>                              | `[svg]`                                       |
| `FileTypeOverrides` | Overrides for specific diagram types to set the desired file type                                                                             | `[]`                                          |
| `TagFormat`         | How the image will be included in the resulting HTML (`img`, `object`, `svg`)                                                                 | `img`                                         |
| `FailFast`          | Errors are raised as plugin errors                                                                                                            | `false`                                       |
| `CacheDir`          | Custom directory for caching rendered diagrams<br>By default uses `$XDG_CACHE_HOME/kroki`, `~/.cache/kroki`, or temp directory                | (automatic)                                   |

Example:

```yaml
  - kroki:
      ServerURL: !ENV [ KROKI_SERVER_URL, 'https://kroki.io' ]
      FileTypes:
        - png
        - svg
      FileTypeOverrides:
        mermaid: png
      FailFast: !ENV CI
```

### Caching

The plugin automatically caches rendered diagrams to improve build performance, especially useful during `mkdocs serve`
when diagrams would otherwise be re-rendered on every file save.

**Note:** Caching only applies when using `HttpMethod: POST`. The GET method generates URLs pointing to the Kroki server
and doesn't download diagram content.

**How it works:**

- Diagrams are cached based on their content, type, format, and options
- Unchanged diagrams are retrieved from cache instead of being re-rendered
- Both in-memory and file-based caching are used for optimal performance
- **LRU strategy**: Frequently accessed diagrams stay in cache, unused ones expire after 3 days
- Cache cleanup runs automatically on plugin initialization with minimal overhead

**Cache location (fallback hierarchy):**

1. `$XDG_CACHE_HOME/kroki` (if XDG_CACHE_HOME is set)
2. `~/.cache/kroki` (if HOME is set)
3. System temp directory + `/kroki` (final fallback)
4. Custom location: Set `CacheDir` in plugin configuration to override

**Example with custom cache directory:**

```yaml
  - kroki:
      CacheDir: .cache/kroki  # Store cache in project directory
```

## Usage

Use code-fences with a tag of kroki-`<Module>` to replace the code with the wanted diagram.

[Diagram options](https://docs.kroki.io/kroki/setup/diagram-options/) can be set as well.

Example for BlockDiag:

````markdown
```kroki-blockdiag no-transparency=false
blockdiag {
  blockdiag -> generates -> "block-diagrams";
  blockdiag -> is -> "very easy!";

  blockdiag [color = "greenyellow"];
  "block-diagrams" [color = "pink"];
  "very easy!" [color = "orange"];
}
```
````

You can render diagram from file with `@from_file:` directive:

````markdown
```kroki-bpmn
@from_file:path/to/diagram.bpmn
```
````

## Contributors

[![Contributors](https://contrib.rocks/image?repo=AVATEAM-IT-SYSTEMHAUS/mkdocs-kroki-plugin)](https://github.com/AVATEAM-IT-SYSTEMHAUS/mkdocs-kroki-plugin/graphs/contributors)

> Want to appear in the list of contributors?
>
> Get started by reading the [Contribution Guidelines](./CONTRIBUTING.md)

## See Also

Diagram examples can be found [here](https://kroki.io/examples.html).

More information about installing a self-manged Kroki-Service [here](https://docs.kroki.io/kroki/setup/install/).

More Plugins for MkDocs can be found [here](http://www.mkdocs.org/user-guide/plugins/)

## Pre-Release-Versions

Install the newest pre-release version using pip:

`pip install -i https://test.pypi.org/simple/ mkdocs-kroki-plugin`

## Development

### Setup

```sh
git clone git@github.com:AVATEAM-IT-SYSTEMHAUS/mkdocs-kroki-plugin.git
cd mkdocs-kroki-plugin
uv sync
```

### Pre-commit Hooks

Install the pre-commit hooks to run linting, type checking, and tests automatically on commit:

```sh
uv run pre-commit install
```

To run all hooks manually:

```sh
uv run pre-commit run --all-files
```

### Testing

Run tests:

```sh
uv run pytest
```

Run tests with coverage:

```sh
uv run pytest --cov
```

### Linting & Formatting

Run ruff for linting and formatting:

```sh
uv run ruff check .
uv run ruff format .
```

### Type Checking

Run mypy:

```sh
uv run --group types mypy kroki
```

### Creating a Release

Use the release script to create a new version:

```sh
./release.py <version>
```

For example:

```sh
./release.py 1.2.3
```

The script will:
1. Validate the version format (semantic versioning: X.Y.Z)
2. Check that the working tree is clean
3. Update the `__version__` in `kroki/__init__.py`
4. Create a commit: `chore: Bump version to X.Y.Z`
5. Create an annotated git tag: `vX.Y.Z`
6. Push the commit and tag to GitHub
7. Open your browser to create a GitHub release where you can add the changelog

**Requirements:**
- Clean working tree (no uncommitted changes)
- Version must follow semantic versioning format (e.g., 1.2.3)
