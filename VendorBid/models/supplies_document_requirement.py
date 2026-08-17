from odoo import models, fields, _
from odoo.exceptions import UserError


class SuppliesDocumentRequirement(models.Model):
    _name = 'supplies.document.requirement'
    _description = 'Vendor Document Requirement'
    _order = 'vendor_category_id, sequence, name'

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    vendor_category_id = fields.Many2one('product.category', required=True, ondelete='cascade')
    document_field = fields.Selection(
        [
            ('trade_license_doc', 'Trade License'),
            ('vat_tax_certificate_doc', 'TIN / VAT / BIN Certificate'),
            ('certificate_of_incorporation_doc', 'Incorporation / Registration Certificate'),
            ('past_2_years_financial_statement_doc', 'Financial Statement / Turnover Evidence'),
            ('bank_letter_doc', 'Bank Account Evidence'),
            ('identification_of_authorised_person_doc', 'Authorized Person Evidence'),
            ('memorandum_of_association_doc', 'Company Profile / Memorandum'),
            ('certificate_of_good_standing_doc', 'Relevant Experience Evidence'),
            ('other_certification_doc', 'Other Certification / RFP Evidence'),
            ('company_stamp', 'Company Stamp'),
        ],
        required=True,
    )
    required = fields.Boolean(default=True)
    active = fields.Boolean(default=True)

    def _get_missing_for_partner(self, partner):
        missing = []
        for requirement in self.filtered('required'):
            if not getattr(partner, requirement.document_field, False):
                missing.append(requirement.name)
        return missing

    def action_validate_category_vendors(self):
        for requirement in self:
            vendors = self.env['res.partner'].search([
                ('supplier_rank', '>', 0),
                ('product_category_id', 'child_of', requirement.vendor_category_id.id),
            ])
            missing = []
            for vendor in vendors:
                if not getattr(vendor, requirement.document_field, False):
                    missing.append(vendor.display_name)
            if missing:
                raise UserError(_('Missing %s for vendors: %s') % (requirement.name, ', '.join(missing[:20])))
        return True
