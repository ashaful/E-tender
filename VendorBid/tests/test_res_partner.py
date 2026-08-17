import base64

from odoo.tests.common import TransactionCase
from datetime import date, datetime

class TestResPartnerInherit(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_model = self.env['res.partner']

    def test_create_partner_with_custom_fields(self):
        """Test creation of a partner with all inherited fields filled."""
        dummy_file_content = base64.b64encode(b'This is a test file.').decode('utf-8')
        dummy_file_content_not_equal= base64.b64encode(b'this for not equal').decode('utf-8')

        vals = {
            'name': 'Test Company',
            'company_category_type': 'LLC',
            'product_category_id': self.env.ref('product.product_category_all').id,
            'trade_license_number': '12345678',
            'commencement_date': '2023-01-01',
            'expiry_date': '2025-01-01',
            'trade_license_doc': dummy_file_content,
            'certificate_of_incorporation_doc': dummy_file_content,
            'certificate_of_good_standing_doc': dummy_file_content,
            'establishment_card_doc': dummy_file_content,
            'vat_tax_certificate_doc': dummy_file_content,
            'memorandum_of_association_doc': dummy_file_content,
            'identification_of_authorised_person_doc': dummy_file_content,
            'bank_letter_doc': dummy_file_content,
            'past_2_years_financial_statement_doc': dummy_file_content,
            'other_certification_doc': dummy_file_content,
            'company_stamp': dummy_file_content,
            'certification_name': 'ISO 9001',
            'certificate_number': 'ISO1234',
            'certifying_body': 'ISO Organization',
            'certification_award_date': '2023-01-01',
            'certification_expiry_date': '2026-01-01',
            'signatory_name': 'John Doe',
            'authorized_signatory_name': 'Jane Smith',
            'date_registration': '2023-01-01 10:00:00',
        }

        partner = self.partner_model.create(vals)
        self.assertEqual(partner.company_category_type, 'LLC')
        self.assertEqual(partner.trade_license_number, '12345678')
        self.assertEqual(partner.certification_name, 'ISO 9001')
        self.assertEqual(partner.signatory_name, 'John Doe')
        self.assertEqual(partner.authorized_signatory_name, 'Jane Smith')
        self.assertEqual(partner.trade_license_doc.decode(), dummy_file_content)
        self.assertNotEqual(partner.company_stamp.decode(), dummy_file_content_not_equal)

    def test_default_values(self):
        """Test default behavior when fields are not set."""
        partner = self.partner_model.create({'name': 'Empty Fields Partner'})
        self.assertFalse(partner.company_category_type)
        self.assertFalse(partner.trade_license_number)
        self.assertFalse(partner.certification_name)
        self.assertFalse(partner.trade_license_doc)
