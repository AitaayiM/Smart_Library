const axios = require('axios');
const amqp = require('amqplib');
const readline = require('readline');

const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE5NDQ3OTQ1LCJpYXQiOjE3MTgxNTE5NDUsImp0aSI6IjRiMzk4YWRlOWE0YzRhNTFhYmJhOGQ2YzM1NDk3MTA1IiwidXNlcl9pZCI6Mn0.beaZ6HUXC4lOafXNEVQG62s5CwaIF8LjQEJ0mNYGUbs';
const USER_ID = 1;
const RECEIVER_ID = 25;
const DJANGO_URL = 'http://localhost:8000/api/available/';
const API_URL_SEND = 'http://localhost:8000/api/chat/message/send';
const API_URL_GET = 'http://localhost:8000/api/chat/message/get/';
const API_URL_QUEUE = 'http://localhost:8000/api/chat/message/token';
const RABBITMQ_HOST = 'localhost';

let QUEUE_NAME = '';
let NAME_QUEUE = '';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function isDjangoServerAvailable(url) {
  try {
    const response = await axios.get(url);
    return response.status === 200;
  } catch (error) {
    return false;
  }
}

async function getQueueTokens() {
  try {
    const response = await axios.post(API_URL_QUEUE, { receiver_id: RECEIVER_ID }, {
      headers: { 'Authorization': `Bearer ${TOKEN}` }
    });
    QUEUE_NAME = response.data.queue_token_sender;
    NAME_QUEUE = response.data.queue_token_receiver;
  } catch (error) {
    console.error('Error getting queue tokens:', error);
  }
}

class MessageSender {
  constructor(content) {
    this.send(content);
  }

  async send(content) {
    try {
      const connection = await amqp.connect(`amqp://${RABBITMQ_HOST}`);
      const channel = await connection.createChannel();
      await channel.assertQueue(QUEUE_NAME);
      channel.sendToQueue(QUEUE_NAME, Buffer.from(content));
      //console.log(`[x] Sent ${content}`);
      await channel.close();
      await connection.close();
    } catch (error) {
      console.error('Error sending message:', error);
    }
  }
}

async function sendMessage(content) {
  try {
    const headers = { 'Authorization': `Bearer ${TOKEN}` };
    const formData = new FormData();
    formData.append('receiver_id', RECEIVER_ID);
    formData.append('content', content);
    if (await isDjangoServerAvailable(DJANGO_URL)) {
      await axios.post(API_URL_SEND, formData, { headers });
    }
  } catch (error) {
    console.error('Error sending message to Django:', error);
  }
}


async function receiveMessages(queueName) {
  try {
    const connection = await amqp.connect(`amqp://${RABBITMQ_HOST}`);
    const channel = await connection.createChannel();
    await channel.assertQueue(NAME_QUEUE);
    //console.log(`[*] Waiting for messages in ${NAME_QUEUE}. To exit press CTRL+C`);

    channel.consume(NAME_QUEUE, (msg) => {
      if (msg !== null) {
        const messageContent = msg.content.toString();
        sendMessage(messageContent);
        console.log(`[x] Received ${messageContent}`);
        channel.ack(msg);
      }
    });
  } catch (error) {
    console.error('Error receiving messages:', error);
  }
}

function startReceiving() {
  setTimeout(() => receiveMessages(QUEUE_NAME), 2000);
}

async function checkServerAvailability(url, headers) {
  try {
    const response = await axios.head(url, { headers, timeout: 5000 });
    return response.status === 200;
  } catch (error) {
    return false;
  }
}

async function main() {
  const headers = { 'Authorization': `Bearer ${TOKEN}` };

  while (!await isDjangoServerAvailable(DJANGO_URL)) {
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  await getQueueTokens();

  if (await isDjangoServerAvailable(DJANGO_URL)) {
    try {
      const response = await axios.get(`${API_URL_GET}${RECEIVER_ID}`, { headers });
      if (response.status === 200) {
        const messages = response.data;
        for (const message of messages) {
          const senderName = message.sender === USER_ID ? "you" : "it";
          console.log(`${senderName}: ${message.content}`);
        }
      } else {
        console.log(`Error getting messages: ${response.status} - ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error getting messages:', error);
    }
  }

  startReceiving();

  rl.on('line', (input) => {
    new MessageSender(input);
  });
}

main();
