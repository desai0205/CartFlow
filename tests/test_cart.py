def test_add_to_cart(client, auth_header, product):
    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 2},
        headers=auth_header,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["total_items"] == 2
    assert len(data["items"]) == 1
    assert float(data["total_amount"]) == 59.98


def test_add_to_cart_insufficient_stock(client, auth_header, product):
    response = client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 999},
        headers=auth_header,
    )
    assert response.status_code == 400


def test_update_and_remove_cart_item(client, auth_header, product):
    add = client.post(
        "/api/v1/cart/items",
        json={"product_id": product["id"], "quantity": 1},
        headers=auth_header,
    )
    item_id = add.json()["items"][0]["id"]

    updated = client.put(
        f"/api/v1/cart/items/{item_id}",
        json={"quantity": 3},
        headers=auth_header,
    )
    assert updated.status_code == 200
    assert updated.json()["total_items"] == 3

    removed = client.delete(f"/api/v1/cart/items/{item_id}", headers=auth_header)
    assert removed.status_code == 200
    assert removed.json()["total_items"] == 0


def test_get_cart_requires_auth(client):
    response = client.get("/api/v1/cart")
    assert response.status_code == 401
