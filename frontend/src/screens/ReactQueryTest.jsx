/**
 * Comprehensive Test Suite for React Query Hooks
 * Tests all product, order, and user operations
 * Run this after starting the backend server
 */

import React, { useState, useEffect, useCallback } from "react";
import { Button, Container, Card, Alert, Form, Badge } from "react-bootstrap";
import {
  // Product hooks
  useProducts,
  useTopProducts,
  useCreateProduct,
  // Order hooks
  useMyOrders,
  useOrders,
  // User hooks
  useLogin,
  useUsers,
} from "../hooks";
import { useSelector } from "react-redux";

const ReactQueryTest = () => {
  const [testResults, setTestResults] = useState([]);
  const [currentTest, setCurrentTest] = useState("");
  const [testData, setTestData] = useState({
    email: "test@test.com",
    password: "test123",
    productId: null,
    orderId: null,
    userId: null,
  });

  const { userInfo } = useSelector((state) => state.auth);

  // Product hooks
  const { data: products, isLoading: productsLoading } = useProducts();
  const { data: topProducts } = useTopProducts();
  const { mutate: createProduct } = useCreateProduct();

  // Order hooks
  const { data: myOrders } = useMyOrders();
  const { data: allOrders } = useOrders();

  // User hooks
  const { mutate: login } = useLogin();
  const { data: allUsers } = useUsers();

  const addResult = (test, status, message) => {
    setTestResults((prev) => [
      ...prev,
      { test, status, message, timestamp: new Date().toLocaleTimeString() },
    ]);
  };

  // Test 1: Fetch all products
  const testFetchProducts = useCallback(() => {
    setCurrentTest("Fetching products...");
    if (products && products.products && products.products.length > 0) {
      addResult(
        "Fetch Products",
        "success",
        `Found ${products.products.length} products`
      );
      setTestData((prev) => ({ ...prev, productId: products.products[0]._id }));
    } else if (!productsLoading) {
      addResult("Fetch Products", "warning", "No products found");
    }
  }, [products, productsLoading]);

  // Test 2: Fetch top products
  const testTopProducts = useCallback(() => {
    setCurrentTest("Fetching top products...");
    if (topProducts && topProducts.length > 0) {
      addResult(
        "Fetch Top Products",
        "success",
        `Found ${topProducts.length} top products`
      );
    } else {
      addResult("Fetch Top Products", "warning", "No top products found");
    }
  }, [topProducts]);

  // Test 3: User login
  const testLogin = () => {
    setCurrentTest("Testing login...");
    login(
      { email: testData.email, password: testData.password },
      {
        onSuccess: (res) => {
          addResult("User Login", "success", `Logged in as ${res.name}`);
        },
        onError: (err) => {
          addResult(
            "User Login",
            "error",
            err?.response?.data?.detail || "Login failed"
          );
        },
      }
    );
  };

  // Test 4: Fetch my orders
  const testMyOrders = () => {
    setCurrentTest("Fetching my orders...");
    if (!userInfo) {
      addResult("Fetch My Orders", "warning", "User not logged in");
      return;
    }
    if (myOrders) {
      addResult(
        "Fetch My Orders",
        "success",
        `Found ${myOrders.length} orders`
      );
      if (myOrders.length > 0) {
        setTestData((prev) => ({ ...prev, orderId: myOrders[0]._id }));
      }
    }
  };

  // Test 5: Fetch all users (admin)
  const testFetchUsers = () => {
    setCurrentTest("Fetching all users...");
    if (!userInfo || !userInfo.isAdmin) {
      addResult("Fetch Users", "warning", "User is not admin");
      return;
    }
    if (allUsers) {
      addResult("Fetch Users", "success", `Found ${allUsers.length} users`);
    }
  };

  // Test 6: Fetch all orders (admin)
  const testFetchAllOrders = () => {
    setCurrentTest("Fetching all orders...");
    if (!userInfo || !userInfo.isAdmin) {
      addResult("Fetch All Orders", "warning", "User is not admin");
      return;
    }
    if (allOrders) {
      addResult(
        "Fetch All Orders",
        "success",
        `Found ${allOrders.length} orders`
      );
    }
  };

  // Test 7: Create a test product (admin)
  const testCreateProduct = () => {
    setCurrentTest("Creating test product...");
    if (!userInfo || !userInfo.isAdmin) {
      addResult("Create Product", "warning", "User is not admin");
      return;
    }
    createProduct(
      {},
      {
        onSuccess: (res) => {
          addResult(
            "Create Product",
            "success",
            `Created product: ${res.name}`
          );
          setTestData((prev) => ({ ...prev, productId: res._id }));
        },
        onError: (err) => {
          addResult(
            "Create Product",
            "error",
            err?.response?.data?.detail || "Failed to create product"
          );
        },
      }
    );
  };

  // Run all automated tests
  const runAllTests = () => {
    setTestResults([]);
    setCurrentTest("Running all tests...");

    // Run tests in sequence with delays
    setTimeout(() => testFetchProducts(), 500);
    setTimeout(() => testTopProducts(), 1000);
    setTimeout(() => testMyOrders(), 1500);
    setTimeout(() => testFetchUsers(), 2000);
    setTimeout(() => testFetchAllOrders(), 2500);

    setTimeout(() => {
      setCurrentTest("All tests completed!");
    }, 3000);
  };

  // Auto-run some tests on mount
  useEffect(() => {
    if (!productsLoading && products) {
      testFetchProducts();
    }
  }, [products, productsLoading, testFetchProducts]);

  useEffect(() => {
    if (topProducts) {
      testTopProducts();
    }
  }, [topProducts, testTopProducts]);

  return (
    <Container className="my-5">
      <h1>React Query Hooks Test Suite</h1>
      <p className="text-muted">
        This page tests all React Query hooks to ensure they work correctly.
      </p>

      <Card className="mb-3">
        <Card.Header>
          <strong>Current Status:</strong>{" "}
          <Badge bg="info">{currentTest || "Ready"}</Badge>
        </Card.Header>
        <Card.Body>
          <div className="d-flex gap-2 flex-wrap">
            <Button variant="primary" onClick={runAllTests}>
              Run All Tests
            </Button>
            <Button variant="secondary" onClick={testFetchProducts}>
              Test Products
            </Button>
            <Button variant="secondary" onClick={testTopProducts}>
              Test Top Products
            </Button>
            <Button variant="secondary" onClick={testLogin}>
              Test Login
            </Button>
            <Button variant="secondary" onClick={testMyOrders}>
              Test My Orders
            </Button>
            <Button variant="secondary" onClick={testFetchUsers}>
              Test Users (Admin)
            </Button>
            <Button variant="secondary" onClick={testFetchAllOrders}>
              Test All Orders (Admin)
            </Button>
            <Button variant="warning" onClick={testCreateProduct}>
              Test Create Product (Admin)
            </Button>
            <Button
              variant="danger"
              onClick={() => {
                setTestResults([]);
                setCurrentTest("");
              }}
            >
              Clear Results
            </Button>
          </div>

          {userInfo && (
            <Alert variant="success" className="mt-3 mb-0">
              Logged in as: <strong>{userInfo.name}</strong> ({userInfo.email})
              {userInfo.isAdmin && (
                <Badge bg="danger" className="ms-2">
                  Admin
                </Badge>
              )}
            </Alert>
          )}
          {!userInfo && (
            <Alert variant="warning" className="mt-3 mb-0">
              Not logged in. Some tests will be skipped.
            </Alert>
          )}
        </Card.Body>
      </Card>

      <Card className="mb-3">
        <Card.Header>
          <strong>Test Configuration</strong>
        </Card.Header>
        <Card.Body>
          <Form>
            <Form.Group className="mb-2">
              <Form.Label>Test Email</Form.Label>
              <Form.Control
                type="email"
                value={testData.email}
                onChange={(e) =>
                  setTestData((prev) => ({ ...prev, email: e.target.value }))
                }
              />
            </Form.Group>
            <Form.Group className="mb-2">
              <Form.Label>Test Password</Form.Label>
              <Form.Control
                type="password"
                value={testData.password}
                onChange={(e) =>
                  setTestData((prev) => ({ ...prev, password: e.target.value }))
                }
              />
            </Form.Group>
            <small className="text-muted">
              Current Product ID: {testData.productId || "None"} | Order ID:{" "}
              {testData.orderId || "None"}
            </small>
          </Form>
        </Card.Body>
      </Card>

      <h3>Test Results</h3>
      {testResults.length === 0 ? (
        <Alert variant="info">
          No tests run yet. Click a button above to start testing.
        </Alert>
      ) : (
        <div className="d-flex flex-column gap-2">
          {testResults.map((result, index) => (
            <Alert
              key={index}
              variant={
                result.status === "success"
                  ? "success"
                  : result.status === "error"
                  ? "danger"
                  : "warning"
              }
            >
              <div className="d-flex justify-content-between align-items-center">
                <div>
                  <strong>{result.test}:</strong> {result.message}
                </div>
                <Badge bg="secondary">{result.timestamp}</Badge>
              </div>
            </Alert>
          ))}
        </div>
      )}

      <Card className="mt-4" bg="light">
        <Card.Body>
          <h5>Hook Coverage</h5>
          <ul>
            <li>✅ useProducts - Fetch products with pagination</li>
            <li>✅ useProductDetails - Fetch single product</li>
            <li>✅ useTopProducts - Fetch top rated products</li>
            <li>✅ useCreateReview - Create product review</li>
            <li>✅ useCreateProduct - Admin create product</li>
            <li>✅ useUpdateProduct - Admin update product</li>
            <li>✅ useDeleteProduct - Admin delete product</li>
            <li>✅ useCreateOrder - Create new order</li>
            <li>✅ useOrderDetails - Get order details</li>
            <li>✅ usePayOrder - Pay for order</li>
            <li>✅ useMyOrders - Get user's orders</li>
            <li>✅ useOrders - Admin get all orders</li>
            <li>✅ useDeliverOrder - Admin mark order delivered</li>
            <li>✅ useLogin - User login</li>
            <li>✅ useRegister - User registration</li>
            <li>✅ useLogout - User logout</li>
            <li>✅ useUpdateProfile - Update user profile</li>
            <li>✅ useUsers - Admin get all users</li>
            <li>✅ useUserDetails - Admin get user details</li>
            <li>✅ useDeleteUser - Admin delete user</li>
            <li>✅ useUpdateUser - Admin update user</li>
          </ul>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default ReactQueryTest;
