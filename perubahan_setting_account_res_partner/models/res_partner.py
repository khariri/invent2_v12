# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields,models

class ResPartner(models.Model):
    _inherit = "res.partner"

    property_account_payable_id =  fields.Many2one(
        required=False,
    )

    property_account_receivable_id = fields.Many2one(
        required=False,
    )