FROM rabbitmq:3.9

# Define environment variables.
ENV RABBITMQ_USER vissim_outputque
ENV RABBITMQ_PASSWORD 123456
ENV RABBITMQ_PID_FILE /var/lib/rabbitmq

COPY ./config/rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
# ENV RABBITMQ_NODE_PORT 5673

ADD init.sh /init.sh
RUN chmod +x /init.sh

# Define default command
CMD ["/init.sh"]
