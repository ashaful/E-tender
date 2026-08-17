from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

class TestResbank(TransactionCase):
    def setUp(self):
        super().setUp()
        # model
        self.Bank = self.env['res.bank']

    def test_defaults_are_empty(self):
        """ New banks should have no SWIFT or IBAN by default."""
        b = self.Bank.create({'name': 'Default Bank'})
        self.assertFalse(b.swift_code, "swift_code should be False or empty by default")
        self.assertFalse(b.iban, "iban should be False or empty by default")

    def test_create_with_swift_and_iban(self):
        """ You can set SWIFT and IBAN on create and they are stored."""
        vals = {
            'name': 'MyBank',
            'swift_code': 'ABCDEFXX',
            'iban': 'GB33BUKB20201555555555',
        }
        b = self.Bank.create(vals)
        self.assertEqual(b.swift_code, vals['swift_code'], "SWIFT not stored correctly")
        self.assertEqual(b.iban, vals['iban'], "IBAN not stored correctly")

    def test_write_swift_and_iban(self):
        """ Writing to swift_code and iban after creation works."""
        b = self.Bank.create({'name': 'WriteBank'})
        b.write({
            'swift_code': 'ZZYYXX11',
            'iban': 'DE89370400440532013000',
        })
        self.assertEqual(b.swift_code, 'ZZYYXX11', "SWIFT write failed")
        self.assertEqual(b.iban, 'DE89370400440532013000', "IBAN write failed")