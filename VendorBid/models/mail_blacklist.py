from odoo import models, fields, api

class BlackList(models.Model):
    """
    Inherits the 'mail.blacklist' model to add a reason field for blacklisting.

    This extension introduces an additional field `reason` that allows users
    to specify or record why an email address was blacklisted. By default,
    the reason is set to "Blacklisted".

    Attributes
    ----------
    reason : Char
        A textual field storing the reason for blacklisting the email.
        Defaults to "Blacklisted".
    """
    _inherit = 'mail.blacklist'

    reason = fields.Char(string='Reason', default='Blacklisted')
