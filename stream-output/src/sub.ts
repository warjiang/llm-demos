import { redis } from './utils'


async function main() {
    // 订阅者订阅一个频道
    redis.subscribe('E0RcOzI6EI2hW3ENcukWU');
    // 当订阅者收到消息时，打印消息
    redis.on('message', (channel, message) => {
        console.log(`Received the following message from ${channel}: ${message}`);
    });

}


main()