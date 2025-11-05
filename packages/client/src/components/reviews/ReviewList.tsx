import StarRating from './StarRating';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from '../ui/button';
import { HiSparkles } from 'react-icons/hi';
import ReviewSkeleton from './ReviewSkeleton';
import type { GetReviewsResponse, GetSummaryResponse } from './reviewsApi';
import reviewsApi from './reviewsApi';

type Props = {
    productId: number;
};

const ReviewList = ({ productId }: Props) => {
    const summaryMutation = useMutation<GetSummaryResponse>({
        mutationFn: () => reviewsApi.summarizeReviews(productId),
    });

    const reviewsQuery = useQuery<GetReviewsResponse>({
        queryKey: ['reviews', productId],
        queryFn: () => reviewsApi.fetchReviews(productId),
    });

    if (reviewsQuery.isLoading) {
        return (
            <div className="flex flex-col gap-5">
                {[1, 2, 3].map((i) => (
                    <div key={i}>
                        <ReviewSkeleton key={i} />
                    </div>
                ))}
            </div>
        );
    }

    if (reviewsQuery.isError) {
        return (
            <p className="text-red-500">Could not get reviews. Try again!</p>
        );
    }

    if (!reviewsQuery.data?.reviews.length) {
        return null;
    }

    const currentSummary: string | undefined =
        reviewsQuery.data?.summary || summaryMutation.data?.summary;

    return (
        <div>
            <div className="mb-5">
                {currentSummary ? (
                    <p>Summary: {currentSummary}</p>
                ) : (
                    <div>
                        <Button
                            onClick={() => summaryMutation.mutate()}
                            className="cursor-pointer"
                            disabled={summaryMutation.isPending}
                        >
                            <HiSparkles />
                            Summarize
                        </Button>
                        {summaryMutation.isPending && (
                            <div className="py3">
                                <ReviewSkeleton />
                            </div>
                        )}
                        {summaryMutation.isError && (
                            <p className="text-red-500">
                                Could not summarize reviews. Try Again!
                            </p>
                        )}
                    </div>
                )}
            </div>

            <div className="flex flex-col gap-5">
                {reviewsQuery.data?.reviews.map((review) => (
                    <div key={review.id}>
                        <div className="font-semibold">{review.author}</div>
                        <div>
                            <StarRating value={review.rating} />
                        </div>
                        <p className="py-2">{review.content}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ReviewList;
