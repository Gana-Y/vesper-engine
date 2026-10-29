FROM alpine:latest

# Install compilers, interpreters, core utilities, and microsecond telemetry tools
RUN apk add --no-cache \
    g++ \
    gcc \
    python3 \
    openjdk17-jdk \
    bash \
    coreutils \
    time

RUN ln -sf python3 /usr/bin/python

# Validate installations
RUN python --version && \
    g++ --version && \
    javac -version && \
    java -version

# Setup non-root execution directory
WORKDIR /workspace
RUN chown -R nobody:nogroup /workspace
