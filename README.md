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
* `FencePrefix` - Diagram prefix, default: `kroki-`
* `EnableBlockDiag` - Enable BlockDiag (and the related Diagrams), default: True
* `Enablebpmn` - Enable BPMN, default: True
* `EnableExcalidraw` - Enable Excalidraw, default: True
* `EnableMermaid` - Enable Mermaid, default: True
* `EnableDiagramsnet` - Enable diagrams.net (draw.io), default: False
* `HttpMethod` - Http method to use (`GET` or `POST`), default: `GET` (Note: you have to enable `DownloadImages` if you want to use `POST`!)
* `DownloadImages` - Download diagrams from kroki as static assets instead of just creating kroki links, default: False
* `DownloadDir` - The asset directory to place downloaded images in, default: images/kroki_generated
* `FileTypes` - File types you want to use, default: [svg], (Note: not all file formats works with all diagram types <https://kroki.io/#support>)

```yaml
  - kroki:
      FileTypes:
        - png
        - svg
```

* `FileTypeOverrides` - Overrides for specific diagrams to set the desired file type default: None,

```yaml
  - kroki:
      FileTypeOverrides:
        mermaid: png
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

## See Also

Diagram examples can be found [here](https://kroki.io/examples.html).

More information about installing a self-manged Kroki-Service [here](https://docs.kroki.io/kroki/setup/install/).

More Plugins for MkDocs can be found [here](http://www.mkdocs.org/user-guide/plugins/)

## Pre-Release-Versions

Install the newest pre-release version using pip:

`pip install -i https://test.pypi.org/simple/ mkdocs-kroki-plugin`
