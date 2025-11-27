FROM flink:1.17

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-dev openjdk-11-jdk-headless && \
    apt-get clean

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64

# Create symlink so pemja finds JNI headers
RUN ln -s /usr/lib/jvm/java-11-openjdk-arm64 /opt/java/openjdk

# Install Flink Python API
RUN pip3 install apache-flink==1.17.2

WORKDIR /opt/flink/usrlib/
COPY unique_users_per_minute.py .

CMD ["flink", "run", "-py", "unique_users_per_minute.py"]
