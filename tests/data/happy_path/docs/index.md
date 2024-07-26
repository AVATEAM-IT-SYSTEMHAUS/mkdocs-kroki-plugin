# Test

## inline

```c4plantuml
!include <C4/C4_Context>
!include <C4/C4_Container>

title System Context diagram for MkDocs Kroki Plugin

Person(writer, "Technical Writer", "Writes documentaion in markdown")
Person(reader, "Audience", "Reads documentaion represented as a web page")

System_Boundary(builder, "Static Site Generation") {
    Container(mkdocs, "MkDocs", "python", "Static Site Generator")
    Container(plugin, "MkDocs Kroki Plugin", "python", "Handles fence block contents")

    ContainerDb(db, "Storage", "gh-pages, S3 or else", "Stores the generated static site")
}

System_Ext(kroki, "kroki.io", "Generates images from fenced contents")
System_Ext(site_host, "Site Host", "Serves the site contents to the audience")

Rel(writer, mkdocs, "use")
BiRel(mkdocs, plugin, "handle diagram blocks")

BiRel(plugin, kroki, "get image data")

Rel(mkdocs, db, "build")
Rel(site_host, db, "read")

Rel(site_host, reader, "serve")
```

## from file

```plantuml
@from_file:assets/diagram.plantuml
```