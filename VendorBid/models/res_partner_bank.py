from odoo import models, fields, api

class ResPartnerBank(models.Model):
    """
    Extends the res.partner.bank model to include additional banking information.

    Fields:
        branch_address (Char): The physical address of the bank branch associated with this bank account.

    Purpose:
        - To store branch-level banking details for suppliers or customers.
        - Enhances financial verification and documentation processes.
    """
    _inherit = 'res.partner.bank'

    branch_address = fields.Char(string='Branch Address')
