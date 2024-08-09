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

Configuration can either be done through the `mkdocs.yaml` file or through environment variables.

For example, the `ServerURL` follows this priority:
1. **Config from mkdocs file**: If specified in the `mkdocs.yaml` file, it takes the highest priority.
2. **Environment Variable**: If not specified in the `mkdocs.yaml` file, it falls back to the `KROKI_SERVER_URL` environment variable.
3. **Default**: If neither is provided, it defaults to `https://kroki.io`.

Other configurations follow a similar priority order.

| Key | Description | Environment Variable | Default |
|---|---|---|---|
| `ServerURL` | URL of your kroki-Server | `KROKI_SERVER_URL` | `https://kroki.io` |
| `FencePrefix` | Diagram prefix | `KROKI_FENCE_PREFIX` | `kroki-` |
| `EnableBlockDiag` | Enable BlockDiag (and the related Diagrams) | `KROKI_ENABLE_BLOCKDIAG` | `true` |
| `EnableBpmn` | Enable BPMN | `KROKI_ENABLE_BPMN` | `true` |
| `EnableExcalidraw` | Enable Excalidraw | `KROKI_ENABLE_EXCALIDRAW` | `true` |
| `EnableMermaid` | Enable Mermaid | `KROKI_ENABLE_MERMAID` | `true` |
| `EnableDiagramsnet` | Enable diagrams.net (draw.io) | `KROKI_ENABLE_DIAGRAMSNET` | `false` |
| `HttpMethod` | HTTP method to use (`GET` or `POST`)<br>__Note:__ On `POST` the retrieved images are stored next to the including page in the build directory | `KROKI_HTTP_METHOD` | `GET` |
| `UserAgent` | User agent for requests to the kroki server | `KROKI_USER_AGENT` | `kroki.plugin/<version>` |
| `FileTypes` | File types you want to use<br>__Note:__ not all file formats work with all diagram types <https://kroki.io/#support> | `KROKI_FILE_TYPES` | `[svg]` |
| `FileTypeOverrides` | Overrides for specific diagram types to set the desired file type | `KROKI_FILE_TYPE_OVERRIDES` | empty |
| `TagFormat` | How the image will be included in the resulting HTML<br>(`img`, `object`, `svg`) | `KROKI_TAG_FORMAT` | `img` |
| `FailFast` | Errors are raised as plugin errors | `KROKI_FAIL_FAST` | `false` |

For boolean environment variables, the values `"true"`, `"1"`, and `"t"` (case-insensitive) are considered `true`.

Example:
```yaml
  - kroki:
      ServerURL: !ENV [KROKI_SERVER_URL, 'https://kroki.io']
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

Setup:

```sh
git clone git@github.com:AVATEAM-IT-SYSTEMHAUS/mkdocs-kroki-plugin.git
cd mkdocs-kroki-plugin
pipx install hatch
pipx install pre-commit
pre-commit install
```

Run tests (for all supported python versions):

```sh
hatch test -a
```

Run static code analysis:

```sh
hatch fmt
```
