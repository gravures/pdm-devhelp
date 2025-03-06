# Copyright (c) 2025 - Gilles Coissac
#
# pdm-devhelp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# pdm-devhelp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pdm-devhelp. If not, see <https://www.gnu.org/licenses/>
#
# ruff: noqa: D100, D102, D103, PLR6301, INP001
from __future__ import annotations

import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

from pdm.cli.commands.base import BaseCommand
from pdm.core import main as cmain
from pdm.project import Config
from pdm_bump.actions.hook import TagChanges
from pdm_bump.actions.increment import (
    DevelopmentVersionIncrementingVersionModifier,
    EpochIncrementingVersionModifier,
    FinalizingVersionModifier,
    MajorIncrementingVersionModifier,
    MicroIncrementingVersionModifier,
    MinorIncrementingVersionModifier,
    PostVersionIncrementingVersionModifier,
    ResetNonSemanticPartsModifier,
)
from pdm_bump.actions.poetry_like import (
    PoetryLikePreMajorVersionModifier,
    PoetryLikePreMinorVersionModifier,
    PoetryLikePrePatchVersionModifier,
    PoetryLikePreReleaseVersionModifier,
)
from pdm_bump.actions.preview import (
    PreReleaseIncrementingVersionModifier,
)
from pdm_bump.actions.vcs import SuggestNewVersion
from pdm_bump.core.version import Version
from pdm_bump.vcs.gitcli import GitCliVcsProvider


if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace

    from pdm.core import Core
    from pdm.project import Project


class VersionCommand(BaseCommand):
    """Bumps the version to a next version following PEP440."""

    def __init__(self) -> None:
        self.project: Project
        self.parser: ArgumentParser

    def add_arguments(self, parser: ArgumentParser) -> None:
        self.parser = parser
        sub = parser.add_subparsers()
        TagChanges.configure(parser)

        tmp = sub.add_parser(
            name=SuggestNewVersion.name,
            description=SuggestNewVersion.description,
        )
        SuggestNewVersion._update_command(sub_parser=tmp)  # pyright: ignore[reportPrivateUsage]
        tmp.set_defaults(suggest=SuggestNewVersion)

        for action in (
            DevelopmentVersionIncrementingVersionModifier,
            EpochIncrementingVersionModifier,
            MajorIncrementingVersionModifier,
            MicroIncrementingVersionModifier,
            MinorIncrementingVersionModifier,
            FinalizingVersionModifier,
            PostVersionIncrementingVersionModifier,
            PreReleaseIncrementingVersionModifier,
            PoetryLikePreMajorVersionModifier,
            PoetryLikePreMinorVersionModifier,
            PoetryLikePrePatchVersionModifier,
            PoetryLikePreReleaseVersionModifier,
            ResetNonSemanticPartsModifier,
        ):
            tmp = sub.add_parser(
                name=action.name,
                description=action.description,
            )
            action._update_command(sub_parser=tmp)  # pyright: ignore[reportPrivateUsage]
            tmp.set_defaults(modifier=action)

    def save_version(self, _: Version) -> None:
        return

    def handle(self, project: Project, options: Namespace) -> None:
        # name = project.config["hello.name"] if not options.name else options.name
        self.project = project
        git = GitCliVcsProvider(self.project.root)
        current = Version.from_string(self._get_version())
        next_: Version | None = None
        kwds = vars(options)
        do_tag: bool = kwds.pop("tag", False)
        dirty: bool = kwds.pop("dirty", False)
        prepend: bool = kwds.pop("prepend_letter_v", True)

        if command := kwds.pop("suggest", False):
            action = command(current, git)
            with redirect_stdout(StringIO()):
                next_ = action.run(dry_run=True)
        elif command := kwds.pop("modifier", False):
            action = command(current, self, **kwds)
            with redirect_stdout(StringIO()):
                next_ = action.create_new_version()

        if next_:
            if do_tag:
                if next_ != current:
                    self._create_tag(next_, git, prepend, dirty)
                else:
                    sys.stderr.write("will not create tag")
            sys.stderr.write("new version will be:\n")
            sys.stdout.write(f"{next_!s}\n")
        else:
            # no sub-command, just pdm bump
            sys.stderr.write("current version is:\n")
            sys.stdout.write(f"{self._get_version()}\n")
            if do_tag:
                self._create_tag(current, git, prepend, dirty)

    def _create_tag(
        self,
        version: Version,
        git: GitCliVcsProvider,
        prepend: bool,
        allow_dirty: bool,
    ) -> None:
        if not git.is_clean and not allow_dirty:
            sys.stderr.write("repository is dirty, canno't create a Tag.")
            return

        sys.stdout.write("creating revision tag from the resulting version\n")
        git.create_tag_from_version(version, prepend_letter_v=prepend)

    def _get_version(self) -> str:
        try:
            with redirect_stdout(StringIO()) as out:
                cmain(["show", "--version"])
            return out.getvalue().strip()
        except SystemError as err:
            raise RuntimeError from err


def has_dynamic_scm_version() -> bool:
    config = Config(Path("pyproject.toml")).self_data
    return (
        config.get("build-system.build-backend") == "pdm.backend"
        and "version" in config.get("project.dynamic", [])
        and config.get("tool.pdm.version.source") == "scm"
    )


def main(core: Core) -> None:
    if has_dynamic_scm_version():
        core.register_command(VersionCommand, "bump")
