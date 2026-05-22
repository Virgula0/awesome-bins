FROM alpine:3.21 AS builder
ARG GCC_VERSION
ARG TARGETARCH
ARG TARGETVARIANT

RUN --mount=type=cache,id=apk-gcc-${TARGETARCH},target=/var/cache/apk \
    apk add --no-cache \
    build-base linux-headers ccache \
    flex bison curl file \
    zlib-dev zlib-static musl-dev

WORKDIR /build
RUN wget "https://github.com/gcc-mirror/gcc/archive/refs/heads/releases/gcc-${GCC_VERSION}.tar.gz" -O gcc.tar.gz \
    && tar xzf gcc.tar.gz \
    && rm gcc.tar.gz \
    && mv gcc-releases-gcc-${GCC_VERSION} gcc

WORKDIR /build/gcc
RUN ./contrib/download_prerequisites

WORKDIR /build/gcc-build
RUN --mount=type=cache,id=ccache-gcc-${TARGETARCH},target=/root/.ccache \
    export PATH="/usr/lib/ccache/bin:$PATH" && \
    export CCACHE_DIR=/root/.ccache && \
    TRIPLE=$(case "${TARGETARCH}-${TARGETVARIANT}" in \
        amd64-)    echo "x86_64-alpine-linux-musl" ;; \
        386-)      echo "i386-alpine-linux-musl" ;; \
        arm64-)    echo "aarch64-alpine-linux-musl" ;; \
        arm-v7)    echo "armv7-alpine-linux-musleabihf" ;; \
        arm-v6)    echo "armv6-alpine-linux-musleabihf" ;; \
        *)         ../gcc/config.guess ;; \
    esac) && \
    ../gcc/configure \
    --build=${TRIPLE} --host=${TRIPLE} \
    --prefix=/opt/gcc-static \
    --disable-shared \
    --enable-static \
    --disable-bootstrap \
    --disable-multilib \
    --enable-languages=c,c++ \
    --disable-libstdcxx-pch \
    --disable-libsanitizer \
    --disable-libssp \
    --disable-libquadmath \
    --disable-libgomp \
    --disable-decimal-float \
    --disable-nls \
    CFLAGS="-Os" \
    CXXFLAGS="-Os" \
    LDFLAGS="-static" \
    CC="gcc" \
    CXX="g++"

RUN make -j$(nproc) && make install

RUN for bin in /opt/gcc-static/bin/gcc /opt/gcc-static/bin/g++ /opt/gcc-static/bin/cpp; do \
    [ -f "$bin" ] || continue; \
    file "$bin" | grep -q "static" || { echo "NOT STATIC: $bin"; exit 1; }; \
    done && \
    find /opt/gcc-static -type f -executable -exec strip --strip-all {} \;

RUN GCC_TRIPLE=$(/opt/gcc-static/bin/gcc -dumpmachine) && \
    GCC_VERSION=$(/opt/gcc-static/bin/gcc -dumpversion) && \
    echo "$GCC_TRIPLE" > /opt/gcc-static/gcc-triple && \
    echo "$GCC_VERSION" > /opt/gcc-static/gcc-version

FROM alpine:3.21
ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" gccuser 2>/dev/null || true && \
    adduser -D -u "$HOST_UID" -G gccuser gccuser 2>/dev/null || true

COPY --from=builder /opt/gcc-static /gcc-static

RUN for tool in gcc g++; do \
        mv "/gcc-static/bin/$tool" "/gcc-static/bin/$tool.real" && \
        printf '#!/bin/sh\nSELF_DIR=$(cd "$(dirname "$0")" && pwd)\nINSTALL_ROOT=$(cd "$SELF_DIR/.." && pwd)\nGCC_TRIPLE=$(cat "$INSTALL_ROOT/gcc-triple")\nGCC_VERSION=$(cat "$INSTALL_ROOT/gcc-version")\nexport GCC_EXEC_PREFIX="$INSTALL_ROOT/libexec/gcc/"\nexec "$SELF_DIR/%s.real" "-B$INSTALL_ROOT/lib/gcc/$GCC_TRIPLE/$GCC_VERSION/" "-L$INSTALL_ROOT/lib" "-L$INSTALL_ROOT/lib/gcc/$GCC_TRIPLE/$GCC_VERSION" "-static" "$@"\n' "$tool" > "/gcc-static/bin/$tool" && \
        chmod 755 "/gcc-static/bin/$tool"; \
    done && \
    if [ -f /gcc-static/bin/cpp ]; then \
        mv /gcc-static/bin/cpp /gcc-static/bin/cpp.real && \
        printf '#!/bin/sh\nSELF_DIR=$(cd "$(dirname "$0")" && pwd)\nINSTALL_ROOT=$(cd "$SELF_DIR/.." && pwd)\nGCC_TRIPLE=$(cat "$INSTALL_ROOT/gcc-triple")\nGCC_VERSION=$(cat "$INSTALL_ROOT/gcc-version")\nexport GCC_EXEC_PREFIX="$INSTALL_ROOT/libexec/gcc/"\nexec "$SELF_DIR/cpp.real" "-I$INSTALL_ROOT/include" "$@"\n' > /gcc-static/bin/cpp && \
        chmod 755 /gcc-static/bin/cpp; \
    fi

USER gccuser

CMD ["sh", "-c", "mkdir -p /output && cp -r /gcc-static/. /output && chmod -R 755 /output"]