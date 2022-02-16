# -*- coding: utf-8 -*-
{
    'name': 'DJBC Laporan Pengeluaran PLB',
    'version': '12.0.1.0.0',
    'summary': 'DJBC Laporan Pengeluaran PLB',
    'description': 'DJBC Laporan Pengeluaran PLB, Nilai barang di ambil dari Invoice  Nilai barang di ambil dari nilai Invoice dan nilai PO',
    'category': 'Extra Tools',
    'author': 'Khariri, Oktovan Rezman',
    'website': '-',
    # 'license': 'AGPL',
    'depends': ['djbc','stock_picking_invoice_link'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/lap_plb_keluar_wiz.xml',	
        'views/lap_plb_keluar.xml',
        'views/menu.xml',
        'reports/report.xml',
    ],
    'demo': [''],
    'installable': True,
    'auto_install': False,
    # 'external_dependencies': {
    #    'python': [''],
    # }
}
