from dataclasses import dataclass, field
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture
from result import Ok

from kroki.common import KrokiImageContext
from kroki.parsing import KrokiDiagramTypes, MarkdownParser


@dataclass
class StubInput:
    page_data: str
    expected_code_block_data: str = ""
    epxected_options: dict = field(default_factory=dict)
    expected_plugin_options: dict = field(default_factory=dict)
    expected_kroki_type: str = ""


TEST_CASES = {
    "#35": StubInput(
        page_data="""
```` plantuml
    stuff containing ```

````
""",
        expected_code_block_data="stuff containing ```\n\n",
        expected_kroki_type="plantuml",
    ),
    "https://pandoc.org/MANUAL.html#fenced-code-blocks": StubInput(
        page_data="""~~~~~~~~~~~~~~~~ mermaid
~~~~~~~~~~
code including tildes
~~~~~~~~~~
~~~~~~~~~~~~~~~~""",
        expected_code_block_data="~~~~~~~~~~\ncode including tildes\n~~~~~~~~~~\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-119": StubInput(
        page_data="""
``` mermaid
<
 >
```
""",
        expected_code_block_data="<\n >\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-120": StubInput(
        page_data="""
~~~ mermaid
<
 >
~~~
""",
        expected_code_block_data="<\n >\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-122": StubInput(
        page_data="""
``` mermaid
aaa
~~~
```
""",
        expected_code_block_data="aaa\n~~~\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-123": StubInput(
        page_data="""
~~~ mermaid
aaa
```
~~~
""",
        expected_code_block_data="aaa\n```\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-125": StubInput(
        page_data="""
~~~~ mermaid
aaa
~~~
~~~~
""",
        expected_code_block_data="aaa\n~~~\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-129": StubInput(
        page_data="""
``` mermaid


```
""",
        expected_code_block_data="\n\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-130": StubInput(
        page_data="""
``` mermaid
```
""",
        expected_code_block_data="",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-147": StubInput(
        page_data="""
``` mermaid
``` aaa
```
""",
        expected_code_block_data="``` aaa\n",
        expected_kroki_type="mermaid",
    ),
    "#85": StubInput(
        page_data="""
```plantuml {kroki=true}
   Alice -> Bob
```
""",
        expected_code_block_data="Alice -> Bob\n",
        epxected_options={},
        expected_kroki_type="plantuml",
    ),
}

TEST_CASES_NOT_COMPLYING = {
    "https://spec.commonmark.org/0.31.2/#example-132": StubInput(
        page_data="""
  ``` mermaid
aaa
  aaa
aaa
  ```
""",
        expected_code_block_data="aaa\n  aaa\naaa\n",  # "aaa\naaa\naaa\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-133": StubInput(
        page_data="""
   ``` mermaid
   aaa
    aaa
  aaa
   ```
""",
        expected_code_block_data=" aaa\n  aaa\naaa\n",  # "aaa\n aaa\naaa\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-134": StubInput(
        page_data="""
    ``` mermaid
    aaa
    ```
""",
        expected_code_block_data="aaa\n",  # should not be replaced..
        expected_kroki_type="mermaid",
    ),
}

TEST_CASES_NOT_SUPPORTED = {
    "https://spec.commonmark.org/0.31.2/#example-121": StubInput(
        page_data="""
`` mermaid
foo
``
""",
        expected_code_block_data="foo\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-124": StubInput(
        page_data="""
```` mermaid
aaa
```
``````
""",
        expected_code_block_data="aaa\n```\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-126": StubInput(
        page_data="""
``` mermaid
""",
        expected_code_block_data="\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-127": StubInput(
        page_data="""
````` mermaid

```
aaa
""",
        expected_code_block_data="\n```\naaa\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-128": StubInput(
        page_data="""
> ``` mermaid
> aaa

bbb
""",
        expected_code_block_data="aaa\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-131": StubInput(
        page_data="""
 ``` mermaid
 aaa
aaa
```
""",
        expected_code_block_data="aaa\naaa\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-135": StubInput(
        page_data="""
```
aaa
  ```
""",
        expected_code_block_data="aaa\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-136": StubInput(
        page_data="""
   ```
aaa
  ```
""",
        expected_code_block_data="aaa\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-140": StubInput(
        page_data="""
foo
```
bar
```
baz
""",
        expected_code_block_data="bar\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-141": StubInput(
        page_data="""
foo
---
~~~
bar
~~~
# baz
""",
        expected_code_block_data="bar\n",
        expected_kroki_type="mermaid",
    ),
    "https://spec.commonmark.org/0.31.2/#example-146": StubInput(
        page_data="""
~~~ mermaid ``` ~~~
foo
~~~
""",
        expected_code_block_data="foo\n",
        expected_kroki_type="mermaid",
    ),
}


@pytest.mark.parametrize(
    "test_data",
    [pytest.param(v, id=k) for k, v in TEST_CASES.items()]
    + [pytest.param(v, id=k) for k, v in TEST_CASES_NOT_COMPLYING.items()],
)
def test_fences(
    test_data: StubInput,
    mock_kroki_diagram_types: KrokiDiagramTypes,
    mocker: MockerFixture,
) -> None:
    # Arrange
    parser = MarkdownParser("", mock_kroki_diagram_types)
    callback_stub = AsyncMock(return_value="")
    context_stub = mocker.stub()
    # Act
    parser.replace_kroki_blocks(test_data.page_data, callback_stub, context_stub)
    # Assert
    callback_stub.assert_called_once_with(
        KrokiImageContext(
            kroki_type=test_data.expected_kroki_type,
            options=test_data.epxected_options,
            plugin_options=test_data.expected_plugin_options,
            data=Ok(test_data.expected_code_block_data),
        ),
        context_stub,
    )


@pytest.mark.parametrize(
    "test_data", [pytest.param(v, id=k) for k, v in TEST_CASES_NOT_SUPPORTED.items()]
)
def test_fences_not_supported(
    test_data: StubInput,
    mock_kroki_diagram_types: KrokiDiagramTypes,
    mocker: MockerFixture,
) -> None:
    # Arrange
    parser = MarkdownParser("", mock_kroki_diagram_types)
    callback_stub = AsyncMock(return_value="")
    context_stub = mocker.stub()
    # Act
    parser.replace_kroki_blocks(test_data.page_data, callback_stub, context_stub)
    # Assert
    callback_stub.assert_not_called()
