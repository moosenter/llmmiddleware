# LLM Middleware
An LLM middleware app is a software layer that sits between large language models (LLMs) like OpenAI's GPT, Anthropic's Claude, or Google's PaLM and the end-user applications or systems that utilize them. Its purpose is to manage, enhance, and customize interactions with the LLM to better align the model's outputs with specific business or technical needs.

## How to implement this app locally, (be free port: 8000 and 3000)

1. create .env file, input LLM provider API keys
```
OPENAI_API_KEY=XXX
GROQ_API_KEY=XXX
```
2. build images using docker-compose
````
docker-compose build
````
3. run application
````
docker-compose up -d
````
4. open `http://localhost:3000`

## RAG database implementation is under maintenance

## Now only support LLAMA