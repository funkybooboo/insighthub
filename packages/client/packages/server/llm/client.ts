import OpenAI from 'openai';
import { InferenceClient } from "@huggingface/inference";
import { Ollama } from 'ollama';

const defaultModel = process.env.CHATBOT_MODEL;

const openaiClient = new OpenAI({
    apiKey: process.env.CHATBOT_OPENAI_API_KEY,
});
const inferenceClient = new InferenceClient(process.env.CHATBOT_HF_TOKEN);
const ollamaClient = new Ollama();

type GenerateTextOptions = {
    model?: string;
    instructions?: string;
    prompt: string;
    temperature?: number;
    maxTokens?: number;
    previousResponseId?: string;
};

type GenerateTextResponse = {
    text: string;
    id: string;
};

type GenerateTextFunction = (options: GenerateTextOptions) => Promise<GenerateTextResponse>;

const openaiGenerateText: GenerateTextFunction = async (options: GenerateTextOptions) => {
    try {
        const response = await openaiClient.responses.create({
            model: options.model,
            instructions: options.instructions || '',
            input: options.prompt,
            temperature: options.temperature,
            max_output_tokens: options.maxTokens,
            previous_response_id: options.previousResponseId,
        });

        return { text: response.output_text, id: response.id };
    } catch (error) {
        console.error("Error generating text with OpenAI:", error);
        throw error;
    }
};

const inferenceGenerateText: GenerateTextFunction = async (options: GenerateTextOptions) => {
    try {
        const chatCompletion = await inferenceClient.chatCompletion({
            provider: "fireworks-ai",
            model: "meta-llama/Llama-3.1-8B-Instruct",
            messages: [
                {
                    role: 'system',
                    content: options.instructions || '',
                },
                {
                    role: "user",
                    content: options.prompt,
                },
            ],
        });

        if (chatCompletion.choices.length === 0) {
            return { text: '', id: '' };
        } else {
            const choice = chatCompletion.choices[0];
            const content = choice?.message?.content ?? '';
            const id = chatCompletion.id ?? '';

            return { text: content, id: id };
        }
    } catch (error) {
        console.error("Error generating text with Meta Llama:", error);
        throw error;
    }
};

const ollamaGenerateText: GenerateTextFunction = async (options: GenerateTextOptions) => {
    const response = await ollamaClient.chat({
        model: 'tinyllama',
        messages: [
            {
                role: 'system',
                content: options.instructions || '',
            },
            {
                role: "user",
                content: options.prompt,
            },
        ],
    });

    return { text: response.message.content, id: crypto.randomUUID() };
};

export default {
    async generateText(options: GenerateTextOptions): Promise<GenerateTextResponse> {
        if(!options.model) {
            options.model = defaultModel;
        }

        if (!options.temperature) {
            options.temperature = 0.2;
        }

        if (!options.maxTokens) {
            options.maxTokens = 300;
        }

        const modifiedPrompt = `${options.prompt}\n\nYou have a max of ${options.maxTokens} tokens to respond with.`;
        options.prompt = modifiedPrompt;

        if (options.model === 'meta-llama/Llama-3.1-8B-Instruct') {
            return inferenceGenerateText(options);
        } else if (options.model === 'tinyllama') {
            return ollamaGenerateText(options);
        } else {
            return openaiGenerateText(options);
        }
    },
};
