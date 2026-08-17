# import unittest
# from unittest.mock import MagicMock, patch
# from odoo.tests.common import TransactionCase
# from odoo import models
# from odoo.addons.VendorBid.utils.controller_utils import validate_email_address, \
#     create_supplier_registration, generate_registration_url, get_rfp_general_search_domain, format_response, \
#     format_labels, get_nice_error_message
#
#
# class TestUtils(TransactionCase):
#     @patch('odoo.http.request')
#     def test_validate_email_address(self, mock_request):
#         # Mock the request environment
#         mock_request.env['mail.blacklist'].sudo().search.return_value = False
#         mock_request.env['res.users'].sudo().search.return_value = False
#         mock_request.env['supplies.registration'].sudo().search.return_value = False
#
#         valid_email = "valid@example.com"
#         invalid_email = "invalid@example.com"
#
#         # Test for valid email
#         result = validate_email_address(mock_request, valid_email)
#         self.assertTrue(result[0])
#
#         # Test for blacklisted email
#         mock_request.env['mail.blacklist'].sudo().search.return_value = MagicMock()
#         result = validate_email_address(mock_request, invalid_email)
#         self.assertFalse(result[0])
#         self.assertEqual(result[1], 'Email address is blacklisted')
#
#         # Test for already registered email
#         mock_request.env['mail.blacklist'].sudo().search.return_value = False
#         mock_request.env['res.users'].sudo().search.return_value = MagicMock()
#         result = validate_email_address(mock_request, invalid_email)
#         self.assertFalse(result[0])
#         self.assertEqual(result[1], 'Email address is already registered')
#
#         # Test for already applied email
#         mock_request.env['res.users'].sudo().search.return_value = False
#         mock_request.env['supplies.registration'].sudo().search.return_value = MagicMock()
#         result = validate_email_address(mock_request, invalid_email)
#         self.assertFalse(result[0])
#         self.assertEqual(result[1], 'You have already applied')
#     #
#     # @patch('odoo.api.Environment')
#     # def test_create_supplier_registration(self, mock_env):
#     #     # Test data
#     #     data = {
#     #         'company_name': 'Test Company',
#     #         'company_address': '123 Street',
#     #         'vat': '1234567890',
#     #         'primary_contact_id': {'email': 'contact@example.com'},
#     #         'client_ref_ids': [{'email': 'client@example.com'}]
#     #     }
#     #
#     #     # Mock the supplier creation
#     #     mock_supplies_contact = MagicMock()
#     #     mock_env['supplies.contact'].sudo().search.return_value = mock_supplies_contact
#     #     mock_env['supplies.contact'].sudo().create.return_value = mock_supplies_contact
#     #     mock_env['supplies.registration'].sudo().create.return_value = MagicMock()
#     #
#     #     # Call the function
#     #     supplier_registration = create_supplier_registration(mock_env, data)
#     #
#     #     # Check that the contacts were created or fetched
#     #     mock_env['supplies.contact'].sudo().create.assert_called_with(data['primary_contact_id'])
#     #     mock_env['supplies.contact'].sudo().create.assert_called_with(data['client_ref_ids'][0])
#     #
#     #     # Verify that the registration was created
#     #     mock_env['supplies.registration'].sudo().create.assert_called_once()
#     #
#     # @patch('odoo.api.Environment')
#     # def test_generate_registration_url(self, mock_env):
#     #     # Test data
#     #     registration_id = 1
#     #
#     #     # Mock the necessary data for URL generation
#     #     mock_env['ir.config_parameter'].sudo().get_param.return_value = 'http://localhost'
#     #     mock_action = MagicMock()
#     #     mock_env.ref.return_value = mock_action
#     #
#     #     # Call the function
#     #     url = generate_registration_url(mock_env, registration_id)
#     #
#     #     # Check if the URL is correctly formatted
#     #     expected_url = "http://localhost/web#id=1&model=supplies.registration&action=340&view_type=form&cids=1"
#     #     self.assertEqual(url, expected_url)
#     #
#     # @patch('odoo.api.Environment')
#     # def test_get_rfp_general_search_domain(self, mock_env):
#     #     # Mock user and their attributes
#     #     mock_user = MagicMock()
#     #     mock_user.partner_id.supplier_rank = 1
#     #     mock_user.partner_id.product_category_id = MagicMock()
#     #     mock_env.user = mock_user
#     #     mock_env['ir.config_parameter'].sudo().get_param.return_value = 'http://localhost'
#     #
#     #     # Mock get_descendant_category_ids function
#     #     mock_get_descendant_category_ids = MagicMock(return_value=[1, 2])
#     #     with patch('VendorBid.common.get_descendant_category_ids', mock_get_descendant_category_ids):
#     #         domain = get_rfp_general_search_domain(mock_env)
#     #
#     #     # Assert that the domain has been correctly set
#     #     self.assertIn(('state', '=', 'approved'), domain)
#     #     self.assertIn(('product_category_id', 'in', [1, 2]), domain)
#     #
#     # def test_format_response(self):
#     #     response = format_response('success', 'Operation was successful', {'key': 'value'})
#     #     self.assertEqual(response, {
#     #         'status': 'success',
#     #         'message': 'Operation was successful',
#     #         'data': {'key': 'value'}
#     #     })
#     #
#     # def test_format_labels(self):
#     #     formatted_labels = format_labels('image_1920', 'street', 'primary_contact_id')
#     #     self.assertIn('Logo', formatted_labels)
#     #     self.assertIn('Address Line 1', formatted_labels)
#     #     self.assertIn('Primary Contact', formatted_labels)
#     #
#     # def test_get_nice_error_message(self):
#     #     # Test for trade license number error
#     #     error_message = get_nice_error_message('trade_license_number', err_type='string_pattern_mismatch',
#     #                                            default="Default error")
#     #     self.assertEqual(error_message, "Trade License number should be a 8-20 characters long alphanumeric string")
#     #
#     #     # Test for TIN error
#     #     error_message = get_nice_error_message('vat', err_type='string_pattern_mismatch', default="Default error")
#     #     self.assertEqual(error_message, "TIN should be 16 digits long")
#
#
# if __name__ == '__main__':
#     unittest.main()



from unittest.mock import patch, MagicMock

from odoo import http
from odoo.tests.common import TransactionCase
from odoo.addons.VendorBid.utils.controller_utils import validate_email_address, \
    create_supplier_registration, generate_registration_url, get_rfp_general_search_domain, format_response, \
    format_labels, get_nice_error_message
class TestUtils(TransactionCase):

    def setUp(self):
        super().setUp()
        # Initialize dummy request
        self.dummy_env = MagicMock()
        self.dummy_request = MagicMock()
        self.dummy_request.env = MagicMock()

        # Replace the global `http.request`
        http.request = self.dummy_request

    def test_validate_email_address(self):
        """
        Test the validate_email_address function.
        """
        # Configure mock environment models for testing
        self.dummy_request.env['mail.blacklist'].sudo().search.return_value = False
        self.dummy_request.env['res.users'].sudo().search.return_value = False
        self.dummy_request.env['supplies.registration'].sudo().search.return_value = False

        # Valid email test
        valid_email = "valid@example.com"
        result = validate_email_address(http.request, valid_email)
        self.assertTrue(result[0])  # Should return True
        self.assertEqual(result[1], '')  # No error message expected

        # Blacklisted email test
        self.dummy_request.env['mail.blacklist'].sudo().search.return_value = MagicMock()  # Simulate blacklist match
        blacklisted_email = "blacklisted@example.com"
        result = validate_email_address(http.request, blacklisted_email)
        self.assertFalse(result[0])  # Should return False
        self.assertEqual(result[1], 'Email address is blacklisted')  # Expected error message

    # def test_create_supplier_registration(self):
    #     """
    #     Test create_supplier_registration with a mocked environment.
    #     """
    #     # Test data
    #     data = {
    #         'company_name': 'Test Company',
    #         'company_address': '123 Test Street',
    #         'vat': '1234567890',
    #         'primary_contact_id': {'email': 'primary@example.com', 'name': 'Primary Contact'},
    #         'finance_contact_id': {'email': 'finance@example.com', 'name': 'Finance Contact'},
    #         'authorized_contact_id': {'email': 'authorized@example.com', 'name': 'Authorized Contact'},
    #         'client_ref_ids': [
    #             {'email': 'client1@example.com', 'name': 'Client 1'},
    #             {'email': 'client2@example.com', 'name': 'Client 2'},
    #         ],
    #     }
    #
    #     # Mock the `supplies.contact` model
    #     mock_contact_model = self.dummy_env['supplies.contact'].sudo()
    #     existing_contact = MagicMock()  # Simulate an existing contact
    #     existing_contact.id = 100  # Simulated ID for existing contacts
    #
    #     # Define side effect: return existing contact based on email query
    #     def search_side_effect(query):
    #         if query[0][2] == "primary@example.com":  # Primary contact already exists
    #             return existing_contact
    #         elif query[0][2] == "client1@example.com":  # Client 1 already exists
    #             return existing_contact
    #         return False  # No match for other emails
    #
    #     mock_contact_model.search.side_effect = search_side_effect
    #
    #     # Mock the behavior for creating new contacts
    #     new_contact_mock = MagicMock()
    #     new_contact_mock.id = 200  # Simulated ID for newly created contacts
    #     mock_contact_model.create.return_value = new_contact_mock
    #
    #     # Mock the `supplies.registration` model
    #     mock_registration_model = self.dummy_env['supplies.registration'].sudo()
    #     new_registration_mock = MagicMock()  # Simulate a new registration
    #     mock_registration_model.create.return_value = new_registration_mock
    #
    #     # Call the function being tested
    #     result = create_supplier_registration(self.dummy_env, data)
    #
    #     # Assertions to verify correct behavior
    #     # 1. Verify `search` was called for each contact and client reference
    #     mock_contact_model.search.assert_any_call([('email', '=', 'primary@example.com')])
    #     mock_contact_model.search.assert_any_call([('email', '=', 'client1@example.com')])
    #
    #     # 2. Verify `create` was called for new contacts
    #     mock_contact_model.create.assert_any_call({'email': 'finance@example.com', 'name': 'Finance Contact'})
    #     mock_contact_model.create.assert_any_call({'email': 'authorized@example.com', 'name': 'Authorized Contact'})
    #
    #     # 3. Validate the data used in the `create` method for `supplies.registration`
    #     expected_registration_data = {
    #         'company_name': 'Test Company',
    #         'company_address': '123 Test Street',
    #         'vat': '1234567890',
    #         'primary_contact_id': 100,  # Existing contact ID
    #         'finance_contact_id': 200,  # Newly created contact ID
    #         'authorized_contact_id': 200,  # Newly created contact ID
    #         'client_ref_ids': [
    #             (4, 100),  # Existing client reference ID
    #             (0, 0, {'email': 'client2@example.com', 'name': 'Client 2'}),  # New client reference
    #         ],
    #     }
    #     mock_registration_model.create.assert_called_once_with(expected_registration_data)
    #
    #     # 4. Ensure the returned registration is correct
    #     self.assertEqual(result, new_registration_mock)