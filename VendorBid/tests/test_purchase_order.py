import base64

from odoo import fields
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class TestPurchaseOrder(TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test Supplier',
            'email': 'test@supplier.com'
        })

        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'consu'
        })

        self.rfp = self.env['supplies.rfp'].create({
            'state': 'draft',
        })

        self.rfp_line = self.env['supplies.rfp.product.line'].create({
            'rfp_id': self.rfp.id,
            'product_id': self.product.id,
        })

        self.rfq = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'rfp_id': self.rfp.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'name': self.product.name,
                'product_qty': 1,
                'price_unit': 1000,
                'delivery_charge': 100
            })],
            'warrenty_period': 12,
            'score': 70,
            'decision_reason': 'Best overall commercial and technical evaluation.',
            'signed_quotation_doc': base64.b64encode(b'signed quotation'),
            'technical_proposal_doc': base64.b64encode(b'technical proposal'),
            'experience_evidence_doc': base64.b64encode(b'experience evidence'),
        })

    def test_system_score_computation(self):
        """Ensure system_score is computed correctly based on order_line values and warranty"""
        self.rfq._compute_system_score()
        self.assertGreater(self.rfq.system_score, 0)
        self.assertLessEqual(self.rfq.system_score, 100)

    def test_negative_score_validation(self):
        """Ensure writing a negative score raises a ValidationError"""
        with self.assertRaises(ValidationError):
            self.rfq.write({'score': -10})

    def test_recommendation_constraint(self):
        """Ensure only one recommendation per supplier per RFP"""
        self.rfq.recommended = True
        with self.assertRaises(UserError):
            self.env['purchase.order'].create({
                'partner_id': self.partner.id,
                'rfp_id': self.rfp.id,
                'recommended': True
            })

    def test_action_accept(self):
        """Ensure action_accept updates state, confirms RFQ, and cancels others"""
        # Create second RFQ to be cancelled
        another_supplier = self.env['res.partner'].create({'name': 'Another Supplier'})
        other_rfq = self.env['purchase.order'].create({
            'partner_id': another_supplier.id,
            'rfp_id': self.rfp.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'name': self.product.name,
                'product_qty': 1,
                'price_unit': 1500,
                'delivery_charge': 200
            })],
        })

        result = self.rfq.action_accept()

        self.assertEqual(self.rfp.state, 'awarded')
        self.assertEqual(self.rfp.approved_supplier_id.id, self.rfq.partner_id.id)
        self.assertEqual(other_rfq.state, 'cancel')

        self.assertEqual(result['res_model'], 'supplies.rfp')
        self.assertEqual(result['res_id'], self.rfp.id)

    def test_open_accept_wizard(self):
        result = self.rfq.action_open_accept_wizard()

        self.assertEqual(result['res_model'], 'supplies.bid.decision.wizard')
        self.assertEqual(result['target'], 'new')
        self.assertEqual(result['context']['default_purchase_order_id'], self.rfq.id)
        self.assertEqual(result['context']['default_decision'], 'accepted')

    def test_last_changed_status_date_update(self):
        """Ensure last_changed_status_date is computed when RFQ status changes"""
        original_date = self.rfq.last_changed_status_date
        self.rfq.state = 'purchase'
        self.rfq._compute_last_changed_status_date()
        self.assertEqual(self.rfq.last_changed_status_date, fields.Datetime.today())
