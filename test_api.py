"""
Test script for FastAPI backend endpoints
"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:5000"
test_results = []


def log_test(name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results.append({"name": name, "passed": passed, "message": message})
    print(f"{status} - {name}")
    if message:
        print(f"  └─ {message}")


async def test_health():
    """Test health endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            log_test("Health Check", response.status_code == 200, f"Status: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        log_test("Health Check", False, str(e))
        return False


async def test_get_products():
    """Test get products endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/products")
            passed = response.status_code == 200
            data = response.json() if passed else {}
            log_test("GET /api/products", passed, 
                    f"Found {len(data.get('products', []))} products" if passed else str(response.text))
            return passed, data
    except Exception as e:
        log_test("GET /api/products", False, str(e))
        return False, {}


async def test_get_top_products():
    """Test get top products endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/products/top")
            passed = response.status_code == 200
            data = response.json() if passed else []
            log_test("GET /api/products/top", passed,
                    f"Found {len(data)} top products" if passed else str(response.text))
            return passed
    except Exception as e:
        log_test("GET /api/products/top", False, str(e))
        return False


async def test_user_auth():
    """Test user authentication"""
    try:
        async with httpx.AsyncClient() as client:
            # Test login
            login_data = {
                "email": "admin@email.com",
                "password": "123456"
            }
            response = await client.post(
                f"{BASE_URL}/api/users/auth",
                json=login_data
            )
            passed = response.status_code == 200
            
            if passed:
                data = response.json()
                cookies = response.cookies
                has_jwt = "jwt" in cookies
                log_test("POST /api/users/auth (Login)", passed and has_jwt,
                        f"User: {data.get('name')}, JWT cookie: {has_jwt}")
                return passed and has_jwt, cookies
            else:
                log_test("POST /api/users/auth (Login)", False,
                        f"Status: {response.status_code}, Body: {response.text}")
                return False, {}
    except Exception as e:
        log_test("POST /api/users/auth (Login)", False, str(e))
        return False, {}


async def test_user_profile(cookies):
    """Test get user profile (requires auth)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/users/profile",
                cookies=cookies
            )
            passed = response.status_code == 200
            data = response.json() if passed else {}
            log_test("GET /api/users/profile", passed,
                    f"User: {data.get('name')}" if passed else str(response.text))
            return passed
    except Exception as e:
        log_test("GET /api/users/profile", False, str(e))
        return False


async def test_user_register():
    """Test user registration"""
    try:
        async with httpx.AsyncClient() as client:
            # Create unique email with timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            register_data = {
                "name": "Test User",
                "email": f"test{timestamp}@email.com",
                "password": "123456"
            }
            response = await client.post(
                f"{BASE_URL}/api/users",
                json=register_data
            )
            passed = response.status_code == 201
            data = response.json() if passed else {}
            log_test("POST /api/users (Register)", passed,
                    f"Created user: {data.get('name')}" if passed else str(response.text))
            return passed
    except Exception as e:
        log_test("POST /api/users (Register)", False, str(e))
        return False


async def test_paypal_config():
    """Test PayPal config endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/config/paypal")
            passed = response.status_code == 200
            data = response.json() if passed else {}
            log_test("GET /api/config/paypal", passed,
                    f"Client ID: {data.get('clientId')}" if passed else str(response.text))
            return passed
    except Exception as e:
        log_test("GET /api/config/paypal", False, str(e))
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FastAPI Backend Test Suite")
    print("="*60 + "\n")
    
    # Test health
    health_ok = await test_health()
    if not health_ok:
        print("\n❌ Server is not running. Start it first.")
        return
    
    print("\n" + "-"*60)
    print("Testing Public Endpoints")
    print("-"*60 + "\n")
    
    # Test products
    await test_get_products()
    await test_get_top_products()
    await test_paypal_config()
    
    print("\n" + "-"*60)
    print("Testing Authentication")
    print("-"*60 + "\n")
    
    # Test auth
    auth_ok, cookies = await test_user_auth()
    await test_user_register()
    
    if auth_ok:
        print("\n" + "-"*60)
        print("Testing Protected Endpoints")
        print("-"*60 + "\n")
        await test_user_profile(cookies)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60 + "\n")
    
    passed = sum(1 for t in test_results if t["passed"])
    failed = len(test_results) - passed
    
    print(f"Total Tests: {len(test_results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print("\nFailed Tests:")
        for test in test_results:
            if not test["passed"]:
                print(f"  - {test['name']}: {test['message']}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
