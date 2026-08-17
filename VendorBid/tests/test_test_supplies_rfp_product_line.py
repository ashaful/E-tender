from odoo.tests import common
from datetime import date


class TestSuppliesRfpProductLine(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.currency = self.env.company.currency_id
        self.category = self.env['product.category'].create({'name': 'Electronics'})

        self.product1 = self.env['product.product'].create({
            'name': 'Laptop',
            'categ_id': self.category.id,

        })

        self.product2 = self.env['product.product'].create({
            'name': 'Monitor',
            'categ_id': self.category.id,
        })

        self.rfp = self.env['supplies.rfp'].create({
            'required_date': date.today(),
            'product_category_id': self.category.id,
        })

    def test_compute_subtotal_price(self):
        line = self.env['supplies.rfp.product.line'].create({
            'rfp_id': self.rfp.id,
            'product_id': self.product1.id,
            'product_qty': 3,
            'unit_price': 100,
            'delivery_charge': 50,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
        })
        line._compute_subtotal_price()
        expected = (3 * 100) + 50
        self.assertEqual(line.subtotal_price, expected)

    def test_onchange_product_qty_negative(self):
        line = self.env['supplies.rfp.product.line'].new({
            'product_qty': -5
        })
        line._onchange_product_qty()
        self.assertEqual(line.product_qty, 1)

    def test_onchange_product_id_duplicate(self):
        # Add initial line with product1
        line1 = self.env['supplies.rfp.product.line'].create({
            'rfp_id': self.rfp.id,
            'product_id': self.product1.id,
            'product_qty': 1,
            'unit_price': 10,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
        })

        # Try to add another line with same product using `new()`
        line2 = self.env['supplies.rfp.product.line'].new({
            'rfp_id': self.rfp.id,
            'product_id': self.product1.id,
        })

        # Attach context to simulate proper onchange
        line2.rfp_id = self.rfp
        line2._onchange_product_id()
        self.assertFalse(line2.product_id, "Product should be reset due to duplicate")

    def test_related_fields(self):
        line = self.env['supplies.rfp.product.line'].create({
            'rfp_id': self.rfp.id,
            'product_id': self.product1.id,
            'product_qty': 2,
            'unit_price': 100,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
        })
        self.assertEqual(line.product_name, self.product1.name)


    def test_default_currency(self):
        line = self.env['supplies.rfp.product.line'].create({
            'rfp_id': self.rfp.id,
            'product_id': self.product1.id,
            'product_qty': 1,
            'unit_price': 100,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
        })
        self.assertEqual(line.currency_id, self.currency)
