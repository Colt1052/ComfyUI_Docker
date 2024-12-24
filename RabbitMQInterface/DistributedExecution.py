import logging
from .DistributedQueuePuller import RabbitMQProcessor

async def ModifiedPut(self, item):
    try:
        logging.info("Putting prompt in distributed queue")
        if not hasattr(self,"rabbitMQProcessor"):
            RABBITMQ_HOST = 'amqp://guest:guest@localhost:5672'
            QUEUE_NAME = 'my_queue'
            APPLICATION_READY_URL = 'http://localhost:8188/api/prompt'
            APPLICATION_PUSH_URL = 'http://localhost:8188/api/prompt'
            self.rabbitMQProcessor = RabbitMQProcessor(
                rabbitmq_host=RABBITMQ_HOST,
                queue_name=QUEUE_NAME,
                ready_url=APPLICATION_READY_URL,
                push_url=APPLICATION_PUSH_URL
            )
        await self.rabbitMQProcessor.publish_message_to_queue(item)
    except Exception as e:
        logging.info("Error putting item in queue: " + str(e))

