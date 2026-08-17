from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SuppliesRequest(models.Model):
    _name = 'supplies.request'
    _inherit = ['mail.thread']
    _description = 'Procurement Request'
    _rec_name = 'request_number'

    request_number = fields.Char(default='New', readonly=True, copy=False, tracking=True)
    request_date = fields.Date(default=fields.Date.context_today, readonly=True, tracking=True)
    requester_id = fields.Many2one('res.users', default=lambda self: self.env.user, required=True, tracking=True)
    department = fields.Char(tracking=True)
    request_category = fields.Selection(
        [('product', 'Product'), ('service', 'Service'), ('work', 'Work')],
        required=True,
        tracking=True,
    )
    title = fields.Char(required=True, tracking=True)
    business_justification = fields.Text(required=True)
    description = fields.Text(string='Detailed Specification', required=True)
    estimated_budget = fields.Monetary()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    delivery_location = fields.Char()
    vendor_category_id = fields.Many2one('product.category', string='Recommended Vendor Category')
    attachment = fields.Binary(string='Supporting Attachment')
    attachment_filename = fields.Char()
    approver_id = fields.Many2one('res.users', tracking=True)
    decision_reason = fields.Text(tracking=True)
    rfp_id = fields.Many2one('supplies.rfp', readonly=True, copy=False)
    line_ids = fields.One2many('supplies.request.line', 'request_id', string='Request Lines')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('correction', 'Correction Required'),
        ],
        default='draft',
        readonly=True,
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('request_number', 'New') == 'New':
                vals['request_number'] = self.env['ir.sequence'].next_by_code('supplies.request.number') or 'New'
        return super().create(vals_list)

    def _check_ready(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_('Please add at least one request line.'))
            if any(line.quantity <= 0 for line in rec.line_ids):
                raise UserError(_('Request line quantity must be greater than zero.'))

    def action_submit(self):
        self._check_ready()
        self.write({'state': 'submitted'})

    def action_approve(self):
        for rec in self:
            if rec.requester_id == self.env.user and not self.env.user.has_group('VendorBid.group_supplies_approver'):
                raise UserError(_('Requester cannot approve their own request.'))
            rec.write({'state': 'approved', 'approver_id': self.env.user.id})

    def action_reject(self):
        for rec in self:
            if not rec.decision_reason:
                raise UserError(_('Please enter a rejection reason before rejecting.'))
            rec.write({'state': 'rejected', 'approver_id': self.env.user.id})

    def action_return_for_correction(self):
        for rec in self:
            if not rec.decision_reason:
                raise UserError(_('Please enter a correction reason before returning.'))
            rec.write({'state': 'correction', 'approver_id': self.env.user.id})

    def action_create_rfp(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_('Only approved requests can be converted to an RFP.'))
        if self.rfp_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'supplies.rfp',
                'view_mode': 'form',
                'res_id': self.rfp_id.id,
            }
        rfp_lines = []
        for line in self.line_ids:
            rfp_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'description': line.description,
                'product_qty': line.quantity,
                'product_uom': line.product_uom_id.id,
            }))
        rfp = self.env['supplies.rfp'].create({
            'request_id': self.id,
            'product_category_id': self.vendor_category_id.id,
            'rfp_title': self.title,
            'scope': self.description,
            'business_justification': self.business_justification,
            'delivery_location': self.delivery_location,
            'currency_id': self.currency_id.id,
            'product_line_ids': rfp_lines,
        })
        self.rfp_id = rfp.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'supplies.rfp',
            'view_mode': 'form',
            'res_id': rfp.id,
        }


class SuppliesRequestLine(models.Model):
    _name = 'supplies.request.line'
    _description = 'Procurement Request Line'

    request_id = fields.Many2one('supplies.request', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', required=True)
    description = fields.Text()
    quantity = fields.Float(required=True, default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='UoM')
    required_date = fields.Date(required=True)
    expected_price = fields.Monetary()
    currency_id = fields.Many2one(related='request_id.currency_id')
