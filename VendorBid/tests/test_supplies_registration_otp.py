from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.fields import Datetime
from datetime import timedelta

class TestRegistrationOTP(TransactionCase):

    def setUp(self):
        super().setUp()
        self.now = Datetime.now()
        self.email = "otp_test@example.com"

        self.otp_record = self.env['supplies.registration.otp'].create({
            'email': self.email,
        })

    def test_otp_is_generated(self):
        self.assertTrue(self.otp_record.otp)
        self.assertEqual(len(self.otp_record.otp), 6)
        self.assertTrue(self.otp_record.otp.isdigit())

    def test_default_expiry_is_5_minutes(self):
        expected_expiry = self.otp_record.create_date + timedelta(minutes=5)
        actual_expiry = self.otp_record.expiry_time
        diff = abs((expected_expiry - actual_expiry).total_seconds())
        self.assertLess(diff, 2, "OTP expiry should be ~5 minutes from creation")

    def test_verify_otp_success(self):
        result = self.otp_record.verify_otp()
        self.assertTrue(result)
        self.assertTrue(self.otp_record.is_verified)

    def test_verify_otp_expired(self):
        # Simulate expiry by backdating the expiry time
        self.otp_record.expiry_time = self.now - timedelta(minutes=10)
        result = self.otp_record.verify_otp()
        self.assertFalse(result)
        self.assertFalse(self.otp_record.is_verified)

    def test_verify_otp_already_verified(self):
        self.otp_record.is_verified = True
        result = self.otp_record.verify_otp()
        self.assertFalse(result)

    def test_send_otp_email_runs_without_error(self):
        """
        This test simply confirms the method executes.
        It won't assert an email was actually sent (no patching).
        """
        template = self.env.ref('VendorBid.email_template_model_bjit_supplies_registration_otp', raise_if_not_found=False)
        if template:
            try:
                self.otp_record.send_otp_email()
            except Exception as e:
                self.fail(f"send_otp_email raised an exception: {e}")
        else:
            self.skipTest("Email template not available in test database.")
