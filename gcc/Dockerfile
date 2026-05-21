FROM alpine:3.21 AS builder
ARG GCC_VERSION
ARG TARGETARCH

RUN --mount=type=cache,id=apk-gcc-${TARGETARCH},target=/var/cache/apk \
    apk add --no-cache \
    build-base git linux-headers ccache \
    flex bison curl file \
    zlib-dev zlib-static musl-dev

WORKDIR /build
RUN git clone --depth=1 --branch "releases/gcc-${GCC_VERSION}" https://github.com/gcc-mirror/gcc.git

WORKDIR /build/gcc
RUN ./contrib/download_prerequisites

WORKDIR /build/gcc-build
RUN --mount=type=cache,id=ccache-gcc-${TARGETARCH},target=/root/.ccache \
    export PATH="/usr/lib/ccache/bin:$PATH" && \
    export CCACHE_DIR=/root/.ccache && \
    ../gcc/configure \
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