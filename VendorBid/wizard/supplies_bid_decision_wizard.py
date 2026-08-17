from odoo import _, fields, models


class SuppliesBidDecisionWizard(models.TransientModel):
    _name = 'supplies.bid.decision.wizard'
    _description = 'Bid Decision Wizard'

    purchase_order_id = fields.Many2one('purchase.order', required=True, readonly=True)
    decision = fields.Selection(
        [
            ('accepted', 'Accept Bid'),
            ('rejected', 'Reject Bid'),
            ('clarification', 'Request Clarification'),
        ],
        required=True,
        readonly=True,
    )
    reason = fields.Text(string='Decision Reason', required=True)

    def action_confirm_decision(self):
        self.ensure_one()
        order = self.purchase_order_id
        order.write({'decision_reason': self.reason})

        if self.decision == 'accepted':
            return order.action_accept()
        if self.decision == 'rejected':
            order.action_bid_reject()
        else:
            order.action_bid_clarification()
        return {'type': 'ir.actions.act_window_close'}
