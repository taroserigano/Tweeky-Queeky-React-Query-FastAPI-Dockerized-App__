"""Quick API Verification Test - All Critical Endpoints"""
import httpx
import asyncio

BASE_URL = "http://127.0.0.1:5000"


async def test_all_apis():
    """Test all critical API endpoints"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        cookies = {}
        results = []
        
        def log(test_name, passed, details=""):
            results.append((test_name, passed, details))
            status = "✅" if passed else "❌"
            print(f"{status} {test_name}" + (f": {details}" if details else ""))
        
        # 1. Health Check
        try:
            r = await client.get("/api/health")
            log("Health Check", r.status_code == 200)
        except Exception as e:
            log("Health Check", False, str(e))
        
        # 2. Register User
        try:
            r = await client.post("/api/users", json={
                "name": "Test User",
                "email": f"test{asyncio.get_event_loop().time()}@test.com",
                "password": "test123"
            })
            log("Register User", r.status_code == 201)
        except Exception as e:
            log("Register User", False, str(e))
        
        # 3. Login Admin
        try:
            r = await client.post("/api/users/auth", json={
                "email": "admin@email.com",
                "password": "123456"
            })
            log("Login Admin", r.status_code == 200)
            if r.status_code == 200:
                cookies.update(r.cookies)
        except Exception as e:
            log("Login Admin", False, str(e))
        
        # 4. Get Profile
        try:
            r = await client.get("/api/users/profile", cookies=cookies)
            log("Get Profile", r.status_code == 200)
        except Exception as e:
            log("Get Profile", False, str(e))
        
        # 5. Update Profile
        try:
            r = await client.put("/api/users/profile", json={
                "name": "Admin User",
                "email": "admin@email.com"
            }, cookies=cookies)
            log("Update Profile", r.status_code == 200)
        except Exception as e:
            log("Update Profile", False, str(e))
        
        # 6. Get All Products
        try:
            r = await client.get("/api/products")
            log("Get All Products", r.status_code == 200)
            product_id = r.json()["products"][0]["_id"] if r.status_code == 200 else None
        except Exception as e:
            log("Get All Products", False, str(e))
            product_id = None
        
        # 7. Get Product by ID
        if product_id:
            try:
                r = await client.get(f"/api/products/{product_id}")
                log("Get Product by ID", r.status_code == 200)
            except Exception as e:
                log("Get Product by ID", False, str(e))
        
        # 8. Get Top Products
        try:
            r = await client.get("/api/products/top")
            log("Get Top Products", r.status_code == 200)
        except Exception as e:
            log("Get Top Products", False, str(e))
        
        # 9. Search Products
        try:
            r = await client.get("/api/products?keyword=apple")
            log("Search Products", r.status_code == 200)
        except Exception as e:
            log("Search Products", False, str(e))
        
        # 10. Create Product Review
        if product_id:
            try:
                r = await client.post(f"/api/products/{product_id}/reviews", json={
                    "rating": 5,
                    "comment": "Great product!"
                }, cookies=cookies)
                log("Create Product Review", r.status_code in [201, 400])
            except Exception as e:
                log("Create Product Review", False, str(e))
        
        # 11. Get All Users (Admin)
        try:
            r = await client.get("/api/users", cookies=cookies)
            log("Get All Users (Admin)", r.status_code == 200)
            user_id = r.json()[0]["_id"] if r.status_code == 200 else None
        except Exception as e:
            log("Get All Users (Admin)", False, str(e))
            user_id = None
        
        # 12. Get User by ID (Admin)
        if user_id:
            try:
                r = await client.get(f"/api/users/{user_id}", cookies=cookies)
                log("Get User by ID (Admin)", r.status_code == 200)
            except Exception as e:
                log("Get User by ID (Admin)", False, str(e))
        
        # 13. Update User (Admin)
        if user_id:
            try:
                r = await client.put(f"/api/users/{user_id}", json={
                    "name": "Admin User",
                    "email": "admin@email.com",
                    "isAdmin": True
                }, cookies=cookies)
                log("Update User (Admin)", r.status_code == 200)
            except Exception as e:
                log("Update User (Admin)", False, str(e))
        
        # 14. Create Product (Admin)
        try:
            r = await client.post("/api/products", json={
                "name": "Test Product",
                "price": 99.99,
                "brand": "Test",
                "category": "Test",
                "countInStock": 10,
                "description": "Test"
            }, cookies=cookies)
            log("Create Product (Admin)", r.status_code == 201)
            new_product_id = r.json()["_id"] if r.status_code == 201 else None
        except Exception as e:
            log("Create Product (Admin)", False, str(e))
            new_product_id = None
        
        # 15. Update Product (Admin)
        if new_product_id:
            try:
                r = await client.put(f"/api/products/{new_product_id}", json={
                    "name": "Test Product Updated",
                    "price": 149.99,
                    "brand": "Test",
                    "category": "Test",
                    "countInStock": 15,
                    "description": "Updated"
                }, cookies=cookies)
                log("Update Product (Admin)", r.status_code == 200)
            except Exception as e:
                log("Update Product (Admin)", False, str(e))
        
        # 16. Create Order
        if product_id:
            try:
                r = await client.post("/api/orders", json={
                    "orderItems": [{
                        "name": "Test Product",
                        "qty": 1,
                        "image": "/test.jpg",
                        "price": 99.99,
                        "product": product_id
                    }],
                    "shippingAddress": {
                        "address": "123 Test St",
                        "city": "Test City",
                        "postalCode": "12345",
                        "country": "Test Country"
                    },
                    "paymentMethod": "PayPal"
                }, cookies=cookies)
                log("Create Order", r.status_code == 201, r.text if r.status_code != 201 else "")
                order_id = r.json().get("_id") if r.status_code == 201 else None
            except Exception as e:
                log("Create Order", False, str(e))
                order_id = None
        
        # 17. Get My Orders
        try:
            r = await client.get("/api/orders/mine", cookies=cookies)
            log("Get My Orders", r.status_code == 200)
            if not order_id and r.status_code == 200 and len(r.json()) > 0:
                order_id = r.json()[0]["_id"]
        except Exception as e:
            log("Get My Orders", False, str(e))
        
        # 18. Get Order by ID
        if order_id:
            try:
                r = await client.get(f"/api/orders/{order_id}", cookies=cookies)
                log("Get Order by ID", r.status_code == 200)
            except Exception as e:
                log("Get Order by ID", False, str(e))
        
        # 19. Get All Orders (Admin)
        try:
            r = await client.get("/api/orders", cookies=cookies)
            log("Get All Orders (Admin)", r.status_code == 200)
        except Exception as e:
            log("Get All Orders (Admin)", False, str(e))
        
        # 20. Update Order to Delivered (Admin)
        if order_id:
            try:
                r = await client.put(f"/api/orders/{order_id}/deliver", cookies=cookies)
                log("Update Order to Delivered", r.status_code == 200)
            except Exception as e:
                log("Update Order to Delivered", False, str(e))
        
        # 21. Delete Product (Admin)
        if new_product_id:
            try:
                r = await client.delete(f"/api/products/{new_product_id}", cookies=cookies)
                log("Delete Product (Admin)", r.status_code == 200)
            except Exception as e:
                log("Delete Product (Admin)", False, str(e))
        
        # 22. Logout
        try:
            r = await client.post("/api/users/logout", cookies=cookies)
            log("Logout", r.status_code == 200)
        except Exception as e:
            log("Logout", False, str(e))
        
        # 23. Unauthorized Access Test
        try:
            r = await client.get("/api/users/profile")  # No cookies
            log("Unauthorized Access Blocked", r.status_code == 401)
        except Exception as e:
            log("Unauthorized Access Blocked", False, str(e))
        
        # Summary
        passed = sum(1 for _, p, _ in results if p)
        total = len(results)
        print(f"\n{'='*60}")
        print(f"RESULTS: {passed}/{total} tests passed ({int(passed/total*100)}%)")
        print(f"{'='*60}")
        
        return passed == total


if __name__ == "__main__":
    success = asyncio.run(test_all_apis())
    exit(0 if success else 1)
