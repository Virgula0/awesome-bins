FROM alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d AS builder
ARG MARIADB_VERSION=12.2.2
ARG TARGETARCH

RUN --mount=type=cache,id=apk-mariadb,target=/var/cache/apk \
    apk add --no-cache \
    build-base \
    cmake \
    openssl-dev \
    openssl-libs-static \
    zlib-static \
    zlib-dev \
    libxml2-dev \
    libxml2-static \
    curl-dev \
    curl-static \
    ncurses-static \
    ncurses-dev \
    linux-headers \
    ccache \
    wget

WORKDIR /build

RUN wget https://archive.mariadb.org/mariadb-${MARIADB_VERSION}/source/mariadb-${MARIADB_VERSION}.tar.gz \
    && tar xzf mariadb-${MARIADB_VERSION}.tar.gz

WORKDIR /build/mariadb-${MARIADB_VERSION}

RUN mkdir build && cd build && \
    cmake .. \
        -DCMAKE_INSTALL_PREFIX=/opt/mariadb-static \
        -DBUILD_SHARED_LIBS=OFF \
        -DWITH_SSL=system \
        -DOPENSSL_CRYPTO_LIBRARY=/usr/lib/libcrypto.a \
        -DOPENSSL_SSL_LIBRARY=/usr/lib/libssl.a \
        -DWITH_ZLIB=system \
        -DZLIB_LIBRARY=/usr/lib/libz.a \
        -DWITH_READLINE=OFF \
        -DCURSES_LIBRARY=/usr/lib/libncurses.a \
        -DLIBXML2_LIBRARY=/usr/lib/libxml2.a \
        -DCURL_LIBRARY=/usr/lib/libcurl.a \
        -DCMAKE_EXE_LINKER_FLAGS="-static -no-pie" \
        -DCMAKE_FIND_LIBRARY_SUFFIXES=".a" \
        -DWITH_UNIT_TESTS=OFF \
        -DWITH_MYSQLD=OFF \
        -DWITH_SERVER=OFF \
        -DPLUGIN_AUTH_EXAMPLES=NO \
        -DPLUGIN_AUTH_PAM=NO \
        -DPLUGIN_AUTH_PAM_V1=NO \
        -DWITH_WSREP=OFF \
        -DWITH_INNODB=OFF \
        -DWITH_ARCHIVE=OFF \
        -DWITH_BLACKHOLE=OFF \
        -DWITH_FEDERATED=OFF \
        -DWITH_PARTITION=OFF \
        -DWITH_CSV=OFF \
        -DWITH_MYISAM=OFF \
        -DWITH_MYISAMMRG=OFF \
        -DWITH_HEAP=OFF \
        -DWITH_PERFSCHEMA=OFF \
        -DWITH_TOKUDB=OFF \
        -DWITH_MROONGA=OFF \
        -DWITH_SPIDER=OFF \
        -DWITH_OQGRAPH=OFF \
        -DWITH_CASSANDRA=OFF \
        -DWITH_CONNECT=OFF

RUN --mount=type=cache,id=ccache-mariadb-${TARGETARCH},target=/root/.ccache \
    export PATH="/usr/lib/ccache/bin:$PATH" && \
    export CCACHE_DIR=/root/.ccache && \
    cd build && \
    make -j$(nproc) mariadb mariadb-dump mariadb-binlog mariadb-import mariadb-show mariadb-test mariadb-check mariadb-slap mariadb-admin

RUN cd build && \
    install -D -m 755 client/mariadb /opt/mariadb-static/bin/mariadb && \
    install -D -m 755 client/mariadb-dump /opt/mariadb-static/bin/mariadb-dump && \
    install -D -m 755 client/mariadb-binlog /opt/mariadb-static/bin/mariadb-binlog && \
    install -D -m 755 client/mariadb-import /opt/mariadb-static/bin/mariadb-import && \
    install -D -m 755 client/mariadb-show /opt/mariadb-static/bin/mariadb-show && \
    install -D -m 755 client/mariadb-test /opt/mariadb-static/bin/mariadb-test && \
    install -D -m 755 client/mariadb-check /opt/mariadb-static/bin/mariadb-check && \
    install -D -m 755 client/mariadb-slap /opt/mariadb-static/bin/mariadb-slap && \
    install -D -m 755 client/mariadb-admin /opt/mariadb-static/bin/mariadb-admin

RUN echo "=== Static binary check ===" && \
    for bin in mariadb mariadb-dump mariadb-binlog mariadb-import mariadb-show mariadb-test mariadb-check mariadb-slap mariadb-admin; do \
        printf "%s: " "$bin"; \
        file "/opt/mariadb-static/bin/$bin" | grep -q "statically linked" \
            && echo "OK (static)" \
            || { echo "FAILED (not static) - $(file /opt/mariadb-static/bin/$bin)"; exit 1; }; \
    done

FROM alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d
ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" mariadbuser 2>/dev/null || true \
    && adduser -D -u "$HOST_UID" -G mariadbuser mariadbuser 2>/dev/null || true

COPY --from=builder /opt/mariadb-static/bin/ /mariadb-bins/
RUN chmod -R 755 /mariadb-bins/
USER mariadbuser
CMD ["sh", "-c", "mkdir -p /output && cp -r /mariadb-bins/. /output/ && chmod -R 755 /output"]