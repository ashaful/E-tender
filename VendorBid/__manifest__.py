# -*- coding: utf-8 -*-
{
    'name': "VendorBid",

    'summary': "Register vendors, Create & Manage RFPs, Manage RFQ submitted by vendors",

    'description': """
        This module is designed to efficiently manage suppliers and Requests for Proposals (RFPs).
        It allows users to create and manage RFPs, invite suppliers to submit bids, and evaluate the responses.
        The system facilitates the selection of suppliers, negotiation, and finalizing contracts, streamlining the procurement process.
    """,

    'author': "BJIT Limited",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['purchase', 'website','contacts'],
    'live_test_url': 'https://vendorbid.app-odoo.bjitgroup.org/app/preview',
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'website': "https://odoo.bjitgroup.com/",
    'application': True,


    # always loaded
    'data': [
        'security/supplies_security.xml',
        'security/ir.model.access.csv',
        'wizard/supplies_rfp_report_wizard_views.xml',
        'wizard/supplies_bid_decision_wizard_views.xml',
        'views/views.xml',
        'views/website_views.xml',
        'views/templates.xml',
        'views/email_templates.xml',
        'views/supplies_registration_views.xml',
        'views/supplies_document_requirement_views.xml',
        'views/supplies_request_views.xml',
        'views/supplies_rfp_views.xml',
        'views/supplies_requester_views.xml',
        'views/supplies_menus.xml',
        'views/mail_blacklist_inherit.xml',
        'views/ir_sequence.xml',
        'views/res_bank_views.xml',
        'views/res_partner_views.xml',
        'views/res_partner_bank_views.xml',
        'views/purchase_order_views.xml',
        'views/portal_templates.xml',
        'views/partner_edit_request_views.xml',
        'report/supplies_rfp_templates.xml',
        'wizard/supplies_blacklist_wizard_view.xml',
        'wizard/supplies_reject_application_wizard_views.xml',
        'wizard/supplies_reject_application_wizard_views.xml',
        'data/cron.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/products.xml',
        'demo/demo_users.xml',
        'demo/suppliers.xml',
        'demo/res.partner.csv',
        'demo/res.bank.csv',
        'demo/res.partner.bank.csv',
        'demo/supplies.contact.csv',
        'demo/supplies.registration.csv',
        'demo/registration_extra.xml',
        'demo/supplies.rfp.csv',
        'demo/mail.blacklist.csv',
        'demo/supplies.rfp.product.line.csv',
        'demo/purchase.order.csv',
        'demo/purchase.order.line.csv',
        'demo/supplies_requester.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'web/static/lib/jquery/jquery.js',
            'VendorBid/static/src/js/registration.js',
        ],
        'web.assets_backend': [
            'VendorBid/static/src/components/**/*.js',
            'VendorBid/static/src/components/**/*.xml',
            'VendorBid/static/src/components/**/*.scss',
        ],
    },
    'test': ['tests/test_supplies_rfp.py'],
}
