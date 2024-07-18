import unittest
import json
from odoo.tests.common import HttpCase

class TestMasterMaterialAPI(HttpCase):
    def test_get_master_material(self):
        response = self.url_open('/api/keda-tech/v1/material/master_material?type=fabric')

        # Check if response status code is 200
        self.assertEqual(response.status_code, 200)

        # Decode response content
        content = response.read().decode('utf-8')
        data = json.loads(content)

        # Check if response contains status, message, and data keys
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertIn('data', data)

        # Check if status is 1 (success)
        self.assertEqual(data['status'], 1)

        # Check if message is 'success'
        self.assertEqual(data['message'], 'success')

        # Check if data is a non-empty list
        self.assertIsInstance(data['data'], list)
        self.assertTrue(data['data'])

        # Check if each item in data has the required keys
        for item in data['data']:
            self.assertIn('material_id', item)
            self.assertIn('material_name', item)
            self.assertIn('material_code', item)
            self.assertIn('material_type', item)
            self.assertIn('material_buy_price', item)
            self.assertIn('supplier_id', item)
            self.assertIn('supplier_code', item)
            self.assertIn('supplier_name', item)

    def test_create_master_material(self):
        request_data = {
            'data': [
                {
                    'material_type': 'fabric',
                    'material_code': 'M001',
                    'material_name': 'Fabric Material',
                    'material_buy_price': 150,
                    'supplier_code': 'FC00000003'
                },
                {
                    'material_type': 'jeans',
                    'material_code': 'M002',
                    'material_name': 'Jeans Material',
                    'material_buy_price': 200,
                    'supplier_code': 'SUP002'
                }
            ]
        }

        # Simulate a POST request to the API endpoint
        response = self.url_open('/api/keda-tech/v1/material/master_material', data=json.dumps(request_data), method='POST')

        # Check if response status code is 200
        self.assertEqual(response.status_code, 200)

        # Decode response content
        content = response.read().decode('utf-8')
        data = json.loads(content)

        # Check if response contains status, message, and data keys
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertIn('data', data)

        # Check if status is 1 (success)
        self.assertEqual(data['status'], 1)

        # Check if message is 'Success Create Material'
        self.assertEqual(data['message'], 'Success Create Material')

        # Check if data is a non-empty list
        self.assertIsInstance(data['data'], list)
        self.assertTrue(data['data'])

        # Check if each item in data has the required keys
        for item in data['data']:
            self.assertIn('material_id', item)
            self.assertIn('material_code', item)
            self.assertIn('material_name', item)

    def test_update_master_material(self):
        request_data = {
            'material_id': 14,
            'material_code': 'M001',
            'material_name': 'Updated Fabric Material',
            'material_buy_price': 200,
            'supplier_code': 'SUP002'
        }

        # Simulate a PUT request to the API endpoint
        response = self.url_open('/api/keda-tech/v1/material/master_material', data=json.dumps(request_data), method='PUT')

        # Check if response status code is 200
        self.assertEqual(response.status_code, 200)

        # Decode response content
        content = response.read().decode('utf-8')
        data = json.loads(content)

        # Check if response contains status, message, and data keys
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertIn('data', data)

        # Check if status is 1 (success)
        self.assertEqual(data['status'], 1)

        # Check if message is 'Success Update Material'
        self.assertEqual(data['message'], 'Success Update Material')

        # Check if data contains material_code key
        self.assertIn('material_code', data['data'])

        # Check if material_code matches the one sent in the request
        self.assertEqual(data['data']['material_code'], 'M001')

    def test_delete_master_material(self):
        request_data = {
            'material_id': 14
        }

        # Simulate a DELETE request to the API endpoint
        response = self.url_open('/api/keda-tech/v1/material/master_material', data=json.dumps(request_data), method='DELETE')

        # Check if response status code is 200
        self.assertEqual(response.status_code, 200)

        # Decode response content
        content = response.read().decode('utf-8')
        data = json.loads(content)

        # Check if response contains status, message, and data keys
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertIn('data', data)

        # Check if status is 1 (success)
        self.assertEqual(data['status'], 1)

        # Check if message is 'Success Delete Material'
        self.assertEqual(data['message'], 'Success Delete Material')

        # Check if data is a non-empty list
        self.assertIsInstance(data['data'], list)
        self.assertTrue(data['data'])

        # Check if each item in data has the required keys
        for item in data['data']:
            self.assertIn('material_id', item)

        # Check if material_id matches the one sent in the request
        self.assertEqual(data['data'][0]['material_id'], 14)

if __name__ == '__main__':
    unittest.main()