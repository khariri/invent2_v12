# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "EDI Indonesia - Penambahan Form Pemusnahan Barang di stock picking",
    "version": "12.0.1.0.0",
    "category": "localization",
    "website": "https://edi-indonesia.co.id",
    "author": "Khariri - PT.EDI Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        'views/stock_picking.xml'
    ],
    "summary": "Penambahan Stock Picking Form Pemusnahan Barang",
    "description": """Untuk dapat memunculkan form ini Create terlebih dahulu Type Operation Baru denhan nama Pemusnahan""", 
}
