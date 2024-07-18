import unittest
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

class TestMasterMaterial(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestMasterMaterial, self).setUp(*args, **kwargs)
        self.Material = self.env['master.material']

    def test_price_validation(self):
        # Create a material with price less than 100, it should raise a ValidationError
        with self.assertRaises(ValidationError):
            self.Material.create({
                'material_name': 'Test Material',
                'material_buy_price': 50,
            })

        # Create a material with price greater than or equal to 100, it should not raise any exception
        material = self.Material.create({
            'material_name': 'Test Material',
            'material_buy_price': 150,
        })
        self.assertEqual(material.name, 'Test Material')

    def test_update_material(self):
        # Create a material
        material = self.Material.create({
            'material_name': 'Original Material',
            'material_buy_price': 200,
        })

        # Update the material's name
        material.write({'material_name': 'Updated Material'})
        self.assertEqual(material.name, 'Updated Material')

    def test_delete_material(self):
        # Create a material
        material = self.Material.create({
            'material_name': 'Test Material',
            'material_buy_price': 150,
        })

        # Delete the material
        material.unlink()
        self.assertFalse(self.Material.search([('material_name','=','Test Material')]))

if __name__ == '__main__':
    unittest.main()