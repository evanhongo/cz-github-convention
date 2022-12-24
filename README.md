# What is it
## **cz-github-convention** is a plugin for [commitizen](https://github.com/commitizen-tools/commitizen)

---

# What it do

- ## Create links to GitHub commits in the CHANGELOG.md

---

# Installation

```sh
pip install cz-github-convention
cz init
```

## cz.json
```json
{
  "commitizen": {
    "name": "cz_github_convention",
    "version": "0.0.1",
    "tag_format": "v$version",
    "github_repo": "superman/super-project"
  }
}
```

## .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v2.38.0
    hooks:
      - id: commitizen
        stages: [commit-msg]
        additional_dependencies: [cz-github-convention]
```