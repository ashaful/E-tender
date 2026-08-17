from odoo.tests.common import HttpCase, tagged
from odoo import fields
from unittest.mock import patch
import json
from ..utils.controller_utils import validate_email_address
from ..utils import mail_utils
from .. import utils




@tagged('-at_install', 'post_install')
class TestSendOtpController(HttpCase):

    def test_invalid_email(self):
        payload = {"email": "invalid-email"}
        with patch('utils.validate_email_address', return_value=(False, "Invalid Email")):
            response = self.url_open(
                '/supplies/register/send-otp',
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                method="POST"
            )
            data = json.loads(response.content)
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Invalid Email')

    # def test_rate_limit(self):
    #     email = "test@example.com"
    #
    #     # Create 5 valid, unexpired OTPs
    #     OTP = self.env['supplies.registration.otp']
    #     for _ in range(5):
    #         OTP.sudo().create({
    #             'email': email,
    #             'expiry_time': fields.Datetime.now() + fields.timedelta(minutes=5)
    #         })
    #
    #     with patch('VendorBid.utils.validate_email_address', return_value=(True, "")):
    #         payload = {"email": email}
    #         response = self.url_open(
    #             '/supplies/register/send-otp',
    #             data=json.dumps(payload),
    #             headers={'Content-Type': 'application/json'},
    #             method="POST"
    #         )
    #         data = json.loads(response.content)
    #         self.assertEqual(data['status'], 'error')
    #         self.assertIn('Maximum number of OTPs', data['message'])
    #
    # def test_successful_otp_send(self):
    #     email = "success@example.com"
    #     with patch('VendorBid.utils.validate_email_address', return_value=(True, "")), \
    #          patch('odoo.addons.VendorBid.models.otp.SuppliesRegistrationOtp.send_otp_email', return_value=True):
    #         payload = {"email": email}
    #         response = self.url_open(
    #             '/supplies/register/send-otp',
    #             data=json.dumps(payload),
    #             headers={'Content-Type': 'application/json'},
    #             method="POST"
    #         )
    #         data = json.loads(response.content)
    #         self.assertEqual(data['status'], 'success')
    #         self.assertIn('OTP sent successfully', data['message'])
    #
    # def test_send_failure(self):
    #     email = "fail@example.com"
    #     with patch('VendorBid.utils.validate_email_address', return_value=(True, "")), \
    #          patch('odoo.addons.VendorBid.models.otp.SuppliesRegistrationOtp.send_otp_email', side_effect=Exception("SMTP error")):
    #         payload = {"email": email}
    #         response = self.url_open(
    #             '/supplies/register/send-otp',
    #             data=json.dumps(payload),
    #             headers={'Content-Type': 'application/json'},
    #             method="POST"
    #         )
    #         data = json.loads(response.content)
    #         self.assertEqual(data['status'], 'error')
    #         self.assertEqual(data['message'], 'Failed to send OTP')
