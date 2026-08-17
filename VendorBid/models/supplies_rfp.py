from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from ..utils.rfp_utils import rfp_state_flow
from ..utils.mail_utils import get_smtp_server_email, get_approver_emails, get_supplier_emails


class SuppliesRfp(models.Model):
    """
    Model: supplies.rfp (Request for Purchase)

    This model handles the lifecycle of a Request for Purchase (RFP) from creation to approval and final closure.
    It integrates with reviewers and suppliers, manages email notifications for different state transitions,
    and links with RFQs (Request for Quotations) and Purchase Orders.

    Key Features:
    - Tracks RFP states (Draft, Submitted, Rejected, Approved, Closed, Recommendation, Accepted).
    - Automatically generates unique RFP numbers using a sequence.
    - Allows adding multiple product lines and calculates total amount.
    - Sends email notifications to reviewers and suppliers during state transitions.
    - Supports user permission-based visibility (e.g., reviewer and requester access).
    - Provides actions to view RFQs and Purchase Orders related to the RFP.
    - Ensures only recommended RFQs can proceed to the recommendation stage.
    - Custom visibility logic using computed and searchable fields.
    - Integrates with external utilities: rfp_state_flow decorator, mail utilities.

    Linked Models:
    - `supplies.rfp.product.line`: Product lines added to the RFP.
    - `purchase.order`: RFQs linked to this RFP.
    - `res.partner`: Approved supplier.
    - `res.users`: Reviewers and submitters.

    Security Groups:
    - `group_supplies_requester`: Users who can submit RFPs.
    - `group_supplies_approver`: Users who can approve or reject RFPs.
    """

    _name = 'supplies.rfp'
    _inherit = ['mail.thread']
    _description = 'Request for Purchase'
    _rec_name = 'rfp_number'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('recommendation', 'Recommendation'),
        ('accepted', 'Accepted'),
        ('awarded', 'Awarded'),
        ('cancelled', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    rfp_number = fields.Char(string='RFP Number', readonly=True, index=True, copy=False, default='New')
    request_id = fields.Many2one('supplies.request', string='Source Request', tracking=True, copy=False)
    rfp_title = fields.Char(string='RFP Title', tracking=True)
    visibility = fields.Selection(
        [('public', 'Public'), ('private', 'Private')],
        default='public',
        required=True,
        tracking=True,
    )
    selected_vendor_ids = fields.Many2many('res.partner', string='Selected Private Vendors')
    publish_date = fields.Datetime(readonly=True, copy=False, tracking=True)
    submission_deadline = fields.Datetime(string='Bid Submission Deadline', tracking=True)
    old_submission_deadline = fields.Datetime(readonly=True, copy=False)
    deadline_extension_reason = fields.Text()
    cancellation_reason = fields.Text(tracking=True)
    scope = fields.Text(string='Scope / Technical Specification')
    business_justification = fields.Text()
    delivery_location = fields.Char()
    buyer_contact = fields.Char()
    eligibility_requirements = fields.Text()
    payment_terms = fields.Text()
    bid_validity = fields.Char()
    pricing_instruction = fields.Text()
    mandatory_bid_documents = fields.Text()
    terms_conditions = fields.Text()
    attachment = fields.Binary(string='RFP Attachment')
    attachment_filename = fields.Char()
    required_date = fields.Date(string='Required Date', tracking=True,
                                default=lambda self: fields.Date.add(fields.Date.today(), days=7))
    approved_supplier_id = fields.Many2one('res.partner', string='Approved Supplier')
    product_line_ids = fields.One2many('supplies.rfp.product.line', 'rfp_id', string='Product Lines')
    rfq_ids = fields.One2many('purchase.order', 'rfp_id', string='RFQs', domain=lambda self: self._get_rfq_domain())
    num_rfq = fields.Integer(string='Number of RFQs', compute='_compute_num_rfq', store=True)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    date_approve = fields.Date(string='Reviewed On', readonly=True)  # when an approver either approves or rejects
    review_by = fields.Many2one('res.users', string='Review By',
                                readonly=True)  # an approver either approves or rejects
    date_accept = fields.Date(string='Accepted On', readonly=True)
    product_category_id = fields.Many2one('product.category', string="Product Category", store=True)
    total_rfq = fields.Integer(string='Number of RFQs', compute='_compute_total_rfq', store=False)
    visible_to_reviewer = fields.Boolean(compute='_compute_visible_to_reviewer', search='_search_visible_to_reviewer')
    submitted_by = fields.Many2one('res.users', string='Submitted By', readonly=True)

    def _compute_visible_to_reviewer(self):
        for rec in self:
            rec.visible_to_reviewer = self._is_visible_to_reviewer(rec)

    def _is_visible_to_reviewer(self, record):
        """
        Determines if a record (RFP) is visible to the current user (reviewer) based on specific conditions.

        Conditions:
        - If the record was created by the current user, it is visible to the user.
        - If the record was created by a user in the 'requester' group and is in 'draft' state, it is visible to the user.
        - If the record was submitted by the current user, it is visible to the user.

        Args:
            record (recordset): The RFP record being checked for visibility.

        Returns:
            bool: True if the record is visible to the current user, False otherwise.
        """
        requester_group = self.env.ref('VendorBid.group_supplies_requester')
        user = self.env.user

        # Check if the record was created by the current user
        if record.create_uid == user:
            return True

        # Check if the record was created by a user in the requester group and is in draft state or was submitted by the user
        if record.create_uid.has_group('VendorBid.group_supplies_requester'):
            if record.state == 'draft' or record.submitted_by == user:
                return True

        return False

    @api.model
    def _search_visible_to_reviewer(self, operator, value):
        """
        Returns the domain for searching records based on visibility to the current user (reviewer).

        This method is used to build the search domain for filtering RFPs that are visible to the current user
        based on the following conditions:
        - The current user is the creator of the RFP.
        - The current user is part of the 'requester' group and the RFP is in 'draft' state or was submitted by the user.

        Args:
            operator (str): The operator used in the search (either '=' or '!=').
            value (bool): The value indicating whether to include or exclude records that are visible to the current user.

        Returns:
            list: A domain to be used in the search query. If `value` is `True`, it returns the domain for visible records;
                  if `value` is `False`, it returns the inverse domain for non-visible records.

        Raises:
            UserError: If the operator is not '=' or '!=' or if the `value` is not a boolean.
        """
        # Ensure the operator is either '=' or '!=' and the value is a boolean
        if operator not in ['=', '!='] or not isinstance(value, bool):
            raise UserError("Unsupported search operation for visible_to_reviewer")

        requester_group = self.env.ref('VendorBid.group_supplies_requester')
        user = self.env.user

        # Construct the domain for the search query based on visibility conditions
        domain = ['|',
                  ('create_uid', '=', user.id),  # Record created by the current user
                  '&',
                  ('create_uid.groups_id', 'in', requester_group.id),
                  # Record created by someone in the requester group
                  '|',
                  ('state', '=', 'draft'),  # Record is in 'draft' state
                  ('submitted_by', '=', user.id)  # Record was submitted by the current user
                  ]

        # Return the domain depending on the value of the operator
        return domain if value else ['!', domain]

    def _compute_total_rfq(self):
        """
        Computes the total number of RFQs associated with the current RFP.
        This updates the 'total_rfq' field with the count of related RFQs.

        Args:
            self: The current instance of the RFP record.
        """
        for rec in self:
            rec.total_rfq = len(rec.rfq_ids)

    def action_view_all_rfq(self):
        """
                Returns an action to open a list view of all RFQs related to the current RFP.

                Depending on the user's group and the RFQ state, the domain will filter the RFQs.

                If the user is an approver, it filters for recommended RFQs only.
                Otherwise, it shows all RFQs associated with the RFP.

                Args:
                    self: The current instance of the RFP record.

                Returns:
                    dict: The action dictionary to open the RFQs in the appropriate view.
        """
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        if self.env.user.has_group('VendorBid.group_supplies_approver'):
            action['domain'] = [('rfp_id', '=', self.id), ('recommended', '=', True)]
            return action
        action['domain'] = [('rfp_id', '=', self.id)]
        return action

    @api.depends('product_line_ids', 'product_line_ids.subtotal_price')
    def _compute_total_amount(self):
        """
            Computes the total amount for the current RFP by summing the 'subtotal_price'
                of all product lines associated with the RFP.

            Args:
                self: The current instance of the RFP record.
        """
        for rfp in self:
            rfp.total_amount = sum(rfp.product_line_ids.mapped('subtotal_price'))

    @api.model
    def _get_rfq_domain(self):
        """
        Returns the domain to filter RFQs based on the current user's group and the RFP's state.

        If the user is an approver, it returns a domain to filter RFQs where the recommendation is true,
        but only if the RFP's state allows it.

        Args:
            self: The current instance of the RFP record.

        Returns:
            list: A domain list for filtering RFQs.
        """
        aprrover_states = ['recommendation', 'accepted']
        if self.env.user.has_group('VendorBid.group_supplies_approver'):
            return [('recommended', '=', True)] if self.state in aprrover_states else [('id', '=', -1)]
        return []

    @api.model_create_multi
    def create(self, vals_list):
        """
        Overrides the create method to assign a unique sequence number to the 'rfp_number' field if it's set to 'New'.

        Args:
            vals_list (list): List of dictionaries containing the RFP values to be created.

        Returns:
            recordset: The created RFP records.
        """
        for vals in vals_list:
            if vals.get('rfp_number', 'New') == 'New':
                vals['rfp_number'] = self.env['ir.sequence'].next_by_code('supplies.rfp.number') or 'New'
        return super(SuppliesRfp, self).create(vals_list)

    def write(self, vals):
        if 'submission_deadline' in vals:
            for rec in self:
                old_deadline = rec.submission_deadline
                new_deadline = vals.get('submission_deadline')
                if old_deadline and new_deadline and old_deadline != new_deadline:
                    rec.old_submission_deadline = old_deadline
                    rec.message_post(body='Submission deadline changed from %s to %s.' % (old_deadline, new_deadline))
        return super().write(vals)

    @api.depends('rfq_ids')
    def _compute_num_rfq(self):
        """
        Compute the number of RFQs associated with the current updates the 'num_rfq' field.
        Args:
            self: The current instance of the RFP record.
        """
        for rfp in self:
            rfp.num_rfq = len(rfp.rfq_ids)

    @rfp_state_flow('draft')
    def action_submit(self):
        """
        Submits the RFP, performs validation checks, and updates the RFP state to 'submitted'.
        Sends email notifications to the approvers and others involved in the submission process.

        Raises:
            UserError: If no product lines or invalid quantities are provided.

        Args:
            self: The current instance of the RFP record.
        """
        if not self.product_line_ids:
            raise UserError('Please add product lines before submitting.')

        if not all(self.product_line_ids.mapped('product_qty')):
            raise UserError('Product quantity must be greater than 0')
        if self.request_id and self.request_id.state != 'approved':
            raise UserError('Only approved source requests can be used for an RFP.')

        self.write({'state': 'submitted', 'submitted_by': self.env.user.id,
                    'product_category_id': self.product_category_id.id, })

        email_values = {
            'email_from': get_smtp_server_email(self.env),
            'email_to': get_approver_emails(self.env),
            'subject': f'New RFP Submitted {self.rfp_number}',
        }
        contexts = {
            'reviwer_name': self.env.user.name,
            'company_name': self.env.company.name,
        }
        template = self.env.ref('VendorBid.email_template_model_supplies_rfp_submission').sudo()
        template.with_context(**contexts).send_mail(self.id, email_values=email_values)

    @rfp_state_flow('rejected', 'submitted')
    def action_return_to_draft(self):
        """
        Returns the RFP to the 'draft' state from 'rejected' or 'submitted' states.

        Args:
            self: The current instance of the RFP record.
        """
        self.state = 'draft'

    @rfp_state_flow('submitted')
    def action_approve(self):
        """
        Approves the RFP, updates the state to 'approved', and sends email notifications to the reviewer and suppliers.

        Args:
            self: The current instance of the RFP record.
        """
        self.write({'state': 'approved', 'date_approve': fields.Date.today(), 'review_by': self.env.user.id})
        # notify reviewer
        email_values = {
            'email_from': get_smtp_server_email(self.env),
            'email_to': self.create_uid.login,
            'subject': f'RFP Approved {self.rfp_number}',
        }
        contexts = {
            'rfp_number': self.rfp_number,
            'company_name': self.env.company.name,
        }
        template = self.env.ref('VendorBid.email_template_model_supplies_rfp_approved_reviewer').sudo()
        template.with_context(**contexts).send_mail(self.id, email_values=email_values)

        self.message_post(body='RFP approved. Publish the RFP to notify eligible vendors.')

    def _validate_publication_ready(self):
        for rec in self:
            missing = []
            if not rec.submission_deadline:
                missing.append('submission deadline')
            if rec.submission_deadline and rec.submission_deadline <= fields.Datetime.now():
                raise UserError('Submission deadline must be in the future.')
            if not rec.product_category_id:
                missing.append('product category')
            if not rec.product_line_ids:
                missing.append('pricing/product lines')
            if not rec.rfp_title:
                missing.append('RFP title')
            if not rec.scope:
                missing.append('scope/specification')
            if rec.visibility == 'private' and not rec.selected_vendor_ids:
                missing.append('selected private vendors')
            if missing:
                raise UserError('Please set the following before publishing: %s.' % ', '.join(missing))

    @rfp_state_flow('approved')
    def action_publish(self):
        self._validate_publication_ready()
        for rec in self:
            rec.write({'state': 'published', 'publish_date': fields.Datetime.now()})
            rec.message_post(body='RFP published to portal.')
            rec._send_publication_invitations()

    def _get_invitation_vendors(self):
        self.ensure_one()
        if self.visibility == 'private':
            return self.selected_vendor_ids.filtered(
                lambda partner: partner.active and partner.supplier_rank > 0 and partner.vendor_document_complete
            )
        domain = [('supplier_rank', '>', 0), ('active', '=', True)]
        if self.product_category_id:
            domain.append(('product_category_id', 'child_of', self.product_category_id.id))
        return self.env['res.partner'].sudo().search(domain).filtered('vendor_document_complete')

    def _send_publication_invitations(self):
        template = self.env.ref('VendorBid.email_template_model_supplies_rfp_approved_supplier', raise_if_not_found=False)
        if not template:
            return
        sent = set()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        portal_url = f'{base_url}/my/supplies/{self.rfp_number}'
        public_url = f'{base_url}/supplies/rfp/{self.rfp_number}'
        login_url = f'{base_url}/web/login?redirect=/my/supplies/{self.rfp_number}'
        for vendor in self._get_invitation_vendors():
            if not vendor.email or vendor.email in sent:
                continue
            sent.add(vendor.email)
            template.sudo().with_context(
                rfp_number=self.rfp_number,
                rfp_title=self.rfp_title,
                company_name=self.env.company.name,
                deadline=self.submission_deadline,
                buyer_contact=self.buyer_contact,
                scope=self.scope,
                category=self.product_category_id.display_name,
                delivery_location=self.delivery_location,
                mandatory_bid_documents=self.mandatory_bid_documents,
                portal_url=portal_url,
                public_url=public_url if self.visibility == 'public' else portal_url,
                login_url=login_url,
            ).send_mail(self.id, email_values={
                'email_from': get_smtp_server_email(self.env),
                'email_to': vendor.email,
                'subject': f'Invitation to Bid: {self.rfp_number}',
            })
        if sent:
            self.message_post(body='Invitation email sent to %s vendor(s).' % len(sent))

    @rfp_state_flow('submitted')
    def action_reject(self):
        """
        Rejects the RFP, updates the state to 'rejected', and sends email notifications to the reviewer.

        Args:
            self: The current instance of the RFP record.
        """
        self.write({'state': 'rejected', 'review_by': self.env.user.id, 'date_approve': fields.Date.today()})
        email_values = {
            'email_from': get_smtp_server_email(self.env),
            'email_to': self.create_uid.login,
            'subject': f'RFP Rejected {self.rfp_number}',
        }
        contexts = {
            'rfp_number': self.rfp_number,
            'company_name': self.env.company.name,
            'approver_name': self.env.user.name,
        }
        template = self.env.ref('VendorBid.email_template_model_supplies_rfp_rejected_reviewer').sudo()
        template.with_context(**contexts).send_mail(self.id, email_values=email_values)

    @rfp_state_flow('approved', 'published')
    def action_close(self):
        """
        Closes the RFP, updating its state to 'closed'.

        Args:
            self: The current instance of the RFP record.
        """
        self.state = 'closed'

    def action_cancel(self):
        for rec in self:
            if not rec.cancellation_reason:
                raise UserError('Cancellation reason is required.')
            rec.write({'state': 'cancelled'})
            rec.message_post(body='RFP cancelled. Reason: %s' % rec.cancellation_reason)

    def action_extend_deadline(self):
        for rec in self:
            if not rec.deadline_extension_reason:
                raise UserError('Deadline extension reason is required.')
            if not rec.submission_deadline or rec.submission_deadline <= fields.Datetime.now():
                raise UserError('Revised deadline must be in the future.')
            rec.message_post(body='RFP deadline extended. Reason: %s' % rec.deadline_extension_reason)

    @api.constrains('submission_deadline')
    def _check_submission_deadline(self):
        for rec in self:
            if rec.state in ('published', 'approved') and rec.submission_deadline and rec.submission_deadline <= fields.Datetime.now():
                raise ValidationError('Submission deadline must be in the future.')

    @api.model
    def _cron_close_expired_rfps(self):
        expired = self.search([
            ('state', '=', 'published'),
            ('submission_deadline', '!=', False),
            ('submission_deadline', '<=', fields.Datetime.now()),
        ])
        for rfp in expired:
            rfp.write({'state': 'closed'})
            rfp.message_post(body='RFP automatically closed at submission deadline.')

    @rfp_state_flow('closed')
    def action_recommendation(self):
        """
        Changes the RFP state to 'recommendation' after at least one RFQ is approved.
        Sends an email notification to the approvers.

        Raises:
            UserError: If no RFQs have been approved.

        Args:
            self: The current instance of the RFP record.
        """
        approved_rfqs = self.rfq_ids.filtered(lambda rfq: rfq.recommended)
        if not approved_rfqs:
            raise UserError('Please approve at least one RFQ before recommending.')
        self.state = 'recommendation'
        email_values = {
            'email_from': get_smtp_server_email(self.env),
            'email_to': get_approver_emails(self.env),
            'subject': f'RFQ Recommendation for {self.rfp_number}',
        }
        contexts = {
            'rfp_number': self.rfp_number,
            'company_name': self.env.company.name,
        }
        template = self.env.ref('VendorBid.email_template_model_supplies_rfp_recommended').sudo()
        template.with_context(**contexts).send_mail(self.id, email_values=email_values)

    def action_view_purchase_order(self):
        """
        Returns an action to view the purchase order related to the current RFP.

        Args:
            self: The current instance of the RFP record.

        Returns:
            dict: The action dictionary to view the related purchase order.
        """
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = [('rfp_id', '=', self.id), ('recommended', '=', True),
                            ('partner_id', '=', self.approved_supplier_id.id)]
        return action

    @api.model
    def get_rfp_sudo(self, domain, fields):
        """
        Returns RFP records using sudo access based on the provided domain and fields.

        Args:
            domain (list): A list of conditions for filtering the RFP records.
            fields (list): A list of fields to retrieve from the RFP records.

        Returns:
            list: A list of RFP records based on the specified domain and fields.
        """
        return self.sudo().search_read(domain, fields)
