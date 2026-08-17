from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSuppliesRfpProductLine(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Product = self.env['product.product']
        self.Rfp = self.env['supplies.rfp']
        self.ProductLine = self.env['supplies.rfp.product.line']

        # Create two products
        self.product_1 = self.Product.create({
            'name': 'Test Product 1',
            'list_price': 100.0,
        })
        self.product_2 = self.Product.create({
            'name': 'Test Product 2',
            'list_price': 200.0,
        })

        # Create a sample RFP
        self.rfp = self.Rfp.create({
            'rfp_number': '12345678',
        })

    def test_subtotal_price_computation(self):
        line = self.ProductLine.create({
            'rfp_id': self.rfp.id,
            'product_id': self.product_1.id,
            'product_qty': 2,
            'unit_price': 150.0,
            'delivery_charge': 20.0,
        })
        self.assertEqual(line.subtotal_price, 2 * 150.0 + 20.0)

    def test_quantity_not_negative(self):
        line = self.ProductLine.new({
            'product_qty': -5
        })
        line._onchange_product_qty()
        self.assertEqual(line.product_qty, 1)

    # def test_prevent_duplicate_product(self):
    #     # Add first product line
    #     self.ProductLine.create({
    #         'rfp_id': self.rfp.id,
    #         'product_id': self.product_1.id,
    #         'product_qty': 1,
    #         'unit_price': 100.0
    #     })
    #
    #     # Attempt to create second product line with the same product
    #     line2 = self.ProductLine.new({
    #         'rfp_id': self.rfp.id,
    #         'product_id': self.product_1.id,
    #     })
    #     warning = line2._onchange_product_id()
    #     self.assertFalse(line2.product_id)
    #     self.assertIn('Duplicate Product', warning['warning']['title'])

