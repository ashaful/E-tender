from odoo import models, fields, api

class ResBank(models.Model):
    """
    Extends the res.bank model to include international banking identifiers.

    Fields:
        swift_code (Char): The SWIFT (Society for Worldwide Interbank Financial Telecommunication) code
                           used for international wire transfers to identify banks globally.
        iban (Char): The IBAN (International Bank Account Number) used to uniquely identify a
                     customer’s bank account across international borders.

    Purpose:
        - To store additional banking details required for cross-border transactions.
        - To support financial compliance and smoother integration with external banking systems.
        - To improve vendor and customer payment processing by capturing critical international payment identifiers.
    """
    _inherit = 'res.bank'

    swift_code = fields.Char(string='SWIFT Code')
    iban = fields.Char(string='IBAN')
