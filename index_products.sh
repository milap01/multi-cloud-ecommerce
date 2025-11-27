cat <<EOF > index_products.sh
#!/bin/bash
echo "Indexing products..."

curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 1, "name": "iPhone 15 Pro", "price": 999.99, "description": "Titanium design, A17 Pro chip"}'
curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 2, "name": "Samsung Galaxy S24", "price": 899.99, "description": "AI features, Nightography"}'
curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 3, "name": "Sony WH-1000XM5", "price": 348.00, "description": "Noise cancelling headphones"}'
curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 4, "name": "MacBook Air M2", "price": 1199.00, "description": "Supercharged by M2"}'
curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 5, "name": "Logitech MX Master 3S", "price": 99.99, "description": "Performance wireless mouse"}'
curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 6, "name": "Kindle Paperwhite", "price": 139.99, "description": "6.8-inch display, warm light"}'
curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 7, "name": "PlayStation 5", "price": 499.99, "description": "Next-gen gaming console"}'
curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 8, "name": "Dell XPS 15", "price": 1499.00, "description": "15-inch laptop with InfinityEdge"}'
curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 9, "name": "iPad Air", "price": 599.00, "description": "Light. Bright. Full of might."}'
curl -X POST http://search.mce.svc.cluster.local:8000/search/index -H "Content-Type: application/json" -d '{"id": 10, "name": "AirPods Pro 2", "price": 249.00, "description": "Active Noise Cancellation"}'

echo "Indexing complete."
EOF