FROM alpine:3.21 AS builder
ARG PG_VERSION=16.1
ARG TARGETARCH

RUN --mount=type=cache,id=apk-pg,target=/var/cache/apk \
    apk add --no-cache \
    build-base \
    openssl-dev \
    openssl-libs-static \
    wget \
    linux-headers \
    ccache

WORKDIR /build

# Download isolated — a failed compile doesn't trigger a re-fetch
RUN wget https://ftp.postgresql.org/pub/source/v${PG_VERSION}/postgresql-${PG_VERSION}.tar.gz \
    && tar xzf postgresql-${PG_VERSION}.tar.gz

WORKDIR /build/postgresql-${PG_VERSION}

# Configure + Makefile patch in their own layer.
# This layer is only invalidated when PG_VERSION changes.
RUN ./configure \
        --prefix=/opt/pg-static \
        --without-readline \
        --without-zlib \
        --without-icu \
        --disable-shared \
        --with-openssl \
        CFLAGS='-std=c17' \
        LDFLAGS='-static -no-pie' \
    && sed -i 's/^all: /all-orig: /' src/interfaces/libpq/Makefile \
    && echo 'all: libpq.a' >> src/interfaces/libpq/Makefile

# Compile with ccache + parallel make
RUN --mount=type=cache,id=ccache-pg-${TARGETARCH},target=/root/.ccache \
    export PATH="/usr/lib/ccache/bin:$PATH" && \
    export CCACHE_DIR=/root/.ccache && \
    make -j$(nproc) -C src/port          CC="ccache gcc" && \
    make -j$(nproc) -C src/common        CC="ccache gcc" && \
    make -j$(nproc) -C src/fe_utils      CC="ccache gcc" && \
    make -j$(nproc) -C src/interfaces/libpq libpq.a CC="ccache gcc" && \
    make -j$(nproc) -C src/bin/psql      CC="ccache gcc" && \
    make -j$(nproc) -C src/bin/pg_dump   CC="ccache gcc" && \
    install -D -m 755 src/bin/psql/psql         /opt/pg-static/bin/psql && \
    install -D -m 755 src/bin/pg_dump/pg_dump    /opt/pg-static/bin/pg_dump && \
    install -D -m 755 src/bin/pg_dump/pg_dumpall /opt/pg-static/bin/pg_dumpall && \
    echo "=== Static binary check ===" && \
    for bin in psql pg_dump pg_dumpall; do \
        printf "%s: " "$bin"; \
        file "/opt/pg-static/bin/$bin" | grep -q "statically linked" \
            && echo "OK (static)" \
            || { echo "FAILED (not static) - $(file /opt/pg-static/bin/$bin)"; exit 1; }; \
    done


FROM alpine:3.21
ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" pguser 2>/dev/null || true \
    && adduser -D -u "$HOST_UID" -G pguser pguser 2>/dev/null || true

COPY --from=builder /opt/pg-static/bin/ /pg-bins/
RUN chmod -R 755 /pg-bins/
USER pguser
CMD ["sh", "-c", "mkdir -p /output && cp -r /pg-bins/. /output/ && chmod -R 755 /output"]