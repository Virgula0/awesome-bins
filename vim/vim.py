from src.abstract import Module
from src.docker_custom import CustomClient
from pathlib import Path
import requests as r
import re
import os


class Vim(Module):
    _url = "https://raw.githubusercontent.com/vim/vim/refs/heads/master/src/version.h"
    _version_c_url = (
        "https://raw.githubusercontent.com/vim/vim/refs/heads/master/src/version.c"
    )
    _target_name = "vim"
    _lts_file = os.path.join(Path(__file__).resolve().parent, "lts_version")
    _stable_file = os.path.join(
        Path(__file__).resolve().parent, "stable_working_version"
    )
    _compiled_file = os.path.join(Path(__file__).resolve().parent, "compiled_versions")
    _compose_file = os.path.join(Path(__file__).resolve().parent, "docker-compose.yaml")

    _verbose = False
    _docker_client = None

    _current_version = "0"
    _docker_env_version = "0"
    _stable_fallback_version = "0"

    def __init__(self, verbose, docker_client: CustomClient):
        super().__init__(verbose=verbose)
        self._verbose = verbose
        self._docker_client = docker_client

        self._current_version = self.read_version_from_file(self._lts_file)
        self._docker_env_version = f"VIM_VERSION={self._current_version}"

        self._stable_fallback_version = self.read_version_from_file(self._stable_file)

    def __str__(self):
        return self._target_name.upper()

    def update_version(self):
        try:
            gh_content = r.get(self._url)

            major = re.search(
                r"#define\s+VIM_VERSION_MAJOR\s+(\d+)",
                gh_content.text,
            )

            minor = re.search(
                r"#define\s+VIM_VERSION_MINOR\s+(\d+)",
                gh_content.text,
            )

            if major is None or minor is None:
                raise ValueError(
                    f"regex version not matched in url file {major}.{minor}"
                )

            major = major.group(1)
            minor = minor.group(1)

            version_c = r.get(self._version_c_url)

            patches = re.findall(
                r"^\s*(\d+),",
                version_c.text,
                re.MULTILINE,
            )

            if not patches:
                raise ValueError("could not extract Vim patch level")

            build = max(int(p) for p in patches)

            #
            # Vim tags use 4-digit zero-padded patch level
            #
            version = f"{major}.{minor}.{build:04d}"

            self.logger(f"Latest version: {version}")

            with open(self._lts_file, "w") as f:
                f.write(version)

            self._current_version = version
            self._docker_env_version = f"VIM_VERSION={self._current_version}"

        except Exception as ex:
            self.logger(ex)
            return False

        return True

    def _build(self, service):
        result = self._docker_client.run(
            service=service,
            compose_file=self._compose_file,
            version=self._docker_env_version,
        )

        if result:
            self.append_compiled(service=service, version=self._current_version)
            return result

        self.logger(
            f"ERROR for {service}! compilation not successful for version {self._current_version} "
            f"falling back and compile {self._stable_fallback_version}"
        )

        result = self._docker_client.run(
            service=service,
            compose_file=self._compose_file,
            version=f"VIM_VERSION={self._stable_fallback_version}",
        )

        if result:
            self.append_compiled(service=service, version=self._stable_fallback_version)

        return result

    def build_x86_64(self):
        """
        VIM_VERSION=9.2.0499 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up vim-static-build-x86_64 --build
        """
        return self._build("vim-static-build-x86_64")

    def build_x86(self):
        """
        VIM_VERSION=9.2.0499 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up vim-static-build-x86 --build
        """
        return self._build("vim-static-build-x86")

    def build_arm64(self):
        """
        VIM_VERSION=9.2.0499 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up vim-static-build-arm64 --build
        """
        return self._build("vim-static-build-arm64")

    def build_arm32(self):
        """
        VIM_VERSION=9.2.0499 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up vim-static-build-arm32 --build
        """
        return self._build("vim-static-build-arm32")
