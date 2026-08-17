from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    """
    Extends the purchase.order.line model to include additional fields for RFP integration
    and product display enhancements.

    Fields:
        delivery_charge (Monetary): The delivery charge associated with the line item.
        product_name (Char): A related field displaying the name of the selected product.
        product_image (Binary): A related field showing the image of the product.
        rfp_id (Many2one): A related field pointing to the RFP linked with the purchase order.

    Purpose:
        - To include delivery charges per product line for use in automated scoring and cost analysis.
        - To provide improved UI elements such as product names and images directly in the purchase order line.
        - To support traceability between RFQs and their parent RFPs for better procurement workflow management.
    """
    _inherit = 'purchase.order.line'

    delivery_charge = fields.Monetary(string='Delivery Charge')
    product_name = fields.Char(string='Product Name', related='product_id.name')
    product_image = fields.Binary(string='Product Image', related='product_id.image_1920')
    rfp_id = fields.Many2one('supplies.rfp', related="order_id.rfp_id")
