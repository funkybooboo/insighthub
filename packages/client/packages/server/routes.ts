import { Router } from 'express';

import chatController from './controllers/chat.controller';
import reviewController from './controllers/review.controller';

const router = Router();

router.post('/api/chat', chatController.sendMessage);

router.get('/api/products/:id/reviews', reviewController.getReviews);
router.post(
    '/api/products/:id/reviews/summarize',
    reviewController.summerizeReviews
);

export default router;
