# Defines class as an interface


class Module:
    def update_version(self) -> bool:  # type: ignore[empty-body]
        """Update the package to lts"""
        pass

    def read_version_from_file(self, lts_file) -> str:
        """Read version from the file"""
        version = ""
        with open(lts_file, "r") as f:
            version = f.readline()  # only first line needed
        return version

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

    def logger(self, string):
        print(string)
