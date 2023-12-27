import { redis, sleepN } from './utils'
import { nanoid } from 'nanoid'
import fs from 'fs';

const pathToTextFile = require.resolve('./test.txt')
const testContent = fs.readFileSync(pathToTextFile).toString()
let current = 0;

const uuid = "E0RcOzI6EI2hW3ENcukWU"//nanoid()
async function main() {
    /*
    // 订阅者订阅一个频道
    redis.subscribe('my-channel');

    // 当订阅者收到消息时，打印消息
    redis.on('message', (channel, message) => {
        console.log(`Received the following message from ${channel}: ${message}`);
    });
    */
    console.log('uuid', uuid)
    while (true) {
        redis.publish(uuid, testContent.slice(current, current + 10))
        await sleepN(Math.random() * 10)
        current+=10;
    }
    
}


main()