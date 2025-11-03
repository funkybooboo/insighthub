import conversationRepository from '../repositories/conversation.repository';
import instructions from '../prompts/dwight_chatbot/instructions.txt';
import llmClient from '../llm/client';

export type ChatResponse = {
    id: string;
    message: string;
};

export default {
    async sendMessage(
        prompt: string,
        conversationId: string
    ): Promise<ChatResponse> {
        const { text: message, id } = await llmClient.generateText({
            instructions,
            prompt,
            temperature: 0.2,
            maxTokens: 100,
            previousResponseId:
                conversationRepository.getLastResponseId(conversationId),
        });

        conversationRepository.setLastResponseId(conversationId, id);

        return {
            id: id,
            message,
        };
    },
};
