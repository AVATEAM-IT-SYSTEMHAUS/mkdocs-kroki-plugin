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

* `ServerURL` - URL of your kroki-Server, default: <https://kroki.io>
* `EnableBlockDiag` - Enable BlockDiag (and the related Diagrams), default: True
* `Enablebpmn` - Enable BPMN, default: True
* `EnableExcalidraw` - Enable Excalidraw, default: True
* `EnableMermaid` - Enable Mermaid, default: True
* `DownloadImages` - Download diagrams from kroki as static assets instead of just creating kroki links, default: False
* `DownloadDir` - The asset directory to place downloaded svg images in, default: images/kroki_generated

## Usage

Use code-fences with a tag of kroki-`<Module>` to replace the code with the wanted diagram.

Example for BlockDiag:

````markdown
```kroki-blockdiag
blockdiag {
  blockdiag -> generates -> "block-diagrams";
  blockdiag -> is -> "very easy!";

  blockdiag [color = "greenyellow"];
  "block-diagrams" [color = "pink"];
  "very easy!" [color = "orange"];
}
```
````

## See Also

Diagram examples can be found [here](https://kroki.io/examples.html).

More information about installing a self-manged Kroki-Service [here](https://docs.kroki.io/kroki/setup/install/).

More Plugins for MkDocs can be found [here](http://www.mkdocs.org/user-guide/plugins/)

## Pre-Release-Versions

Install the newest pre-release version using pip:

`pip install -i https://test.pypi.org/simple/ mkdocs-kroki-plugin`
