from src.abstract import Module
from src.docker_custom import CustomClient
from pathlib import Path
import requests as r
import os


class Tcpdump(Module):
    _url = "https://api.github.com/repos/the-tcpdump-group/tcpdump/tags"
    _target_name = "tcpdump"
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
        self._docker_env_version = f"TCPDUMP_VERSION={self._current_version}"

        self._stable_fallback_version = self.read_version_from_file(self._stable_file)

    def __str__(self):
        return self._target_name.upper()

    def update_version(self):
        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            response = r.get(self._url, headers=headers, timeout=10)
            response.raise_for_status()
            tags = response.json()

            versions = []
            for tag in tags:
                tag_name = tag["name"]
                if tag_name.startswith("tcpdump-"):
                    # Store the full tag name
                    versions.append(tag_name)

            if not versions:
                self.logger("No version tags found in the repository.")
                return False

            # Sort tags using the numeric part only
            def get_version_key(tag):
                import re
                from packaging import version

                match = re.search(r"(\d+\.\d+\.\d+)", tag)
                if match:
                    return version.parse(match.group(1))
                return version.parse("0")

            latest_tag = max(versions, key=get_version_key)
            self.logger(f"Latest tcpdump version tag is: {latest_tag}")

            with open(self._lts_file, "w") as f:
                f.write(latest_tag)

            self._current_version = latest_tag
            self._docker_env_version = f"TCPDUMP_VERSION={self._current_version}"

            return True

        except r.exceptions.RequestException as e:
            self.logger(f"Network or API error: {e}")
        except Exception as ex:
            self.logger(f"An unexpected error occurred: {ex}")

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
            version=f"TCPDUMP_VERSION={self._stable_fallback_version}",
        )

        if result:
            self.append_compiled(service=service, version=self._stable_fallback_version)

        return result

    def build_x86_64(self):
        """
        TCPDUMP_VERSION=0.7.1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up tcpdump-static-build-x86_64 --build
        """
        return self._build("tcpdump-static-build-x86_64")

    def build_x86(self):
        """
        TCPDUMP_VERSION=0.7.1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up tcpdump-static-build-x86 --build
        """
        return self._build("tcpdump-static-build-x86")

    def build_arm64(self):
        """
        TCPDUMP_VERSION=0.7.1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up tcpdump-static-build-arm64 --build
        """
        return self._build("tcpdump-static-build-arm64")

    def build_arm32(self):
        """
        TCPDUMP_VERSION=0.7.1 HOST_UID=$(id -u) HOST_GID=$(id -g) docker-compose up tcpdump-static-build-arm32 --build
        """
        return self._build("tcpdump-static-build-arm32")
