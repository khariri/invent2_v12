# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.one
    @api.depends('picking_type_id')
    def _get_picking_type_pemusnahan(self):
        type_picking_name = self.picking_type_id.name
        self.picking_type_name_pemusnahan = type_picking_name

    picking_type_name_pemusnahan = fields.Char(
        string="Type Name",
        compute="_get_picking_type_pemusnahan",
        store=True,
    )

    nomor_pemusnahan = fields.Char(
        string="Nomor Pemusnahan",
        required=False,
    )

    tanggal_pemusnahan = fields.Date(
        string="Tanggal Pemusnahan",
        required=False,
    )
