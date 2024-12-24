import asyncio
import aio_pika
import aiohttp
import json
from comfy.cli_args import args

class RabbitMQProcessor:
    def __init__(self, rabbitmq_host, queue_name, ready_url, push_url,statusMessage=None):
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name
        self.ready_url = ready_url
        self.push_url = push_url
        self.statusMessage = statusMessage
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    async def is_application_ready(self):
        """Check if the application is ready."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.ready_url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result["exec_info"]["queue_remaining"] == 0:
                            return True
                        else:
                            return False
            except aiohttp.ClientError as e:
                print(f"Error checking application readiness: {e}")
        return False
    
    async def publish_message_to_queue(self, message_body):
        try:
            connection = await aio_pika.connect_robust(self.rabbitmq_host)
            async with connection.channel() as channel:
                await channel.declare_queue(self.queue_name, durable=True)
                message = aio_pika.Message(body=json.dumps(message_body).encode("utf-8"))
                await channel.default_exchange.publish(
                    message, routing_key=self.queue_name
                )
                print(f"Message published to queue '{self.queue_name}'")
        except Exception as e:
            print(f"Failed to publish message: {e}")


    async def push_to_application(self, data):
        """Send data to the application."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.push_url, json=data) as response:
                    if response.status == 200:
                        print("Data successfully sent to the application.")
                    else:
                        print(f"Failed to send data. Status code: {response.status}, Response: {await response.text()}")
            except aiohttp.ClientError as e:
                print(f"Error pushing data to application: {e}")

    async def consume_messages(self):
        connection = await aio_pika.connect_robust(self.rabbitmq_host)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(self.queue_name, durable=True)
            print(f"Listening for messages on queue: {self.queue_name}")
            async for message in queue:
                async with message.process():
                    await self.process_message(channel, None, None, message.body)


    async def process_message(self, channel, method, properties, body):
        """Callback function to process messages from the queue."""
        data = json.loads(body)

        # Wait for the application to be ready
        print("Recieved message from RabbitMQ, Waiting for the application to be ready...")
        #while True:
        self.statusMessage.get()
        print("Application Ready, sending prompt")
            #while not await self.is_application_ready():
            #    await asyncio.sleep(1)

        # Push the message to the application
        p = {"prompt": data[2]}
        await self.push_to_application(p)

    async def run(self):
        await self.consume_messages()

def runQueuePuller(statusMessage):
    # RabbitMQ Configuration
    RABBITMQ_HOST = args.rabbitUrl
    QUEUE_NAME = args.queueName
    APPLICATION_READY_URL = args.ready_url
    APPLICATION_PUSH_URL = args.push_url

    processor = RabbitMQProcessor(
        rabbitmq_host=RABBITMQ_HOST,
        queue_name=QUEUE_NAME,
        ready_url=APPLICATION_READY_URL,
        push_url=APPLICATION_PUSH_URL,
        statusMessage=statusMessage
    )
    asyncio.run(processor.run())


