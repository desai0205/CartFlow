def test_create_category_admin(client, admin_header):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Books", "description": "Reading"},
        headers=admin_header,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Books"


def test_create_category_forbidden_for_user(client, auth_header):
    response = client.post(
        "/api/v1/categories",
        json={"name": "Books"},
        headers=auth_header,
    )
    assert response.status_code == 403


def test_list_categories(client, category):
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_create_product(client, admin_header, category):
    response = client.post(
        "/api/v1/products",
        json={
            "name": "Keyboard",
            "price": "59.99",
            "stock": 10,
            "category_id": category["id"],
        },
        headers=admin_header,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Keyboard"
    assert float(data["price"]) == 59.99
    assert data["stock"] == 10


def test_list_products(client, product):
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert any(p["id"] == product["id"] for p in response.json())


def test_update_stock(client, admin_header, product):
    response = client.patch(
        f"/api/v1/products/{product['id']}/stock",
        json={"stock": 5},
        headers=admin_header,
    )
    assert response.status_code == 200
    assert response.json()["stock"] == 5


def test_soft_delete_product(client, admin_header, product):
    response = client.delete(
        f"/api/v1/products/{product['id']}",
        headers=admin_header,
    )
    assert response.status_code == 204

    listed = client.get("/api/v1/products")
    assert all(p["id"] != product["id"] for p in listed.json())
