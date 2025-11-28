---
name: 🐛 Bug Report
about: File a bug report
labels:
  - bug
assignees:
  - timo-reymann
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!
  - type: dropdown
    id: os
    attributes:
      label: OS
      description: What OS are you using?
      options:
        - Linux
        - Darwin
        - Windows
    validations:
      required: true
  - type: input
    id: plugin-version
    attributes:
      label: Installed version of the mkdocs-kroki plugin
    validations:
      required: true
  - type: input
    id: mkdocs-version
    attributes:
      label: Installed version of mkdocs
    validations:
      required: true
  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: Also tell us, what did you expect to happen?
      placeholder: Tell us what you see!
    validations:
      required: true
  - type: textarea
    id: problem
    attributes:
      label: Problem description
      description: Please provide some details about the error, e.g. what you have
        done before it occured
    validations:
      required: true
  - type: textarea
    id: expected-behaviour
    attributes:
      label: Expected behaviour
      description: What should have happened?
    validations:
      required: true
  - type: textarea
    id: actual-behaviour
    attributes:
      label: Actual  behaviour
      description: What actually happened?
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: Steps to Reproduce
      description: Please list the steps required to reproduce the issue.
    validations:
      required: true
  - type: textarea
    id: more-info
    attributes:
      label: Important Factoids
      description: Is there anything atypical special about your setup or example?
  - type: textarea
    id: references
    attributes:
      label: References
      description: |
        Are there any other GitHub issues (open or closed) or pull requests
        that should be linked here? Vendor documentation?
      placeholder: "You can reference issues with #"
  - type: checkboxes
    id: terms
    attributes:
      label: I read and agree to the contribution guidelines
      description: |
        By submitting this issue, you read and agree to the contribution guidelines.
      options:
        - label: I read and agree to the contribution guidelines
          required: true
---