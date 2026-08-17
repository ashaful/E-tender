from odoo.tests.common import TransactionCase

class TestAccountTaxInherit(TransactionCase):

    def setUp(self):
        super().setUp()
        self.tax = self.env['account.tax'].create({
            'name': 'Test VAT',
            'amount': 10,
            'amount_type': 'percent',
            'type_tax_use': 'sale'
        })

    def test_prepare_base_line_with_delivery_charge(self):
        # Create a dummy record with delivery_charge attribute
        class DummyRecord:
            delivery_charge = 20.0

        dummy = DummyRecord()

        # Call the real method with dummy record and base line
        result = self.tax._prepare_base_line_for_taxes_computation(
            dummy,
            price_unit=100.0,
            quantity=2.0
        )

        expected_price_unit = 100.0 + (20.0 / 2.0)
        self.assertAlmostEqual(result['price_unit'], expected_price_unit)

    def test_prepare_base_line_without_quantity(self):
        class DummyRecord:
            delivery_charge = 10.0

        dummy = DummyRecord()

        # No quantity case: should add full delivery charge
        result = self.tax._prepare_base_line_for_taxes_computation(
            dummy,
            price_unit=80.0,
            quantity=0.0
        )

        expected_price_unit = 80.0 + 10.0
        self.assertAlmostEqual(result['price_unit'], expected_price_unit)
