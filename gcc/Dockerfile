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
# git cline gives problems with emulator
# RUN git clone --depth=1 --branch "releases/gcc-${GCC_VERSION}" https://github.com/gcc-mirror/gcc.git
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

FROM alpine:3.21
ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" gccuser 2>/dev/null || true && \
    adduser -D -u "$HOST_UID" -G gccuser gccuser 2>/dev/null || true

COPY --from=builder /opt/gcc-static /gcc-static
USER gccuser

CMD ["sh", "-c", "mkdir -p /output && cp -r /gcc-static/bin/. /output && chmod -R 755 /output"]