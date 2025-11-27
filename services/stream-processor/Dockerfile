FROM flink:1.17

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

RUN pip3 install apache-flink==1.17.2

WORKDIR /opt/flink/usrlib/

COPY unique_users_per_minute.py .

CMD ["flink", "run", "-py", "unique_users_per_minute.py"]