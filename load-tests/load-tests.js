import http from 'k6/http';
import { check, sleep } from 'k6';

// Configuration for the load test
export const options = {
  stages: [
    { duration: '30s', target: 50 },  // Ramp up to 50 users
    { duration: '2m', target: 200 }, // Stay at 200 users (generate load)
    { duration: '30s', target: 0 },   // Ramp down
  ],
};

export default function () {
  // Replace with your actual Frontend LoadBalancer URL after deployment
  // e.g., 'http://a1b2c3d4...us-east-1.elb.amazonaws.com'
  const BASE_URL = "http://a710c722c54fe438b953bb18524da56a-1777388317.us-east-1.elb.amazonaws.com";

  // 1. View Products
  let res = http.get(`${BASE_URL}/products`);
  check(res, { 'status was 200': (r) => r.status == 200 });

  // 2. Add to Cart (simulate user activity)
  const payload = JSON.stringify({
    userId: 'user-' + Math.floor(Math.random() * 1000),
    productId: 'prod-' + Math.floor(Math.random() * 50),
    quantity: 1
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  let cartRes = http.post(`${BASE_URL}/cart/add`, payload, params);
  check(cartRes, { 'status was 200': (r) => r.status == 200 });

  sleep(1);
}