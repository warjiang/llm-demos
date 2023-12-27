import { Redis } from 'ioredis'
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';
dotenv.config();

export const redis = new Redis({
    host: process.env.REDIS_HOST,
    port: parseInt(process.env.REDIS_PORT || '6379', 10),
    password: process.env.REDIS_PASSWORD,
});

export function sleepN(n: number) {
    return new Promise((resolve) => {
        setTimeout(resolve, n * 1000)
    })
}

export function randomN(n: number) {
    // 生成1~n的随机数
    return Math.floor(Math.random() * n + 1)
}

export class MockGPTStream {
    private content: string;
    private idx: number = 0;
    constructor(txtPath: string) {
        let absoluteTxtPath = txtPath;
        if (!path.isAbsolute(txtPath)) {
            absoluteTxtPath = require.resolve(txtPath)
        }
        this.content = fs.readFileSync(absoluteTxtPath, 'utf-8').toString()
    }

    [Symbol.iterator]() {
        return {
            next: () => {
                if (this.idx < this.content.length) {
                    let n = randomN(200);
                    if ((this.idx + n - 1) >= (this.content.length - 1)) {
                        // [idx, content.length - idx -1]
                        n = this.content.length - this.idx;
                    }
                    const chunk = this.content.slice(this.idx, this.idx + n);
                    this.idx = this.idx + n
                    return { value: chunk, done: false };
                } else {
                    return { done: true };
                }
            }
        };
    }
}