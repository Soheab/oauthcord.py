from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from urllib.parse import quote

from docutils import nodes
from docutils.parsers.rst.states import RSTState
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

from oauthcord.enums import Scope as OAuthScope


@dataclass(slots=True, frozen=True)
class Scope:
    member: OAuthScope

    @classmethod
    def from_name(cls, name: str, /) -> Scope:
        try:
            member = OAuthScope[name.upper()]
        except KeyError:
            member = OAuthScope(name)

        return cls(member)

    @property
    def enum_reference(self) -> str:
        return f"oauthcord.Scope.{self.member.name}"

    @property
    def display_name(self) -> str:
        return self.member.value

    @property
    def docs_link(self) -> str:
        encoded_display_name = quote(self.display_name, safe="")
        link = f"https://docs.discord.food/topics/oauth2#:~:text={encoded_display_name}"
        return f"`Discord OAuth2 docs <{link}>`_"

    @property
    def required_text(self) -> str:
        return (
            f"This method requires the "
            f":attr:`{self.display_name} <{self.enum_reference}>` scope."
        )

    @property
    def more_info_text(self) -> str:
        return f"For more information, see the {self.docs_link}."

    def to_required_paragraph(self, *, state: RSTState, lineno: int) -> nodes.paragraph:
        paragraph = nodes.paragraph(classes=["scope-callout-body"])
        inline_nodes, _messages = state.inline_text(self.required_text, lineno)
        paragraph.extend(inline_nodes)
        return paragraph

    def to_more_info_paragraph(
        self, *, state: RSTState, lineno: int
    ) -> nodes.paragraph:
        paragraph = nodes.paragraph(classes=["scope-callout-more"])
        inline_nodes, _messages = state.inline_text(self.more_info_text, lineno)
        paragraph.extend(inline_nodes)
        return paragraph


class ScopeDirective(SphinxDirective):
    required_arguments = 1
    optional_arguments = 0
    has_content = False

    def run(self) -> list[nodes.Node]:
        scope_name = self.arguments[0].strip()
        if not scope_name:
            raise self.error("scope directive requires a scope name")

        try:
            scope = Scope.from_name(scope_name)
        except (KeyError, ValueError) as error:
            names = [member.name for member in OAuthScope] + [
                member.value for member in OAuthScope
            ]
            close_matches = get_close_matches(scope_name, names, n=1, cutoff=0.2)
            if close_matches:
                raise self.error(
                    f"unknown scope: {scope_name!r}. Did you mean {close_matches[0]!r}?"
                ) from error
            raise self.error(f"unknown scope: {scope_name!r}") from error

        container = nodes.container(classes=["scope-callout"])
        title = nodes.paragraph(classes=["scope-callout-title"])
        title += nodes.strong(text="Required Scope")

        body_paragraph = scope.to_required_paragraph(
            state=self.state, lineno=self.lineno
        )
        more_info_paragraph = scope.to_more_info_paragraph(
            state=self.state, lineno=self.lineno
        )

        container.extend([title, body_paragraph, more_info_paragraph])
        return [container]


def setup(app: Sphinx) -> dict[str, bool | str]:
    app.add_directive("scope", ScopeDirective)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
