name: 🐛 Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: saitejabandaru-in
body:
  - type: markdown
    attributes:
      value: Thank you for taking the time to report a bug!
  - type: textarea
    id: describe
    attributes:
      label: Describe the bug
      placeholder: A clear and concise description of what the bug is. E.g. something crashed.
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: Steps to reproduce
      placeholder: |
        1. Go to '...'
        2. Click on '....'
        3. See error
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
      placeholder: A clear and concise description of what you expected to happen.
    validations:
      required: true
