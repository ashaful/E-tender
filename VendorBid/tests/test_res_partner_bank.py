from odoo.tests.common import TransactionCase

class TestResPartnerBankInherit(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})

    def test_create_bank_with_branch_address(self):
        # Create a bank account with the custom branch_address field
        bank_account = self.env['res.partner.bank'].create({
            'acc_number': '1234567890',
            'partner_id': self.partner.id,
            'branch_address': '123 Test Street, City',
        })

        # Assert values
        self.assertEqual(bank_account.branch_address, '123 Test Street, City')
        self.assertEqual(bank_account.partner_id, self.partner)
        self.assertEqual(bank_account.acc_number, '1234567890')
