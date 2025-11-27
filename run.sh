# 1. Login to ECR (Get the registry URL from terraform output or AWS console)
# Example Account ID: 343938549827 (Check your terraform output for the exact ID)
export AWS_ACCOUNT_ID=343938549827
export REGION=us-east-1
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# 2. Build and Push All Services (Cross-compiling for AMD64/x86_64)

# Frontend
cd services/frontend
docker build --platform linux/amd64 -t frontend-repo-mce-2 .
docker tag frontend-repo-mce-2:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/frontend-repo-mce-2:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/frontend-repo-mce-2:latest
cd ../..

# Product
cd services/product
docker build --platform linux/amd64 -t product-repo-mce-2 .
docker tag product-repo-mce-2:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/product-repo-mce-2:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/product-repo-mce-2:latest
cd ../..

# Cart
cd services/cart
docker build --platform linux/amd64 -t cart-repo-mce-2 .
docker tag cart-repo-mce-2:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cart-repo-mce-2:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/cart-repo-mce-2:latest
cd ../..

# Order
cd services/order
docker build --platform linux/amd64 -t order-repo-mce-2 .
docker tag order-repo-mce-2:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/order-repo-mce-2:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/order-repo-mce-2:latest
cd ../..

# Search
cd services/search
docker build --platform linux/amd64 -t search-repo-mce-2 .
docker tag search-repo-mce-2:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/search-repo-mce-2:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/search-repo-mce-2:latest
cd ../..

# Events Producer
cd services/event-producer
docker build --platform linux/amd64 -t events-producer-repo-mce-2 .
docker tag events-producer-repo-mce-2:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/events-producer-repo-mce-2:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/events-producer-repo-mce-2:latest
cd ../..

# Analytics Consumer
cd services/analytics-consumer
docker build --platform linux/amd64 -t analytics-consumer-repo-mce-2 .
docker tag analytics-consumer-repo-mce-2:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/analytics-consumer-repo-mce-2:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/analytics-consumer-repo-mce-2:latest
cd ../..

# Stream Processor (Flink)
cd services/stream-processor
docker build --platform linux/amd64 -t stream-processor-repo-mce-2 .
docker tag stream-processor-repo-mce-2:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/stream-processor-repo-mce-2:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/stream-processor-repo-mce-2:latest
cd ../..