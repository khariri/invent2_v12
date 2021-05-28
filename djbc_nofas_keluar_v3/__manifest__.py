# -*- coding: utf-8 -*-
{
    'name': 'DJBC Laporan Pengeluaran Versi 3',
    'version': '12.0.1.0.0',
    'summary': 'DJBC Laporan Pengeluaran Fasilitas TPB dan Non Fasilitas',
    'description': 'DJBC Laporan Pengeluaran Fasilitas TPB dan Non Fasilitas, Nilai barang di ambil dari Invoice  Nilai barang di ambil dari nilai Invoice dan nilai PO',
    'category': 'Extra Tools',
    'author': 'Khariri, Oktovan Rezman',
    'website': '-',
    # 'license': 'AGPL',
    'depends': ['djbc','stock_picking_invoice_link'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/nofas_keluar_wiz.xml',	
        'views/nofas_keluar.xml',
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
