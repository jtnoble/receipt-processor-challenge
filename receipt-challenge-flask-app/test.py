import unittest
from app import app, entries, calculate_points

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        entries.clear()

    def test_process_receipt_valid(self):
        data = {
            "retailer": "Test Store",
            "purchaseDate": "2025-01-09",
            "purchaseTime": "14:30",
            "total": "50.00",
            "items": [
                {"shortDescription": "item1", "price": "10.00"},
                {"shortDescription": "item2", "price": "20.00"}
            ]
        }
        response = self.app.post('/receipts/process', json=data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json)

    def test_process_receipt_invalid_missing_field(self):
        data = {
            "retailer": "Test Store",
            "purchaseDate": "2025-01-09",
            "purchaseTime": "14:30",
            "total": "50.00"
            # Missing "items"
        }
        response = self.app.post('/receipts/process', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("The receipt is invalid.", response.json['description'])
    
    def test_process_receipt_invalid_type_incorrect(self):
        data = {
            "retailer": "Test Store",
            "purchaseDate": "2025-01-09",
            "purchaseTime": "14:30",
            "total": 50.00, # Incorrect type, should be string
            "items": [
                {"shortDescription": "item1", "price": "10.00"},
                {"shortDescription": "item2", "price": "20.00"}
            ]
        }
        response = self.app.post('/receipts/process', json=data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("The receipt is invalid.", response.json['description'])

    def test_get_points_by_id_valid(self):
        receipt_id = "test-id"
        entries[receipt_id] = 25
        response = self.app.get(f'/receipts/{receipt_id}/points')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['points'], 25)

    def test_get_points_by_id_not_found(self):
        response = self.app.get('/receipts/nonexistent-id/points')

        self.assertEqual(response.status_code, 404)
        self.assertIn("No receipt found for that ID.", response.json['description'])

    def test_calculate_points_retailer_points_only(self):
        data = {
            "retailer": "Market",   # 6 points for 6 letters
            "purchaseDate": "2025-01-02",
            "purchaseTime": "12:00",
            "items": [
                {
                "shortDescription": "Apple",
                "price": "0.89"
                }
            ],
            "total": "0.89"
        }
        
        calculated_points = calculate_points(data)
        actual_points = 6

        self.assertEqual(calculated_points, actual_points)
    
    def test_calculate_points_round_dollar_amount(self):
        data = {
            "retailer": "Market",   # 6 points for 6 letters
            "purchaseDate": "2025-01-02",
            "purchaseTime": "12:00",
            "items": [
                {
                "shortDescription": "Apple",
                "price": "1.00"
                }
            ],
            "total": "1.00" # 25 points for multiple of 25 / 50 points for round dollar amount
        }
        
        calculated_points = calculate_points(data)
        actual_points = 81  # 6 + 25 + 50

        self.assertEqual(calculated_points, actual_points)

    def test_calculate_points_total_multiple_of_quarter(self):
        data = {
            "retailer": "Market",   # 6 points for 6 letters
            "purchaseDate": "2025-01-02",
            "purchaseTime": "12:00",
            "items": [
                {
                "shortDescription": "Apple",
                "price": "1.25"
                }
            ],
            "total": "1.25" # 25 points for multiple of 25
        }
        
        calculated_points = calculate_points(data)
        actual_points = 31  # 6 + 25

        self.assertEqual(calculated_points, actual_points)
    
    def test_calculate_points_5_points_every_2_items(self):
        data = {
            "retailer": "Market",   # 6 points for 6 letters
            "purchaseDate": "2025-01-02",
            "purchaseTime": "12:00",
            "items": [  # 5 points for 2 items
                {
                "shortDescription": "Apple",
                "price": "1.05"
                },
                {
                "shortDescription": "Apple",
                "price": "1.05"
                }
            ],
            "total": "2.10"
        }
        
        calculated_points = calculate_points(data)
        actual_points = 11  # 6 + 5

        self.assertEqual(calculated_points, actual_points)
    
    def test_calculate_points_trimmed_length_item_multiply_then_round_up(self):
        data = {
            "retailer": "Market",   # 6 points for 6 letters
            "purchaseDate": "2025-01-02",
            "purchaseTime": "12:00",
            "items": [
                {
                "shortDescription": "Pineapple", # 9 characters, multiple of 3
                "price": "5.51" # 2 points, 5.51 * 0.2 = ~1.1, round up to 2
                }
            ],
            "total": "5.51"
        }
        
        calculated_points = calculate_points(data)
        actual_points = 8  # 6 + 2

        self.assertEqual(calculated_points, actual_points)
    
    def test_calculate_points_purchase_date_odd(self):
        data = {
            "retailer": "Market",   # 6 points for 6 letters
            "purchaseDate": "2025-01-01", # 6 points for odd purchase date
            "purchaseTime": "12:00",
            "items": [
                {
                "shortDescription": "Apple",
                "price": "0.89"
                }
            ],
            "total": "0.89"
        }
        
        calculated_points = calculate_points(data)
        actual_points = 12  # 6 + 6

        self.assertEqual(calculated_points, actual_points)
    
    def test_calculate_points_between_2pm_4pm(self):
        data = {
            "retailer": "Market",   # 6 points for 6 letters
            "purchaseDate": "2025-01-02",
            "purchaseTime": "15:00", # 10 points, 3pm is between 2pm and 4pm
            "items": [
                {
                "shortDescription": "Apple",
                "price": "0.89"
                }
            ],
            "total": "0.89"
        }
        
        calculated_points = calculate_points(data)
        actual_points = 16  # 6 + 10

        self.assertEqual(calculated_points, actual_points)
    

    def test_calculate_points_github_example_1(self):
        data = {
            "retailer": "Target",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {
                "shortDescription": "Mountain Dew 12PK",
                "price": "6.49"
                },{
                "shortDescription": "Emils Cheese Pizza",
                "price": "12.25"
                },{
                "shortDescription": "Knorr Creamy Chicken",
                "price": "1.26"
                },{
                "shortDescription": "Doritos Nacho Cheese",
                "price": "3.35"
                },{
                "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
                "price": "12.00"
                }
            ],
            "total": "35.35"
        }
        
        calculated_points = calculate_points(data)
        actual_points = 28

        self.assertEqual(calculated_points, actual_points)

    def test_calculate_points_github_example_2(self):
        data = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-03-20",
            "purchaseTime": "14:33",
            "items": [
                {
                "shortDescription": "Gatorade",
                "price": "2.25"
                },{
                "shortDescription": "Gatorade",
                "price": "2.25"
                },{
                "shortDescription": "Gatorade",
                "price": "2.25"
                },{
                "shortDescription": "Gatorade",
                "price": "2.25"
                }
            ],
            "total": "9.00"
        }
        
        calculated_points = calculate_points(data)
        actual_points = 109

        self.assertEqual(calculated_points, actual_points)

if __name__ == '__main__':
    unittest.main()