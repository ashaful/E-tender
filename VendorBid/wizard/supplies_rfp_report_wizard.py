from odoo import models, fields, api
from ..utils import report_utils as utils

class RfpReportWizard(models.TransientModel):
    _name = 'supplies.rfp.report.wizard'
    _description = 'RFP Report Wizard'
    _rec_name = 'display_name'

    supplier_id = fields.Many2one('res.partner', string='Supplier', domain="[('supplier_rank', '>', 0)]")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    excel_report = fields.Binary(string='Excel Report File', readonly=True)
    company_logo = fields.Image(max_width=200, max_height=200, string='Company Logo')
    html_preview = fields.Html('Report Preview', readonly=True)

    def _compute_display_name(self):
        for record in self:
            record.display_name = 'Generate RFP Report'

    def _check_fields_for_report(self):
        """
        Check if all the requried fields are filled correctly
        """
        if not all([self.supplier_id, self.start_date, self.end_date]):
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Please fill all the fields.',
                    'type': 'danger',
                    'sticky': False,
                }
            }
        if self.start_date > self.end_date:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Start date should be less than end date.',
                    'type': 'danger',
                    'sticky': False,
                }
            }
        if not self.env.company.logo:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'Please upload the company logo in the company settings.',
                    'type': 'danger',
                    'sticky': False,
                }
            }
        self.company_logo = self.env.company.logo
        return True

    def _get_accepted_rfps(self):
        accepted_rfps = self.env['supplies.rfp'].search([
            ('approved_supplier_id', '=', self.supplier_id.id),
            ('state', '=', 'accepted'),
            ('date_approve', '>=', self.start_date),
            ('date_approve', '<=', self.end_date)
        ])
        return accepted_rfps

    def action_download_excel_report(self):
        """
        Downloads the excel report for the selected supplier and date range
        """
        check = self._check_fields_for_report()
        if isinstance(check, dict):
            return check
        accepted_rfps = self._get_accepted_rfps()
        if not accepted_rfps:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': 'No accepted RFPs found for the selected supplier for the specified interval.',
                    'type': 'danger',
                    'sticky': False,
                }
            }
        self.excel_report = utils.generate_excel_report(self.env, self.supplier_id, accepted_rfps, self.company_logo)
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s/%s?download=true' % (self._name, self.id, 'excel_report'),
            'target': 'self',
        }

    def action_preview_html(self):
        """
        Preview the report in HTML format
        """
        check = self._check_fields_for_report()
        if isinstance(check, dict):
            return check
        accepted_rfps = self._get_accepted_rfps()
        if not accepted_rfps:
            self.html_preview = utils.get_error_response_html()
            return
        try:
            self.html_preview = utils.generate_html_preview(self.env, self.supplier_id, accepted_rfps)
        except Exception as e:
            print(e, flush=True)
            self.html_preview = utils.get_error_response_html('Failed to generate the report')

