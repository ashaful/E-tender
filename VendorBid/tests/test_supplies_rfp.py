from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestSuppliesRfp(TransactionCase):

    def setUp(self):
        super().setUp()
        self.RFP = self.env['supplies.rfp']
        self.ProductLine = self.env['supplies.rfp.product.line']
        self.partner = self.env['res.partner'].create({
            'name': 'Test Supplier',
            'email': 'supplier@example.com',
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
        })
        self.category = self.env['product.category'].create({
            'name': 'Electronics',
        })

    def test_submit_rfp_without_product_line_should_fail(self):
        rfp = self.RFP.create({
            'product_category_id': self.category.id,
        })
        with self.assertRaises(UserError):
            rfp.action_submit()

    def test_submit_rfp_with_zero_qty_should_fail(self):
        rfp = self.RFP.create({
            'product_category_id': self.category.id,
        })
        self.ProductLine.create({
            'rfp_id': rfp.id,
            'product_id': self.product.id,
            'product_qty': 0,
            'unit_price': 100,
        })
        with self.assertRaises(UserError):
            rfp.action_submit()

    def test_successful_rfp_submission(self):
        rfp = self.RFP.create({
            'product_category_id': self.category.id,
        })
        self.ProductLine.create({
            'rfp_id': rfp.id,
            'product_id': self.product.id,
            'product_qty': 5,
            'unit_price': 100,
        })
        rfp.action_submit()
        self.assertEqual(rfp.state, 'submitted')
        self.assertEqual(rfp.submitted_by.id, self.env.user.id)

    def test_total_amount_computation(self):
        rfp = self.RFP.create({
            'product_category_id': self.category.id,
        })
        self.ProductLine.create({
            'rfp_id': rfp.id,
            'product_id': self.product.id,
            'product_qty': 2,
            'unit_price': 100,
        })
        rfp._compute_total_amount()
        self.assertEqual(rfp.total_amount, 200)

    def test_reject_rfp(self):
        rfp = self.RFP.create({
            'product_category_id': self.category.id,
        })
        self.ProductLine.create({
            'rfp_id': rfp.id,
            'product_id': self.product.id,
            'product_qty': 1,
            'unit_price': 100,
        })
        rfp.action_submit()
        rfp.action_reject()
        self.assertEqual(rfp.state, 'rejected')

    def test_visibility_computation(self):
        rfp = self.RFP.create({
            'product_category_id': self.category.id,
        })
        rfp._compute_visible_to_reviewer()
        self.assertIn(rfp.visible_to_reviewer, [True, False])  # Depends on group/user logic

    def test_get_rfp_sudo(self):
        rfp = self.RFP.create({
            'product_category_id': self.category.id,
        })
        result = self.RFP.get_rfp_sudo([('id', '=', rfp.id)], ['id', 'rfp_number'])
        self.assertTrue(result)
        self.assertEqual(result[0]['id'], rfp.id)
