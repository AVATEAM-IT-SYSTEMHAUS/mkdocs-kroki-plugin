import pytest

from tests.utils import MkDocsTemplateHelper

TEST_CASES = {
    "#35": """
```` plantuml
    stuff containing ```
````
""",
    "https://spec.commonmark.org/0.31.2/#example-119": """
``` mermaid
<
 >
```
""",
    "https://spec.commonmark.org/0.31.2/#example-120": """
~~~ mermaid
<
 >
~~~
""",
    "https://spec.commonmark.org/0.31.2/#example-122": """
``` mermaid
aaa
~~~
```
""",
    "https://spec.commonmark.org/0.31.2/#example-123": """
~~~ mermaid
aaa
```
~~~
""",
    "https://spec.commonmark.org/0.31.2/#example-125": """
~~~~ mermaid
aaa
~~~
~~~~
""",
    "https://spec.commonmark.org/0.31.2/#example-129": """
``` mermaid


```
""",
    "https://spec.commonmark.org/0.31.2/#example-130": """
``` mermaid
```
""",
}

TEST_CASES_NOT_SUPPORTED = {
    "https://spec.commonmark.org/0.31.2/#example-121": """
`` mermaid
foo
``
""",
    "https://spec.commonmark.org/0.31.2/#example-124": """
```` mermaid
aaa
```
``````
""",
    "https://spec.commonmark.org/0.31.2/#example-126": """
``` mermaid
""",
    "https://spec.commonmark.org/0.31.2/#example-127": """
````` mermaid

```
aaa
""",
    "https://spec.commonmark.org/0.31.2/#example-128": """
> ``` mermaid
> aaa

bbb
""",
    "https://spec.commonmark.org/0.31.2/#example-131": """
 ``` mermaid
 aaa
aaa
```
""",
    "https://spec.commonmark.org/0.31.2/#example-132": """
  ```
aaa
  aaa
aaa
  ```
""",
    "https://spec.commonmark.org/0.31.2/#example-133": """
   ```
   aaa
    aaa
  aaa
   ```
""",
    "https://spec.commonmark.org/0.31.2/#example-135": """
```
aaa
  ```
""",
    "https://spec.commonmark.org/0.31.2/#example-136": """
   ```
aaa
  ```
""",
    "https://spec.commonmark.org/0.31.2/#example-140": """
foo
```
bar
```
baz
""",
    "https://spec.commonmark.org/0.31.2/#example-141": """
foo
---
~~~
bar
~~~
# baz
""",
    "https://spec.commonmark.org/0.31.2/#example-146": """
~~~ aa ``` ~~~
foo
~~~
""",
    "https://spec.commonmark.org/0.31.2/#example-147": """
```
``` aaa
```
""",
}

TEST_CASES_ESCAPED = {
    "https://spec.commonmark.org/0.31.2/#example-134": """
    ```
    aaa
    ```
""",
}


@pytest.mark.parametrize("test_code_block", [pytest.param(v, id=k) for k, v in TEST_CASES.items()])
@pytest.mark.usefixtures("kroki_dummy")
def test_fences(test_code_block) -> None:
    with MkDocsTemplateHelper(test_code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0, f"exit code {result.exit_code}, expected 0"
        image_files = list((mkdocs_helper.test_dir / "site").glob("*.svg"))
        assert len(image_files) == 1, f"created images {len(image_files)}, expected 1"


@pytest.mark.parametrize(
    "test_code_block",
    [pytest.param(v, id=k) for k, v in TEST_CASES_NOT_SUPPORTED.items()]
    + [pytest.param(v, id=k) for k, v in TEST_CASES_ESCAPED.items()],
)
@pytest.mark.usefixtures("kroki_dummy")
def test_fences_not_supported(test_code_block) -> None:
    with MkDocsTemplateHelper(test_code_block) as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0, f"exit code {result.exit_code}, expected 0"
        image_files = list((mkdocs_helper.test_dir / "site").glob("*.svg"))
        assert len(image_files) == 0, f"created images {len(image_files)}, expected 0"


@pytest.mark.usefixtures("kroki_dummy")
def test_pandoc_fenced_code_blocks() -> None:
    with MkDocsTemplateHelper("""~~~~~~~~~~~~~~~~
~~~~~~~~~~ mermaid
code including tildes
~~~~~~~~~~
~~~~~~~~~~~~~~~~""") as mkdocs_helper:
        mkdocs_helper.set_http_method("POST")
        result = mkdocs_helper.invoke_build()

        assert result.exit_code == 0, f"exit code {result.exit_code}, expected 0"
        image_files = list((mkdocs_helper.test_dir / "site").glob("*.svg"))
        assert len(image_files) == 0, f"created images {len(image_files)}, expected 0"
