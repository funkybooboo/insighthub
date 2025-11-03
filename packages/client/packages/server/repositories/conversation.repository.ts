const conversations = new Map<string, string>();

export default {
    getLastResponseId(conversationId: string): string | undefined {
        return conversations.get(conversationId);
    },
    setLastResponseId(conversationId: string, lastResponseId: string) {
        conversations.set(conversationId, lastResponseId);
    },
};
