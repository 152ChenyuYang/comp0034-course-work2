import pytest

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data or b"Home" in response.data

def test_tables(client):
    response = client.get("/tables")
    assert response.status_code == 200
    assert b"Tables" in response.data

def test_areas(client):
    response = client.get("/areas")
    assert response.status_code == 200
    assert b"Area" in response.data

def test_chart_valid_area(client):
    response = client.get("/area_chart/E09000001")  
    assert response.status_code == 200
    assert b"canvas" in response.data

def test_area_detail(client):
    response = client.get("/area_detail/E09000001")  
    assert response.status_code == 200
    assert b"Housing" in response.data or b"Waiting" in response.data

def test_data_table(client):
    response = client.get("/data/Affordable_Housing_Data")
    assert response.status_code == 200
    assert b"Housing" in response.data or b"Year" in response.data

def test_data_table_search(client):
    response = client.get("/data/Affordable_Housing_Data?search=London")
    assert response.status_code == 200

def test_export_table(client):
    response = client.get("/export/Affordable_Housing_Data")
    assert response.status_code == 200
    assert "text/csv" in response.headers["Content-Type"]

def test_export_area(client):
    area_code = "E09000001"  
    response = client.get(f"/export_area/{area_code}")

    
    if response.status_code != 200:
        print("\n⚠️ Export Area 失败时响应内容：\n", response.data.decode())

    assert response.status_code == 200
    assert "text/csv" in response.headers.get("Content-Type", "")
    assert response.headers.get("Content-Disposition", "").endswith(".csv")



def test_news(client):
    response = client.get("/news")
    assert response.status_code in [200, 302]  

def test_not_found(client):
    response = client.get("/random404")
    assert response.status_code == 404

def test_method_not_allowed(client):
    response = client.post("/")
    assert response.status_code == 405
