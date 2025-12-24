"""
Complete End-to-End Testing Suite for ALL API Endpoints
Tests every single API endpoint with realistic scenarios
"""
import httpx
import asyncio
from typing import Dict, List

BASE_URL = "http://127.0.0.1:5000"


class E2ETestSuite:
    def __init__(self):
        self.client = None
        self.cookies: Dict[str, str] = {}
        self.results: List[tuple] = []
        self.test_data = {
            "admin_id": None,
            "user_id": None,
            "product_id": None,
            "new_product_id": None,
            "order_id": None,
        }
    
    async def setup(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=60.0)
    
    async def teardown(self):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
    
    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.results.append((name, passed, details))
        status = "✅" if passed else "❌"
        msg = f"{status} {name}"
        if details:
            msg += f" - {details}"
        print(msg)
    
    async def test_health_check(self):
        """Test: Health check endpoint"""
        try:
            r = await self.client.get("/api/health")
            self.log_test("Health Check", r.status_code == 200)
            return r.status_code == 200
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    async def test_register_user(self):
        """Test: Register new user"""
        try:
            r = await self.client.post("/api/users", json={
                "name": "E2E Test User",
                "email": f"e2etest_{int(asyncio.get_event_loop().time())}@test.com",
                "password": "testpass123"
            })
            if r.status_code == 201:
                data = r.json()
                self.test_data["user_id"] = data.get("_id")
                self.log_test("Register User", True, f"User ID: {self.test_data['user_id']}")
                return True
            else:
                self.log_test("Register User", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Register User", False, str(e))
            return False
    
    async def test_login_wrong_credentials(self):
        """Test: Login with invalid credentials should fail"""
        try:
            r = await self.client.post("/api/users/auth", json={
                "email": "wrong@email.com",
                "password": "wrongpass"
            })
            passed = r.status_code == 401
            self.log_test("Login Wrong Credentials (Should Fail)", passed)
            return passed
        except Exception as e:
            self.log_test("Login Wrong Credentials", False, str(e))
            return False
    
    async def test_login_admin(self):
        """Test: Login as admin"""
        try:
            r = await self.client.post("/api/users/auth", json={
                "email": "admin@email.com",
                "password": "123456"
            })
            if r.status_code == 200:
                self.cookies.update(dict(r.cookies))
                data = r.json()
                self.test_data["admin_id"] = data.get("_id")
                is_admin = data.get("isAdmin", False)
                self.log_test("Login Admin", is_admin, f"Admin ID: {self.test_data['admin_id']}")
                return is_admin
            else:
                self.log_test("Login Admin", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Login Admin", False, str(e))
            return False
    
    async def test_get_profile(self):
        """Test: Get user profile (requires auth)"""
        try:
            r = await self.client.get("/api/users/profile", cookies=self.cookies)
            passed = r.status_code == 200
            if passed:
                data = r.json()
                self.log_test("Get Profile", True, f"Name: {data.get('name')}")
            else:
                self.log_test("Get Profile", False, f"Status: {r.status_code}")
            return passed
        except Exception as e:
            self.log_test("Get Profile", False, str(e))
            return False
    
    async def test_update_profile(self):
        """Test: Update user profile"""
        try:
            r = await self.client.put("/api/users/profile", json={
                "name": "Admin User Updated E2E",
                "email": "admin@email.com"
            }, cookies=self.cookies)
            passed = r.status_code == 200
            self.log_test("Update Profile", passed)
            return passed
        except Exception as e:
            self.log_test("Update Profile", False, str(e))
            return False
    
    async def test_get_all_products(self):
        """Test: Get all products with pagination"""
        try:
            r = await self.client.get("/api/products?pageNumber=1")
            if r.status_code == 200:
                data = r.json()
                products = data.get("products", [])
                if products:
                    self.test_data["product_id"] = products[0]["_id"]
                self.log_test("Get All Products", True, f"Count: {len(products)}, Pages: {data.get('pages')}")
                return True
            else:
                self.log_test("Get All Products", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Products", False, str(e))
            return False
    
    async def test_get_product_by_id(self):
        """Test: Get specific product"""
        if not self.test_data["product_id"]:
            self.log_test("Get Product By ID", False, "No product ID available")
            return False
        try:
            r = await self.client.get(f"/api/products/{self.test_data['product_id']}")
            if r.status_code == 200:
                data = r.json()
                self.log_test("Get Product By ID", True, f"Name: {data.get('name')}")
                return True
            else:
                self.log_test("Get Product By ID", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Product By ID", False, str(e))
            return False
    
    async def test_get_top_products(self):
        """Test: Get top rated products"""
        try:
            r = await self.client.get("/api/products/top")
            if r.status_code == 200:
                data = r.json()
                self.log_test("Get Top Products", True, f"Count: {len(data)}")
                return True
            else:
                self.log_test("Get Top Products", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Top Products", False, str(e))
            return False
    
    async def test_search_products(self):
        """Test: Search products by keyword"""
        try:
            r = await self.client.get("/api/products?keyword=apple")
            if r.status_code == 200:
                data = r.json()
                count = len(data.get("products", []))
                self.log_test("Search Products", True, f"Found: {count}")
                return True
            else:
                self.log_test("Search Products", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Search Products", False, str(e))
            return False
    
    async def test_create_product_review(self):
        """Test: Create product review"""
        if not self.test_data["product_id"]:
            self.log_test("Create Product Review", False, "No product ID")
            return False
        try:
            r = await self.client.post(
                f"/api/products/{self.test_data['product_id']}/reviews",
                json={"rating": 5, "comment": "E2E Test Review - Excellent!"},
                cookies=self.cookies
            )
            # 201 = created, 400 = already reviewed (both acceptable)
            passed = r.status_code in [201, 400]
            status_msg = "Created" if r.status_code == 201 else "Already reviewed"
            self.log_test("Create Product Review", passed, status_msg)
            return passed
        except Exception as e:
            self.log_test("Create Product Review", False, str(e))
            return False
    
    async def test_admin_get_all_users(self):
        """Test: Admin get all users"""
        try:
            r = await self.client.get("/api/users", cookies=self.cookies)
            if r.status_code == 200:
                data = r.json()
                self.log_test("Admin Get All Users", True, f"Count: {len(data)}")
                return True
            else:
                self.log_test("Admin Get All Users", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Get All Users", False, str(e))
            return False
    
    async def test_admin_get_user_by_id(self):
        """Test: Admin get user by ID"""
        if not self.test_data["admin_id"]:
            self.log_test("Admin Get User By ID", False, "No user ID")
            return False
        try:
            r = await self.client.get(f"/api/users/{self.test_data['admin_id']}", cookies=self.cookies)
            if r.status_code == 200:
                data = r.json()
                self.log_test("Admin Get User By ID", True, f"Name: {data.get('name')}")
                return True
            else:
                self.log_test("Admin Get User By ID", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Get User By ID", False, str(e))
            return False
    
    async def test_admin_update_user(self):
        """Test: Admin update user"""
        if not self.test_data["admin_id"]:
            self.log_test("Admin Update User", False, "No user ID")
            return False
        try:
            r = await self.client.put(f"/api/users/{self.test_data['admin_id']}", json={
                "name": "Admin User",
                "email": "admin@email.com",
                "isAdmin": True
            }, cookies=self.cookies)
            passed = r.status_code == 200
            self.log_test("Admin Update User", passed)
            return passed
        except Exception as e:
            self.log_test("Admin Update User", False, str(e))
            return False
    
    async def test_admin_create_product(self):
        """Test: Admin create new product"""
        try:
            r = await self.client.post("/api/products", json={
                "name": "E2E Test Product",
                "price": 99.99,
                "brand": "E2E Brand",
                "category": "Electronics",
                "countInStock": 10,
                "description": "E2E Test Description"
            }, cookies=self.cookies)
            if r.status_code == 201:
                data = r.json()
                self.test_data["new_product_id"] = data.get("_id")
                self.log_test("Admin Create Product", True, f"ID: {self.test_data['new_product_id']}")
                return True
            else:
                self.log_test("Admin Create Product", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Create Product", False, str(e))
            return False
    
    async def test_admin_update_product(self):
        """Test: Admin update product"""
        if not self.test_data["new_product_id"]:
            self.log_test("Admin Update Product", False, "No product ID")
            return False
        try:
            r = await self.client.put(f"/api/products/{self.test_data['new_product_id']}", json={
                "name": "E2E Test Product UPDATED",
                "price": 149.99,
                "brand": "E2E Brand",
                "category": "Electronics",
                "countInStock": 20,
                "description": "Updated description"
            }, cookies=self.cookies)
            passed = r.status_code == 200
            self.log_test("Admin Update Product", passed)
            return passed
        except Exception as e:
            self.log_test("Admin Update Product", False, str(e))
            return False
    
    async def test_create_order(self):
        """Test: Create order (realistic flow)"""
        if not self.test_data["product_id"]:
            self.log_test("Create Order", False, "No product ID")
            return False
        try:
            # Get product details first (like real app does)
            prod_r = await self.client.get(f"/api/products/{self.test_data['product_id']}")
            if prod_r.status_code != 200:
                self.log_test("Create Order", False, "Failed to get product")
                return False
            
            product = prod_r.json()
            
            r = await self.client.post("/api/orders", json={
                "orderItems": [{
                    "name": product["name"],
                    "qty": 2,
                    "image": product.get("image", "/images/test.jpg"),
                    "price": product["price"],
                    "product": self.test_data["product_id"]
                }],
                "shippingAddress": {
                    "address": "2409 Town Lake Cir",
                    "city": "AUSTIN",
                    "postalCode": "78741",
                    "country": "United States"
                },
                "paymentMethod": "PayPal"
            }, cookies=self.cookies)
            
            if r.status_code == 201:
                data = r.json()
                self.test_data["order_id"] = data.get("_id")
                total = data.get("totalPrice", 0)
                self.log_test("Create Order", True, f"ID: {self.test_data['order_id']}, Total: ${total}")
                return True
            else:
                self.log_test("Create Order", False, f"Status: {r.status_code}, Response: {r.text}")
                return False
        except Exception as e:
            self.log_test("Create Order", False, str(e))
            return False
    
    async def test_get_my_orders(self):
        """Test: Get logged-in user's orders"""
        try:
            r = await self.client.get("/api/orders/mine", cookies=self.cookies)
            if r.status_code == 200:
                data = r.json()
                self.log_test("Get My Orders", True, f"Count: {len(data)}")
                # If we don't have order_id yet, grab first order
                if not self.test_data["order_id"] and data:
                    self.test_data["order_id"] = data[0]["_id"]
                return True
            else:
                self.log_test("Get My Orders", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Get My Orders", False, str(e))
            return False
    
    async def test_get_order_by_id(self):
        """Test: Get specific order"""
        if not self.test_data["order_id"]:
            self.log_test("Get Order By ID", False, "No order ID")
            return False
        try:
            r = await self.client.get(f"/api/orders/{self.test_data['order_id']}", cookies=self.cookies)
            if r.status_code == 200:
                data = r.json()
                self.log_test("Get Order By ID", True, f"Total: ${data.get('totalPrice')}")
                return True
            else:
                self.log_test("Get Order By ID", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Order By ID", False, str(e))
            return False
    
    async def test_admin_get_all_orders(self):
        """Test: Admin get all orders"""
        try:
            r = await self.client.get("/api/orders", cookies=self.cookies)
            if r.status_code == 200:
                data = r.json()
                self.log_test("Admin Get All Orders", True, f"Count: {len(data)}")
                return True
            else:
                self.log_test("Admin Get All Orders", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Get All Orders", False, str(e))
            return False
    
    async def test_admin_update_order_delivered(self):
        """Test: Admin mark order as delivered"""
        if not self.test_data["order_id"]:
            self.log_test("Admin Update Order Delivered", False, "No order ID")
            return False
        try:
            r = await self.client.put(f"/api/orders/{self.test_data['order_id']}/deliver", cookies=self.cookies)
            if r.status_code == 200:
                data = r.json()
                is_delivered = data.get("isDelivered", False)
                self.log_test("Admin Update Order Delivered", is_delivered)
                return is_delivered
            else:
                self.log_test("Admin Update Order Delivered", False, f"Status: {r.status_code}")
                return False
        except Exception as e:
            self.log_test("Admin Update Order Delivered", False, str(e))
            return False
    
    async def test_get_paypal_config(self):
        """Test: Get PayPal client ID"""
        try:
            r = await self.client.get("/api/config/paypal")
            passed = r.status_code == 200
            if passed:
                data = r.json()
                self.log_test("Get PayPal Config", True, f"Client ID exists: {bool(data.get('clientId'))}")
            else:
                self.log_test("Get PayPal Config", False, f"Status: {r.status_code}")
            return passed
        except Exception as e:
            self.log_test("Get PayPal Config", False, str(e))
            return False
    
    async def test_admin_delete_product(self):
        """Test: Admin delete product"""
        if not self.test_data["new_product_id"]:
            self.log_test("Admin Delete Product", False, "No product ID")
            return False
        try:
            r = await self.client.delete(f"/api/products/{self.test_data['new_product_id']}", cookies=self.cookies)
            passed = r.status_code == 200
            self.log_test("Admin Delete Product", passed)
            return passed
        except Exception as e:
            self.log_test("Admin Delete Product", False, str(e))
            return False
    
    async def test_logout(self):
        """Test: Logout user"""
        try:
            r = await self.client.post("/api/users/logout", cookies=self.cookies)
            passed = r.status_code == 200
            if passed:
                self.cookies.clear()
            self.log_test("Logout", passed)
            return passed
        except Exception as e:
            self.log_test("Logout", False, str(e))
            return False
    
    async def test_unauthorized_access(self):
        """Test: Unauthorized access should be blocked"""
        try:
            r = await self.client.get("/api/users/profile")  # No cookies
            passed = r.status_code == 401
            self.log_test("Unauthorized Access Blocked", passed)
            return passed
        except Exception as e:
            self.log_test("Unauthorized Access Blocked", False, str(e))
            return False
    
    def print_summary(self):
        """Print test summary"""
        passed = sum(1 for _, p, _ in self.results if p)
        failed = len(self.results) - passed
        percentage = int((passed / len(self.results)) * 100) if self.results else 0
        
        print("\n" + "="*70)
        print(f"END-TO-END TEST RESULTS")
        print("="*70)
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {percentage}%")
        print("="*70)
        
        if failed > 0:
            print("\nFailed Tests:")
            for name, passed, details in self.results:
                if not passed:
                    print(f"  ❌ {name}" + (f": {details}" if details else ""))
        
        return passed == len(self.results)


async def run_e2e_tests():
    """Run complete end-to-end test suite"""
    suite = E2ETestSuite()
    
    print("="*70)
    print("🚀 COMPREHENSIVE END-TO-END API TEST SUITE")
    print("="*70)
    print()
    
    await suite.setup()
    
    try:
        # Run all tests in sequence
        await suite.test_health_check()
        await suite.test_register_user()
        await suite.test_login_wrong_credentials()
        await suite.test_login_admin()
        await suite.test_get_profile()
        await suite.test_update_profile()
        await suite.test_get_all_products()
        await suite.test_get_product_by_id()
        await suite.test_get_top_products()
        await suite.test_search_products()
        await suite.test_create_product_review()
        await suite.test_admin_get_all_users()
        await suite.test_admin_get_user_by_id()
        await suite.test_admin_update_user()
        await suite.test_admin_create_product()
        await suite.test_admin_update_product()
        await suite.test_create_order()
        await suite.test_get_my_orders()
        await suite.test_get_order_by_id()
        await suite.test_admin_get_all_orders()
        await suite.test_admin_update_order_delivered()
        await suite.test_get_paypal_config()
        await suite.test_admin_delete_product()
        await suite.test_logout()
        await suite.test_unauthorized_access()
        
        return suite.print_summary()
    
    finally:
        await suite.teardown()


if __name__ == "__main__":
    success = asyncio.run(run_e2e_tests())
    exit(0 if success else 1)
