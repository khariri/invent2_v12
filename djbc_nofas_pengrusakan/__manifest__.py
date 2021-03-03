# -*- coding: utf-8 -*-
{
    'name': 'DJBC Laporan Pengrusakan',
    'version': '12.0.1.0.0',
    'summary': 'DJBC Laporan Pengrusakan',
    'description': 'DJBC Laporan Pengrusakan',
    'category': 'Extra Tools',
    'author': 'Khariri',
    'website': '-',
    # 'license': 'AGPL',
    'depends': ['djbc','stock_picking_invoice_link','pengrusakan_barang'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/nofas_rusak_wiz.xml',	
        'views/nofas_rusak.xml',
        'views/menu.xml',
        'reports/report_xls.xml'
    ],
    'demo': [''],
    'installable': True,
    'auto_install': False,
    # 'external_dependencies': {
    #    'python': [''],
    # }
}
