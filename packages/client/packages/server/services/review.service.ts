import type { Review } from '../generated/prisma';
import reviewRepository from '../repositories/review.repository';
import llmClient from '../llm/client';
import instructions from '../prompts/summerize_reviews/instructions.txt';

export default {
    async getReviews(productId: number): Promise<Review[]> {
        return reviewRepository.getReviews(productId);
    },

    async summarizeReviews(productId: number): Promise<string> {
        const existingSummary =
            await reviewRepository.getReviewSummary(productId);
        if (existingSummary) {
            return existingSummary;
        }

        const reviews = await reviewRepository.getReviews(productId, 10);
        const joinedReivews = reviews.map((r) => r.content).join('\n\n');

        const { text: summary } = await llmClient.generateText({ instructions, prompt: joinedReivews });

        await reviewRepository.storeReviewSummary(productId, summary);

        return summary;
    },

    async getReviewSummary(productId: number) {
        return reviewRepository.getReviewSummary(productId);
    },
};
