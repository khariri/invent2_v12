# -*- coding: utf-8 -*-
{
    'name': 'DJBC Laporan Pemusnahan',
    'version': '12.0.1.0.0',
    'summary': 'DJBC Laporan Pemusnahan',
    'description': 'DJBC Laporan Pemusnahan',
    'category': 'Extra Tools',
    'author': 'Khariri',
    'website': '-',
    # 'license': 'AGPL',
    'depends': ['djbc','stock_picking_invoice_link','pemusnahan_barang'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/nofas_musnah_wiz.xml',	
        'views/nofas_musnah.xml',
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
