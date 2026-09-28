def test_create_order_from_cart(client, auth_header, admin_header, product):
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 2},
        headers=auth_header,
    )

    response = client.post(
        "/api/v1/orders",
        json={"shipping_address": "123 Main Street, City"},
        headers=auth_header,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["items"][0]["quantity"] == 2
    assert float(data["total_amount"]) == 59.98

    # Stock reduced
    product_resp = client.get(f"/api/v1/products/{product['id']}")
    assert product_resp.json()["stock"] == 48

    # Cart cleared
    cart = client.get("/api/v1/cart", headers=auth_header)
    assert cart.json()["total_items"] == 0


def test_create_order_empty_cart(client, auth_header):
    response = client.post(
        "/api/v1/orders",
        json={"shipping_address": "123 Main Street, City"},
        headers=auth_header,
    )
    assert response.status_code == 400


def test_list_orders_user_sees_own(client, auth_header, product):
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 1},
        headers=auth_header,
    )
    client.post(
        "/api/v1/orders",
        json={"shipping_address": "123 Main Street, City"},
        headers=auth_header,
    )

    response = client.get("/api/v1/orders", headers=auth_header)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_admin_cancel_restores_stock(client, auth_header, admin_header, product):
    client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 3},
        headers=auth_header,
    )
    order = client.post(
        "/api/v1/orders",
        json={"shipping_address": "123 Main Street, City"},
        headers=auth_header,
    ).json()

    assert client.get(f"/api/v1/products/{product['id']}").json()["stock"] == 47

    cancelled = client.patch(
        f"/api/v1/orders/{order['id']}/status",
        json={"status": "cancelled"},
        headers=admin_header,
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
    assert client.get(f"/api/v1/products/{product['id']}").json()["stock"] == 50
