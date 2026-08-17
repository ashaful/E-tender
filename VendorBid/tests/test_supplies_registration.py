from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields
from unittest.mock import patch


class TestSuppliesRegistration(TransactionCase):

    def setUp(self):
        super().setUp()
        # Create test contacts
        self.contact_1 = self.env['supplies.contact'].create({'name': 'John Primary', 'email': 'john@example.com'})
        self.contact_2 = self.env['supplies.contact'].create({'name': 'Jane Finance', 'email': 'jane@example.com'})
        self.contact_3 = self.env['supplies.contact'].create({'name': 'Jack Authorized', 'email': 'jack@example.com'})
        self.client_ref = self.env['supplies.contact'].create({'name': 'Client X', 'email': 'client@example.com'})

        self.registration = self.env['supplies.registration'].create({
            'name': 'Test Supplier Co.',
            'company_category_type': 'LLC',
            'product_category_id': self.env['product.category'].create({'name': 'Test Category'}).id,
            'email': 'supplier@example.com',
            'street': '123 Street',
            'primary_contact_id': self.contact_1.id,
            'finance_contact_id': self.contact_2.id,
            'authorized_contact_id': self.contact_3.id,
            'client_ref_ids': [(6, 0, [self.client_ref.id])],
            'bank_name': 'Test Bank',
            'branch_address': 'Branch Street',
            'acc_number': '12345678',
        })

    def test_action_approve_success(self):
        self.assertEqual(self.registration.state, 'submitted')
        self.registration.action_approve()
        self.assertEqual(self.registration.state, 'approved')

    def test_action_approve_invalid_state(self):
        self.registration.write({'state': 'approved'})
        with self.assertRaises(ValidationError):
            self.registration.action_approve()

    @patch('odoo.addons.VendorBid.models.supplies_registration.schemas.CompanySchema.model_validate')
    @patch('odoo.addons.VendorBid.models.supplies_registration.schemas.BankSchema.model_validate')
    @patch('odoo.addons.VendorBid.models.supplies_registration.schemas.BankAccountSchema.model_validate')
    @patch('odoo.addons.VendorBid.models.supplies_registration.schemas.UserSchema.model_validate')
    @patch('odoo.addons.VendorBid.models.supplies_registration.utils.get_or_create_bank')
    @patch('odoo.addons.VendorBid.models.supplies_registration.utils.get_child_contacts')
    @patch('odoo.addons.VendorBid.models.supplies_registration.get_smtp_server_email', return_value='noreply@example.com')
    def test_action_finalize_success(self, mock_email, mock_contacts, mock_bank, mock_user_schema, mock_bank_acc_schema, mock_bank_schema, mock_company_schema):
        # Set approved state
        self.registration.action_approve()

        # Mock schema responses
        mock_company_schema.return_value.model_dump.return_value = {
            'name': self.registration.name,
            'email': self.registration.email,
            'street': self.registration.street,
        }
        mock_bank.return_value.id = 1
        mock_bank_acc_schema.return_value.model_dump.return_value = {'acc_number': '12345678'}
        mock_contacts.return_value = []
        mock_user_schema.return_value.model_dump.return_value = {
            'login': self.registration.email,
            'partner_id': 1,
            'company_id': self.env.company.id,
            'groups_id': [(6, 0, self.env.ref('base.group_portal').ids)],
        }

        # Test finalize
        self.registration.action_finalize()
        self.assertEqual(self.registration.state, 'finalized')

    def test_action_finalize_invalid_state(self):
        with self.assertRaises(ValidationError):
            self.registration.action_finalize()

    def test_action_blacklist_opens_wizard(self):
        result = self.registration.action_blacklist()
        self.assertEqual(result['res_model'], 'supplies.blacklist.wizard')
        self.assertEqual(result['view_mode'], 'form')
        self.assertEqual(result['target'], 'new')

    def test_action_reject_opens_wizard(self):
        result = self.registration.action_reject()
        self.assertEqual(result['res_model'], 'supplies.reject.application.wizard')
        self.assertEqual(result['view_mode'], 'form')
        self.assertEqual(result['target'], 'new')
