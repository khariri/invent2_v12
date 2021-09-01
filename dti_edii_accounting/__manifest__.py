{
    "name": "DTI EDII Accounting",
    "author": "PT. Ditama Teknologi Indonesia, "
              "Aldy Apriansyah",
    "website": "www.ditama.id",
    "version": "1.0",
    "category": "Accounting",
    "summary": "Centra Accounting",
    "description": "",
    "depends": [
        "base",
        "account",
    ],
    "data": 
        [   
            "security/ir.model.access.csv",
            "security/security.xml",
            
            "views/account_account_view.xml",
            "views/account_financial_report_view.xml",
            "views/account_fiscal_year_view.xml",
            "views/account_invoice_view.xml",
            "views/account_move_view.xml",
            "views/account_period_view.xml",
            "views/account_cashflow_items_view.xml",

            "wizard/wizard_general_ledger_view.xml",
            "wizard/wizard_trial_balance_view.xml",
            "wizard/wizard_laporan_keuangan_view.xml",
            "wizard/wizard_laporan_cashflow_view.xml",

            "menu.xml",
        ],
    'installable': True,
    'application': True,
}