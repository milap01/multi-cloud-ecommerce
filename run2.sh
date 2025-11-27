# Create Namespaces
kubectl apply -f k8s/namespace.yaml

# Create ConfigMaps/Secrets (Update values if endpoints changed!)
kubectl apply -f k8s/configmap-common.yaml
kubectl apply -f k8s/secret-template.yaml 

# Deploy Services
kubectl apply -f k8s/product/
kubectl apply -f k8s/cart/
kubectl apply -f k8s/search/
kubectl apply -f k8s/order/
kubectl apply -f k8s/event-producer/
kubectl apply -f k8s/analytics-consumer/
kubectl apply -f k8s/stream-processor/
kubectl apply -f k8s/frontend/