from odoo import fields, models, api

class AccountTax(models.Model):
    """
    Inherits the 'account.tax' model to customize tax base line computation
    by including delivery charges in the tax calculation.

    This customization overrides the `_prepare_base_line_for_taxes_computation`
    method to adjust the `price_unit` by distributing the `delivery_charge`
    (if present) across the quantity of the record being taxed.

    Methods
    -------
    _prepare_base_line_for_taxes_computation(record, **kwargs)
        Extends the base implementation to add delivery charge per unit
        to the price_unit, ensuring accurate tax computation.

    Parameters
    ----------
    record : recordset
        The record (typically invoice line or sale order line) for which
        tax computation is being prepared. Must optionally have a field
        `delivery_charge` to be effective.
    kwargs : dict
        Additional keyword arguments passed to the super method.

    Returns
    -------
    dict
        A dictionary representing the base line for tax computation with
        `price_unit` adjusted to include delivery charges if applicable.
    """
    _inherit = 'account.tax'

    @api.model
    def _prepare_base_line_for_taxes_computation(self, record, **kwargs):
        base_line = super(AccountTax, self)._prepare_base_line_for_taxes_computation(record, **kwargs)
        if deli_charge := getattr(record, 'delivery_charge', None):
            quantity = base_line.get('quantity', 0.0)
            base_line['price_unit'] += (deli_charge / quantity) if quantity else deli_charge
        return base_line
