from odoo.tests.common import TransactionCase

class TestMailBlacklist(TransactionCase):

    def test_create_blacklist_with_reason(self):
        blacklist = self.env['mail.blacklist'].create(
            {
                'email':'test@example.com',
                'reason':'Too many request'
            }
        )
        print(blacklist.create_uid)
        self.assertEqual(blacklist.reason,'Too many request')
        self.assertEqual(blacklist.email,'test@example.com')
