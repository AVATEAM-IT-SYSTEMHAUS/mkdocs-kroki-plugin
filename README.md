# mkdocs-kroki-plugin

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

| Key                 | Description                                                                                                                                | Default                                       |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| `ServerURL`         | URL of your kroki-Server                                                                                                                   | `!ENV [KROKI_SERVER_URL, 'https://kroki.io']` |
| `FencePrefix`       | Diagram prefix, set to an empty string to render all diagrams using Kroki                                                                  | `kroki-`                                      |
| `EnableBlockDiag`   | Enable BlockDiag (and the related Diagrams)                                                                                                | `true`                                        |
| `EnableBpmn`        | Enable BPMN                                                                                                                                | `true`                                        |
| `EnableExcalidraw`  | Enable Excalidraw                                                                                                                          | `true`                                        |
| `EnableMermaid`     | Enable Mermaid                                                                                                                             | `true`                                        |
| `EnableDiagramsnet` | Enable diagrams.net (draw.io)                                                                                                              | `false`                                       |
| `HttpMethod`        | Http method to use (`GET` or `POST`)<br> Note: On `POST` the retrieved images are stored next to the including page in the build directory | `GET`                                         |
| `UserAgent`         | User agent for requests to the kroki server                                                                                                | `kroki.plugin/<version>`                      |
| `FileTypes`         | File types you want to use<br>Note: not all file formats work with all diagram types <https://kroki.io/#support>                           | `[svg]`                                       |
| `FileTypeOverrides` | Overrides for specific diagram types to set the desired file type                                                                          | `[]`                                          |
| `TagFormat`         | How the image will be included in the resulting HTML (`img`, `object`, `svg`)                                                              | `img`                                         |
| `FailFast`          | Errors are raised as plugin errors                                                                                                         | `false`                                       |

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
