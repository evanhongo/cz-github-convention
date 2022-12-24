import re
from collections import OrderedDict
from typing import Any, Dict, List
from commitizen import defaults, git, config
from commitizen.cz.base import BaseCommitizen
from commitizen.cz.utils import multiple_line_breaker, required_validator
from commitizen.cz.exceptions import CzException
from commitizen.defaults import MAJOR, MINOR, PATCH

__all__ = ["GithubConventionCz"]


def parse_scope(text):
    if not text:
        return ""

    scope = text.strip().split()
    if len(scope) == 1:
        return scope[0]

    return "-".join(scope)


def parse_subject(text):
    if isinstance(text, str):
        text = text.strip(".").strip()

    return required_validator(text, msg="Subject is required.")


class GithubConventionCz(BaseCommitizen):
    bump_pattern = (
        r"^(BREAKING[\-\ ]CHANGE|🎉? ?feat|🐛? ?fix|🔧? ?refactor|🚀? ?perf)(\(.+\))?(!)?"
    )
    bump_map = OrderedDict(
        (
            (r"^.+!$", MAJOR),
            (r"^BREAKING[\-\ ]CHANGE", MAJOR),
            (r"^🎉? ?feat", MINOR),
            (r"^🐛? ?fix", PATCH),
            (r"^🔧? ?refactor", PATCH),
            (r"^🚀? ?perf", PATCH),
        )
    )
    changelog_pattern = bump_pattern

    # Read the config file and check if required settings are available
    conf = config.read_cfg()

    if "github_repo" not in conf.settings:
        print("Please add the key github_repo to your .cz.yaml|json|toml config file.")
        quit()

    github_repo = conf.settings["github_repo"]
    # if "change_type_map" not in conf.settings:
    change_type_map = {
        "feat": "Feat",
        "fix": "Fix",
        "refactor": "Refactor",
        "perf": "Perf",
    }

    def questions(self) -> List[Dict[str, Any]]:
        questions: List[Dict[str, Any]] = [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the type of change you are committing",
                "choices": [
                    {
                        "value": "🐛 fix",
                        "name": "🐛 fix: A bug fix. Correlates with PATCH in SemVer",
                    },
                    {
                        "value": "🎉 feat",
                        "name": "🎉 feat: A new feature. Correlates with MINOR in SemVer",
                    },
                    {"value": "📜 docs", "name": "📜 docs: Documentation only changes"},
                    {
                        "value": "😎 style",
                        "name": (
                            "😎 style: Changes that do not affect the "
                            "meaning of the code (white-space, formatting,"
                            " missing semi-colons, etc)"
                        ),
                    },
                    {
                        "value": "🔧 refactor",
                        "name": (
                            "🔧 refactor: A code change that neither fixes "
                            "a bug nor adds a feature"
                        ),
                    },
                    {
                        "value": "🚀 perf",
                        "name": "🚀 perf: A code change that improves performance",
                    },
                    {
                        "value": "🚦 test",
                        "name": (
                            "🚦 test: Adding missing or correcting " "existing tests"
                        ),
                    },
                    {
                        "value": "🚧 build",
                        "name": (
                            "🚧 build: Changes that affect the build system or "
                            "external dependencies (example scopes: pip, docker, npm)"
                        ),
                    },
                    {
                        "value": "🛸 ci",
                        "name": (
                            "🛸 ci: Changes to our CI configuration files and "
                            "scripts (example scopes: GitLabCI)"
                        ),
                    },
                ],
            },
            {
                "type": "input",
                "name": "scope",
                "message": (
                    "Scope. Could be anything specifying place of the "
                    "commit change (users, db, poll):\n"
                ),
                "filter": parse_scope,
            },
            {
                "type": "input",
                "name": "subject",
                "filter": parse_subject,
                "message": (
                    "Write a short and imperative summary of the code changes: (lower case and no period)\n"
                ),
            },
            {
                "type": "input",
                "name": "body",
                "message": (
                    "Provide additional contextual information about the code changes: (press [enter] to skip)\n"
                ),
                "filter": multiple_line_breaker,
            },
            {
                "type": "confirm",
                "message": "Is this a BREAKING CHANGE? Correlates with MAJOR in SemVer",
                "name": "is_breaking_change",
                "default": False,
            },
            {
                "type": "input",
                "name": "footer",
                "message": (
                    "Footer. Information about Breaking Changes and "
                    "reference issues that this commit closes: (press [enter] to skip)\n"
                ),
            },
        ]

        return questions

    def message(self, answers: dict) -> str:
        prefix = answers["prefix"]
        scope = answers["scope"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]
        if scope:
            scope = f"({scope})"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE 🚨: {footer}"
        if footer:
            footer = f"\n\n{footer}"
        message = f"{prefix}{scope}: {subject}{body}{footer}"
        return message

    def example(self) -> str:
        return (
            "fix(#12): correct minor typos in code\n"
            "\n"
            "see the issue for details on the typos fixed\n"
            "\n"
            "closes issue #12"
        )

    def schema(self) -> str:
        return (
            "<type>(<scope>): <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE 🚨: )<footer>"
        )

    def schema_pattern(self) -> str:
        PATTERN = (
            r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)"
            r"(\(\S+\))?!?:(\s.*)"
        )
        return PATTERN

    def process_commit(self, commit: str) -> str:
        pat = re.compile(self.schema_pattern())
        m = re.match(pat, commit)
        if m is None:
            return ""
        return m.group(3).strip()

    def changelog_message_builder_hook(
        self, parsed_message: dict, commit: git.GitCommit
    ) -> dict:
        """add github link to the readme"""
        rev = commit.rev
        m = parsed_message["message"]
        parsed_message[
            "message"
        ] = f"{m} [{rev[:5]}](https://github.com/{self.github_repo}/commit/{commit.rev})"
        return parsed_message


class InvalidAnswerError(CzException):
    ...


discover_this = GithubConventionCz
