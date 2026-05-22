from src.abstract import Module
from src.docker_custom import CustomClient
from pathlib import Path
import os
import requests as r


class Tmux(Module):
    _url = "https://api.github.com/repos/tmux/tmux/releases/latest"  # releases available for tmux
    _target_name = "tmux"
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
        self._docker_env_version = f"TMUX_VERSION={self._current_version}"

        self._stable_fallback_version = self.read_version_from_file(self._stable_file)

    def __str__(self):
        return self._target_name.upper()

    def update_version(self):
        try:
            response = r.get(self._url, timeout=10)
            response.raise_for_status()
            data = response.json()

            tag = data["tag_name"]
            version = tag[1:] if tag.startswith("v") else tag

            self.logger(f"Latest tmux version: {version}")

            with open(self._lts_file, "w") as f:
                f.write(version)

            self._current_version = version
            self._docker_env_version = f"TMUX_VERSION={self._current_version}"

            return True

        except Exception as e:
            self.logger(f"Error: {e}")
            return False

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
            version=f"TMUX_VERSION={self._stable_fallback_version}",
        )

        if result:
            self.append_compiled(service=service, version=self._stable_fallback_version)

        return result

    def build_x86_64(self):
        """
        TMUX_VERSION=tmux3.6b HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up tmux-static-build-x86_64 --build
        """
        return self._build("tmux-static-build-x86_64")

    def build_x86(self):
        """
        TMUX_VERSION=tmux3.6b HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up tmux-static-build-x86 --build
        """
        return self._build("tmux-static-build-x86")

    def build_arm64(self):
        """
        TMUX_VERSION=tmux3.6b HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up tmux-static-build-arm64 --build
        """
        return self._build("tmux-static-build-arm64")

    def build_arm32(self):
        """
        TMUX_VERSION=tmux3.6b HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up tmux-static-build-arm32 --build
        """
        return self._build("tmux-static-build-arm32")
