from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    harga_satuan = fields.Float(
        string="Unit Price",
        digits=(12,3)
    )