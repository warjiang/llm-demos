import { useState, useRef } from 'react'
import { Box, Flex, Heading, Text, Textarea, Button, useToast } from '@chakra-ui/react'
import { SSE } from "sse";
import type { SSEvent, ReadyStateEvent } from 'sse'
import { combinePrompts, extractSSEData } from './utils';

function App() {
  const [userInput, setUserInput] = useState('')
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState("");
  const toast = useToast();
  const responseRef = useRef(response);
  const [conversationContext, setConversationContext] = useState<Array<{ role: string, content: string }>>([])

  const submitQuestionStream = async () => {
    const synthesisConversationContext = combinePrompts(conversationContext, userInput);
    setConversationContext(synthesisConversationContext);
    setIsLoading(true);
    setUserInput('');
    responseRef.current = ''


    const url = `${import.meta.env.VITE_OPENAI_BASE}/chat/completions`;
    const config = {
      model: import.meta.env.VITE_OPENAI_MODEL_NAME,
      messages: synthesisConversationContext,
      max_tokens: 1024,
      n: 1,
      temperature: 0.5,
      stream: true,
    }
    const source = new SSE(url, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${import.meta.env.VITE_OPENAI_API_KEY}`,
      },
      method: "POST",
      payload: JSON.stringify(config),
    })
    source.addEventListener('readystatechange', (e: ReadyStateEvent) => {
      console.log("ReadyState: ", e.readyState);
    })
    source.addEventListener('message', (e: SSEvent) => {
      console.log("Message: ", e.data);
      if (e.data == "[DONE]") {
        // setConversationContext((prev) => [...prev, response]);
        setIsLoading(false);
        return;
      }
      const { data, isSSEData } = extractSSEData(e.data)
      if (!isSSEData) {
        source.close()
        return
      }
      const objectsArray = data.map(item => JSON.parse(item))
      if (objectsArray && !!objectsArray[0].choices[0].delta.content) {
        responseRef.current += objectsArray[0].choices[0].delta.content
        setResponse(responseRef.current)
        setIsLoading(false)
      }
    })
    source.stream()
  }

  return (
    <>
      <Flex
        width={"100vw"}
        height={"100vh"}
        alignContent={"center"}
        justifyContent={"center"}
        bgGradient={"linear(to-b, #964dd6, #997c7e)"}
      >
        <Box
          boxShadow="dark-lg"
          maxW="2xl"
          m="auto"
          bg={"white"}
          p="20px"
          borderRadius={"md"}
        >
          <Heading mb={4}>🤖 OpenAI Completions</Heading>
          <Text mb={4}>
            This is an example of using SSE (Server-Sent Events) with React, Vite.
          </Text>
          <Textarea
            value={userInput}
            onChange={(e) => {
              setUserInput(e.target.value)
            }}
            placeholder={"Give me any sentence to complete.."}
          />
          <Button
            mt={4}
            isLoading={isLoading}
            loadingText="Fetching Data.."
            onClick={() => {
              if (!userInput) {
                toast({
                  title: "Prompt is empty",
                  description: "Please enter a prompt",
                  status: "error",
                  duration: 2000,
                  isClosable: true,
                });
                return
              }
              submitQuestionStream()
            }}
            colorScheme={"purple"}
          >
            Ask
          </Button>
          <Button mt={4} mx={4} onClick={() => {
            setUserInput("");
            setResponse("");
          }}>
            Clear
          </Button>

          {response === "" ? null : (
            <Box mt={4}>
              <Heading fontSize={"md"}>Response</Heading>
              <Text mt={2}>{response}</Text>
            </Box>
          )}
        </Box>
      </Flex>
    </>
  )
}

export default App
