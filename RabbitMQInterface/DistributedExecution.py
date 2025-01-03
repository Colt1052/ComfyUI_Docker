import logging
from .DistributedQueuePuller import RabbitMQProcessor
from comfy.cli_args import args

async def ModifiedPut(self, item):
    try:
        logging.info("Putting prompt in distributed queue")
        if not hasattr(self,"rabbitMQProcessor"):
            RABBITMQ_HOST = args.rabbitUrl
            QUEUE_NAME = args.queueName
            APPLICATION_READY_URL = args.ready_url
            APPLICATION_PUSH_URL = args.push_url
            self.rabbitMQProcessor = RabbitMQProcessor(
                rabbitmq_host=RABBITMQ_HOST,
                queue_name=QUEUE_NAME,
                ready_url=APPLICATION_READY_URL,
                push_url=APPLICATION_PUSH_URL
            )
        await self.rabbitMQProcessor.publish_message_to_queue(item)
    except Exception as e:
        logging.info("Error putting item in queue: " + str(e))

