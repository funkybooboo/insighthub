import { productRepository } from '../repositories/product.repository';

export default {
    async getProduct(productid: number) {
        return productRepository.getProduct(productid);
    },
};
