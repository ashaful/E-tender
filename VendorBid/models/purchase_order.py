from logging import exception

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from ..utils.mail_utils import get_smtp_server_email


class PurchaseOrder(models.Model):
    """
    Inherits the 'purchase.order' model to integrate with the RFP (Request for Purchase)
    process, extend functionality for evaluating supplier proposals, and provide
    recommendation and scoring mechanisms.

    Enhancements include:
    ---------------------
    - Link to an RFP via `rfp_id`
    - Additional evaluation fields like `warrenty_period`, `score`, `system_score`, and `recommended`
    - Computation of a `system_score` based on price, delivery charge, and warranty period
    - Constraint to ensure only one recommendation per supplier per RFP
    - Automation for accepting an RFQ and updating related RFP and other RFQs
    - Tracking when the RFQ status last changed

    Fields
    ------
    rfp_id : Many2one
        Reference to the related RFP (supplies.rfp).

    warrenty_period : Integer
        Warranty period offered by the supplier, measured in months.

    score : Float
        Manual score for evaluation purposes, default is 0.

    system_score : Float (computed)
        Computed score based on normalized price, delivery charge, and warranty.

    recommended : Boolean
        Flag to mark the purchase order as recommended.

    last_changed_status_date : Datetime (computed & stored)
        Records the last date when the RFQ status changed.

    Methods
    -------
    _compute_last_changed_status_date()
        Sets the last_changed_status_date to today's date whenever the RFQ state changes.

    action_accept()
        Accepts the RFQ, confirms the PO, updates the RFP product lines,
        and cancels competing RFQs for the same RFP.

    _check_recommended()
        Ensures that a supplier is not recommended more than once for the same RFP.

    get_purchase_order_sudo(domain, fields)
        Sudo-enabled method to fetch purchase orders with specified domain and fields.

    write(vals)
        Overrides write to ensure that score cannot be set to a negative value.

    _compute_system_score()
        Calculates a weighted system score:
        - 40% weight for normalized price (lower is better),
        - 30% for normalized delivery charge (lower is better),
        - 30% for normalized warranty period (higher is better).

    Raises
    ------
    UserError:
        If a supplier is marked as recommended more than once for a given RFP.

    ValidationError:
        If an attempt is made to write a negative score.
    """
    _inherit = 'purchase.order'

    rfp_id = fields.Many2one('supplies.rfp', string='RFP', index=True, copy=False)
    warrenty_period = fields.Integer(string='Warrenty Period (in months)')
    score = fields.Float(string='Score', default=0)
    system_score = fields.Float(string='System Score', compute='_compute_system_score')
    recommended = fields.Boolean(string='Recommended', default=False)
    bid_submitted_at = fields.Datetime(string='Bid Submitted At', readonly=True, copy=False)
    bid_decision = fields.Selection(
        [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('clarification', 'Clarification Required')],
        default='pending',
        tracking=True,
    )
    decision_reason = fields.Text(string='Decision Reason', tracking=True)
    signed_quotation_doc = fields.Binary(string='Signed Financial Quotation')
    signed_quotation_filename = fields.Char()
    technical_proposal_doc = fields.Binary(string='Technical Proposal / Compliance')
    technical_proposal_filename = fields.Char()
    experience_evidence_doc = fields.Binary(string='Relevant Experience Evidence')
    experience_evidence_filename = fields.Char()
    rfp_specific_doc = fields.Binary(string='RFP-Specific Mandatory Documents')
    rfp_specific_filename = fields.Char()
    last_changed_status_date = fields.Datetime(
        string='Last Updated Date of RFQ Status',
        compute='_compute_last_changed_status_date',
        store=True
    )

    @api.depends('state')
    def _compute_last_changed_status_date(self):
        for rfq in self:
            rfq.last_changed_status_date = fields.Date.today()

    def action_accept(self):
        if not self.decision_reason:
            raise UserError(_('Acceptance reason is required.'))
        self._validate_required_bid_documents()
        self.rfp_id.write({
            'state': 'awarded',
            'approved_supplier_id': self.partner_id.id,
            'date_accept': fields.Date.today()
        })
        self.bid_decision = 'accepted'
        self.button_confirm()
        # updating RFP product line prices
        for line in self.rfp_id.product_line_ids:
            rfq_line = self.order_line.filtered(lambda x: x.product_id == line.product_id)
            line.write({
                'unit_price': rfq_line.price_unit,
                'delivery_charge': rfq_line.delivery_charge,
            })
        # cancelling other RFQs
        other_rfqs = self.env['purchase.order'].search([
            ('rfp_id', '=', self.rfp_id.id),
            ('id', '!=', self.id),
        ])
        other_rfqs.write({'bid_decision': 'rejected', 'decision_reason': _('Another bid was selected.')})
        other_rfqs.button_cancel()
        self._send_bid_decision_email('VendorBid.email_template_bid_acceptance', 'Bid Accepted')
        other_rfqs._send_bid_decision_email('VendorBid.email_template_bid_non_selection', 'Bid Not Selected')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'supplies.rfp',
            'view_mode': 'form',
            'res_id': self.rfp_id.id,
            'target': 'current',
        }

    def _open_bid_decision_wizard(self, decision):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bid Decision'),
            'res_model': 'supplies.bid.decision.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_order_id': self.id,
                'default_decision': decision,
            },
        }

    def action_open_accept_wizard(self):
        return self._open_bid_decision_wizard('accepted')

    def action_open_reject_wizard(self):
        return self._open_bid_decision_wizard('rejected')

    def action_open_clarification_wizard(self):
        return self._open_bid_decision_wizard('clarification')

    def _validate_required_bid_documents(self):
        for order in self:
            missing = []
            if not order.signed_quotation_doc:
                missing.append(_('signed financial quotation'))
            if not order.technical_proposal_doc:
                missing.append(_('technical proposal/compliance document'))
            if not order.experience_evidence_doc:
                missing.append(_('relevant experience evidence'))
            if order.rfp_id.mandatory_bid_documents and not order.rfp_specific_doc:
                missing.append(_('RFP-specific mandatory documents'))
            if missing:
                raise ValidationError(_('Missing required bid document(s): %s') % ', '.join(missing))
        return True

    def action_bid_reject(self):
        for order in self:
            if not order.decision_reason:
                raise UserError(_('Rejection reason is required.'))
            order.write({'bid_decision': 'rejected'})
            order._send_bid_decision_email('VendorBid.email_template_bid_rejection', 'Bid Rejected')

    def action_bid_clarification(self):
        for order in self:
            if not order.decision_reason:
                raise UserError(_('Clarification reason is required.'))
            order.write({'bid_decision': 'clarification'})
            order._send_bid_decision_email('VendorBid.email_template_bid_clarification', 'Bid Clarification Required')

    def _send_bid_decision_email(self, template_xmlid, fallback_subject):
        template = self.env.ref(template_xmlid, raise_if_not_found=False)
        if not template:
            return
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for order in self.filtered(lambda po: po.partner_id.email):
            template.sudo().with_context(
                rfp_number=order.rfp_id.rfp_number,
                rfp_title=order.rfp_id.rfp_title,
                rfq_number=order.name,
                vendor_name=order.partner_id.name,
                decision_reason=order.decision_reason,
                company_name=order.company_id.name,
                portal_url=f'{base_url}/my/supplies/rfq/{order.name}',
            ).send_mail(order.id, email_values={
                'email_from': get_smtp_server_email(self.env),
                'email_to': order.partner_id.email,
                'subject': f'{fallback_subject}: {order.rfp_id.rfp_number}',
            })

    @api.constrains('recommended')
    def _check_recommended(self):
        for order in self:
            if order.recommended:
                existing_recommendation = self.env['purchase.order'].search([
                    ('recommended', '=', True),
                    ('rfp_id', '=', order.rfp_id.id),
                    ('partner_id', '=', order.partner_id.id),
                    ('id', '!=', order.id),
                ])
                if existing_recommendation:
                    raise UserError(
                        f'The supplier {order.partner_id.name} is recommended multiple times for the same RFP.'
                    )

    @api.model
    def get_purchase_order_sudo(self, domain, fields):
        return self.sudo().search_read(domain, fields)

    @api.model
    def write(self, vals):
        if 'score' in vals and vals['score'] is not None and vals['score'] < 0:
            raise ValidationError(_("Score of this RFQ can not be negative"))
        return super(PurchaseOrder, self).write(vals)

    @api.depends('order_line.price_unit', 'order_line.delivery_charge', 'warrenty_period')
    def _compute_system_score(self):
        for order in self:
            if not order.order_line:
                order.system_score = 0
                continue

            price = [line.price_unit for line in order.order_line]
            deliveries = [line.delivery_charge for line in order.order_line]
            warranty = order.warrenty_period or 0

            sum_price = sum(price)
            sum_delivery = sum(deliveries)

            max_price, max_delivery, max_warranty = 100000000, 1000000, 100

            normalized_price = min(sum_price / max_price, 1.0)
            normalized_delivery = min(sum_delivery / max_delivery, 1.0)
            normalized_warranty = min(warranty / max_warranty, 1.0)

            order.system_score = 100 * round(
                0.4 * (1 - normalized_price) +
                0.3 * (1 - normalized_delivery) +
                0.3 * normalized_warranty, 3)
