cat <<EOF > init_db.sql
-- 1. Create Products Table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Populate Product Catalog
INSERT INTO products (name, price, description) VALUES 
('iPhone 15 Pro', 999.99, 'Titanium design, A17 Pro chip, 48MP Main camera.'),
('Samsung Galaxy S24', 899.99, 'AI features, Nightography, High resolution photo.'),
('Sony WH-1000XM5', 348.00, 'Noise cancelling wireless headphones.'),
('MacBook Air M2', 1199.00, 'Supercharged by M2. 13.6-inch Liquid Retina display.'),
('Logitech MX Master 3S', 99.99, 'Performance wireless mouse, 8K DPI.'),
('Kindle Paperwhite', 139.99, '6.8-inch display, warm light, 10 weeks battery.'),
('PlayStation 5', 499.99, 'Next-gen gaming console with 4K support.'),
('Dell XPS 15', 1499.00, '15-inch laptop with InfinityEdge display.'),
('iPad Air', 599.00, 'Light. Bright. Full of might.'),
('AirPods Pro 2', 249.00, 'Active Noise Cancellation and Transparency mode.');
EOF