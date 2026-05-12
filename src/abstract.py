# Defines class as an interface

import os


class Module:
    def __init__(self, verbose=False):
        self._verbose = verbose

    def logger(self, string):
        if self._verbose:
            print(f"{self}: {string}")

    def update_version(self) -> bool:  # type: ignore[empty-body]
        """Update the package to lts"""
        pass

    def read_version_from_file(self, file_path) -> str:
        """Read version from the file"""
        version = ""
        with open(file_path, "r") as f:
            version = f.readline()
        self.logger(f"Version read from file {os.path.basename(file_path)}: {version}")
        return version

    def append_compiled(self, service, version):
        """Append compiled service version to file"""
        with open(self._compiled_file, "a") as f:
            f.write(f"{service}:{version}\n")

    def build_x86_64(self) -> bool:  # type: ignore[empty-body]
        """Build x86_64 for the specified module"""
        pass

    def build_x86(self) -> bool:  # type: ignore[empty-body]
        """32 bit architectures"""
        pass

    def build_arm64(self) -> bool:  # type: ignore[empty-body]
        """Build arm64"""
        pass

    def build_arm32(self) -> bool:  # type: ignore[empty-body]
        """Build arm32"""
        pass


