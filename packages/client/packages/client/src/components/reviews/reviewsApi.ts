import axios from 'axios';
import type { Rating } from './StarRating';

export type Review = {
    id: number;
    author: string;
    content: string;
    rating: Rating;
    createdAt: string;
};

export type GetReviewsResponse = {
    summary: string | null;
    reviews: Review[];
};

export type GetSummaryResponse = {
    summary: string;
};

export default {
    async summarizeReviews(productId: number): Promise<GetSummaryResponse> {
        const { data } = await axios.post<GetSummaryResponse>(
            `/api/products/${productId}/reviews/summarize`
        );
        return data;
    },

    async fetchReviews(productId: number): Promise<GetReviewsResponse> {
        const { data } = await axios.get<GetReviewsResponse>(
            `/api/products/${productId}/reviews`
        );
        return data;
    },
};
