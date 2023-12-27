import { extractSSEData } from '../src/utils.ts'
const data = `Message:  {"id":"chatcmpl-8aKjX8qGn9lpXzxlnn8gPeivfI9hJ","object":"chat.completion.chunk","created":1703670199,"model":"gpt-35-turbo","choices":[{"index":0,"delta":{"content":"么"},"finish_reason":null,"content_filter_results":{"hate":{"filtered":false},"self_harm":{"filtered":false},"sexual":{"filtered":false},"violence":{"filtered":false}}}]}`



const ret = extractSSEData(data)
console.log(ret)