from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import date


class TestPartnerEditRequest(TransactionCase):

    def setUp(self):
        super().setUp()
        # Create a supplier partner
        self.partner = self.env['res.partner'].create({
            'name': 'Test Supplier',
            'email': 'supplier@example.com',
        })

        # Create an edit request for that partner
        self.edit_request = self.env['partner.edit.request'].create({
            'partner_id': self.partner.id,
            'trade_license_number': 'TL-12345',
            'commencement_date': date(2020, 1, 1),
            'expiry_date': date(2030, 1, 1),
            'phone': '+1234567890',
        })

    def test_approve_edit_request(self):
        """Test that approving an edit request updates the partner and changes state."""
        self.edit_request.action_approve()

        self.partner = self.env['res.partner'].browse(self.partner.id)
        self.assertEqual(self.edit_request.state, 'approved', "Edit request should be approved")
        self.assertEqual(self.partner.trade_license_number, 'TL-12345', "Trade license should be updated")
        self.assertEqual(self.partner.phone, '+1234567890', "Phone number should be updated")
        self.assertIsNotNone(self.edit_request.review_date, "Review date should be set")
        self.assertEqual(self.edit_request.reviewed_by.id, self.env.user.id, "Reviewer should be current user")

    def test_prevent_double_approval(self):
        """Test that already approved requests cannot be approved again."""
        self.edit_request.action_approve()
        with self.assertRaises(UserError):
            self.edit_request.action_approve()

    def test_open_reject_wizard_action(self):
        """Test that the rejection wizard action returns correct window form data."""
        action = self.edit_request.action_open_reject_wizard()
        self.assertEqual(action['res_model'], 'partner.edit.reject.wizard', "Should open the correct wizard model")
        self.assertEqual(action['view_mode'], 'form')
        self.assertEqual(action['target'], 'new')
        self.assertEqual(action['context']['default_request_id'], self.edit_request.id, "Context must include request ID")
