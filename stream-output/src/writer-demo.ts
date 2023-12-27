import { MockGPTStream } from './utils';
import { Typewriter } from './typewriter';

async function main() {
    const writer = new Typewriter(
        (str) => {
            process.stdout.write(str)
        }
    )
    writer.start()
    const g = new MockGPTStream('./test.txt')
    for (const chunk of g) {
        if(chunk) {
            // console.log("chunk", chunk)
            writer.add(chunk)
        }
    }
}

main()
    .catch(err => {
        console.error(err);
        process.exit(1);
    })
    .finally(() => {
        console.log('finish')
    })