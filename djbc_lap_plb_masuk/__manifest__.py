# -*- coding: utf-8 -*-
{
    'name': 'DJBC Laporan Pemasukan PLB',
    'version': '12.0.1.0.0',
    'summary': 'DJBC Laporan Pemasukan PLB',
    'description': 'DJBC Laporan Pemasukan PLB,  Nilai barang di ambil dari nilai Invoice dan nilai PO',
    'category': 'Extra Tools',
    'author': 'Khariri, Oktovan Rezman',
    'website': '-',
    # 'license': 'AGPL',
    'depends': ['djbc','stock_picking_invoice_link'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/lap_plb_masuk_wiz.xml',	
        'views/lap_plb_masuk.xml',
        'views/menu.xml',
        'reports/report.xml'
    ],
    'demo': [''],
    'installable': True,
    'auto_install': False,
    # 'external_dependencies': {
    #    'python': [''],
    # }
}
