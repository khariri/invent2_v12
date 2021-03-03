# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.one
    @api.depends('picking_type_id')
    def _get_picking_type_pengrusakan(self):
        type_picking_name = self.picking_type_id.name
        self.picking_type_name_pengrusakan = type_picking_name

    picking_type_name_pengrusakan = fields.Char(
        string="Type Name",
        compute="_get_picking_type_pengrusakan",
        store=True,
    )

    nomor_pengrusakan = fields.Char(
        string="Nomor Pengrusakan",
        required=False,
    )

    tanggal_pengrusakan = fields.Date(
        string="Tanggal Pengrusakan",
        required=False,
    )