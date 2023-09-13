from starlette.testclient import TestClient
import pandas as pd
from main import app

client = TestClient(app)


class TestBasic:
    def test_read_main(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}


class TestCreateBasic:
    def test_create_cruise(self):
        response = client.post(
            "/cruises/",
            headers={"X-Token": "coneofsilence"},
            json={
                "date_start": "2023-09-13",
                "date_end": "2023-09-13",
                "mixed_layer_depth_value": 0,
                "mixed_layer_depth_method": "dens_T2"
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "date_start": "2023-09-13",
            "date_end": "2023-09-13",
            "mixed_layer_depth_value": 0,
            "mixed_layer_depth_method": "dens_T2",
            "id": 1,
            "casts": []
        }



