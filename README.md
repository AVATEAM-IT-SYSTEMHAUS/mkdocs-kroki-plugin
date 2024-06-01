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

| Key | Description |
|---|---|
| `ServerURL` | URL of your kroki-Server, default: `!ENV [KROKI_SERVER_URL, 'https://kroki.io']` |
| `FencePrefix` | Diagram prefix, default: `kroki-` |
| `EnableBlockDiag` | Enable BlockDiag (and the related Diagrams), default: `true` |
| `EnableBpmn` | Enable BPMN, default: `true` |
| `EnableExcalidraw` | Enable Excalidraw, default: `true` |
| `EnableMermaid` | Enable Mermaid, default: `true` |
| `EnableDiagramsnet` | Enable diagrams.net (draw.io), default: `false` |
| `HttpMethod` | Http method to use (`GET` or `POST`), default: `GET`<br>__Note:__ On `POST` the retrieved images are stored next to the including page in the build directory |
| `UserAgent` | User agent for requests to the kroki server, default: `kroki.plugin/0.7.1`  |
| `FileTypes` | File types you want to use, default: `[svg]`<br>__Note:__ not all file formats work with all diagram types <https://kroki.io/#support>  |
| `FileTypeOverrides` | Overrides for specific diagram types to set the desired file type, default: empty |
| `FailFast` | Errors are raised as plugin errors, default: `false` |

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
