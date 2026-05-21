FROM alpine:3.21 AS builder
ARG PYTHON3_VERSION
ARG TARGETARCH

RUN apk add --no-cache \
    build-base git linux-headers ccache libc6-compat musl-dev \
    openssl-dev openssl-libs-static zlib-dev zlib-static \
    libffi-dev expat-dev expat-static bzip2-dev bzip2-static \
    xz-dev xz-static sqlite-dev sqlite-static \
    ncurses-dev ncurses-static readline-dev readline-static pkgconf

WORKDIR /build

RUN BRANCH_NAME=$(echo "${PYTHON3_VERSION}" | cut -d. -f1,2) && \
    git clone --depth=1 --branch "${BRANCH_NAME}" https://github.com/python/cpython.git || \
    git clone --depth=1 https://github.com/python/cpython.git

WORKDIR /build/cpython

# Disable test modules that cause link errors
RUN echo "*disabled*" > Modules/Setup.local && \
    echo "xxlimited" >> Modules/Setup.local && \
    echo "_testinternalcapi" >> Modules/Setup.local

RUN --mount=type=cache,id=ccache-python-${TARGETARCH},target=/root/.ccache \
    export PATH="/usr/lib/ccache/bin:$PATH" && \
    export CCACHE_DIR=/root/.ccache && \
    ./configure \
        --prefix=/opt/python-static \
        --disable-shared \
        --without-ensurepip \
        MODULE_BUILDTYPE=static \
        CFLAGS="-Os -static" \
        CPPFLAGS="-static" \
        LDFLAGS="-static -no-pie" \
    && sed -i 's/\*shared\*/\*static\*/g' Modules/Setup.stdlib \
    && make -j$(nproc) \
    && make install

RUN for bin in /opt/python-static/bin/python3.??; do \
        [ -f "$bin" ] || continue; \
        printf "%s: " "$(basename "$bin")"; \
        file "$bin" | grep -q "statically linked" && echo "OK (static)" || { echo "FAILED (not static) - $bin"; exit 1; }; \
    done

FROM alpine:3.21
ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" pyuser 2>/dev/null || true && \
    adduser -D -u "$HOST_UID" -G pyuser pyuser 2>/dev/null || true

COPY --from=builder /opt/python-static/bin/ /python-static/
RUN chmod -R 755 /python-static/

USER pyuser
CMD ["sh", "-c", "mkdir -p /output && cp -r /python-static/python3.?? /output/ && chmod -R 755 /output"]