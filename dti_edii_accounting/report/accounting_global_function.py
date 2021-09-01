from odoo import models, fields, api
from odoo.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
import calendar
import collections
import operator

class DtAccGlobalFunction(models.TransientModel):
    _name = 'dt.acc.global.function'

    def get_trial_balance_report_data(self, period_id, start_date, end_date, account_id):
        domain_all = [
            ('company_id.id','=',self.env.user.company_id.id),
            ('move_id.state','=','posted'),
            ('date','<=',end_date),
        ]

        domain = [
            ('company_id.id','=',self.env.user.company_id.id),
            ('move_id.state','=','posted'),
            ('date','>=',start_date),
            ('date','<=',end_date),
        ]

        if account_id:
            domain += [('account_id.id', 'child_of', account_id)]
            domain_all += [('account_id.id', 'child_of', account_id)]

        period_obj = self.env['account.period'].browse(period_id)

        # MUTASI
        move_all_ids = self.env['account.move.line'].sudo().search(domain_all, order='account_id asc')

        DATA_TEMP = []
        for m in move_all_ids:

            debit = 0
            credit = 0
            myr = 0
            usd = 0
            
            if str(m.account_id.code)[0] in ['4','5','6','7','8','9'] and m.date < period_obj.fiscalyear_id.date_from:
                debit = 0
                credit = 0
                myr = 0
                usd = 0
            else:
                debit = m.debit
                credit = m.credit
                myr = m.amount_myr
                usd = m.amount_usd

            DATA_TEMP.append({
                'account_id'        : m.account_id.id,
                'date'              : m.date,
                'debit_awal'        : debit if m.date < start_date else 0,
                'credit_awal'       : credit if m.date < start_date else 0,
                'debit'             : debit if m.date >= start_date and m.date <= end_date else 0,
                'credit'            : credit if m.date >= start_date and m.date <= end_date else 0,
                'myr'               : myr if m.date >= start_date and m.date <= end_date else 0,
                'usd'            : usd if m.date >= start_date and m.date <= end_date else 0,
                })

        grouped = collections.defaultdict(list)
        for item in DATA_TEMP:
            grouped[item['account_id']].append(item)
        
        DATA_REPORT = []
        for code, group in grouped.items():
            total_debit_awal = sum(l['debit_awal'] for l in group)
            total_credit_awal = sum(l['credit_awal'] for l in group)
            total_debit = sum(l['debit'] for l in group)
            total_credit = sum(l['credit'] for l in group)
            total_myr = sum(l['myr'] for l in group)
            total_usd = sum(l['usd'] for l in group)

            saldo_normal = self.env['account.account'].sudo().browse(code).saldo_normal

            saldo_awal = 0
            saldo_akhir = 0

            if saldo_normal == 'debit':
                saldo_awal = total_debit_awal - total_credit_awal
            else:
                saldo_awal = total_credit_awal - total_debit_awal

            if saldo_normal == 'debit':
                saldo_akhir = saldo_awal + total_debit - total_credit
            else:
                saldo_akhir = saldo_awal - total_debit + total_credit

            if saldo_awal != 0 or total_debit != 0 or total_credit != 0 or saldo_akhir != 0:
                DATA_REPORT.append({
                    'code'                      : self.env['account.account'].sudo().browse(code).code,
                    'account_id'                : self.env['account.account'].sudo().browse(code).name,
                    'saldo_awal'                : saldo_awal,
                    'debit'                     : total_debit,
                    'credit'                    : total_credit,
                    'myr'                       : total_myr,
                    'usd'                       : total_usd,
                    'saldo_akhir'               : saldo_akhir,
                    })

        return sorted(DATA_REPORT, key=operator.itemgetter('code'))    

    def get_general_ledger_report_data(self, period_id, start_date, end_date, start_account_id, end_account_id):

        DATA_REPORT = []

        start_coa = self.env['account.account'].sudo().browse(start_account_id)
        end_coa = self.env['account.account'].sudo().browse(end_account_id)
        # level = start_coa.level

        period_obj = self.env['account.period'].browse(period_id)

        coa_ids = self.env['account.account'].sudo().search([
            ('company_id.id', '=', self.env.user.company_id.id),
            ('code', '>=', start_coa.code),
            ('code', '<=', end_coa.code),
            # ('level', '=', level),
            # ('type', '!=', 'view'),
            ])

        for coa in coa_ids:
            DATA_LINE = []

            domain_saldo_awal = [
                ('company_id.id','=',self.env.user.company_id.id),
                ('account_id.id', '=', coa.id),
                ('move_id.state','=','posted'),
                ('date','<',start_date),
            ]

            domain = [
                ('company_id.id','=',self.env.user.company_id.id),
                ('move_id.state','=','posted'),
                ('account_id.id', '=', coa.id),
                ('date','>=',start_date),
                ('date','<=',end_date),
            ]

            # SALDO AWAL UNTUK PENDAPATAN & BIAYA
            if str(coa.code)[0] in ['4','5','6','7','8','9']:
                domain_saldo_awal = [
                    ('company_id.id','=',self.env.user.company_id.id),
                    ('move_id.state','=','posted'),
                    ('account_id.id', '=', coa.id),
                    ('date','>=',period_obj.fiscalyear_id.date_from),
                    ('date','<',start_date),
                ]
                
            # SALDO AWAL
            move_saldo_awal_ids = self.env['account.move.line'].sudo().search(domain_saldo_awal, order='date asc')

            # MUTASI
            move_ids = self.env['account.move.line'].sudo().search(domain, order='date asc')

            saldo_awal = 0
            for m in move_saldo_awal_ids:
                if m.account_id.saldo_normal == 'debit':
                    saldo_awal = saldo_awal + m.debit - m.credit
                else:
                    saldo_awal = saldo_awal - m.debit + m.credit

            if move_saldo_awal_ids or move_ids:
                DATA_LINE.append({
                    'date'              : start_date,
                    'voucher_id'        : False,
                    'voucher_no'        : '',
                    'label'             : 'SALDO AWAL',
                    'debit'             : saldo_awal if coa.saldo_normal == 'debit' else 0,
                    'credit'            : saldo_awal if coa.saldo_normal == 'credit' else 0,
                    'myr'               : 0,
                    'usd'               : 0,
                    'saldo'             : saldo_awal,
                    'create_uid'        : '',
                    })


                saldo = saldo_awal
                total_debit = 0
                total_credit = 0
                total_myr = 0
                total_usd = 0

                # total_debit += saldo_awal if coa.saldo_normal == 'debit' else 0
                # total_credit += saldo_awal if coa.saldo_normal == 'credit' else 0

                for m in move_ids:
                    if m.account_id.saldo_normal == 'debit':
                        saldo = saldo + m.debit - m.credit
                    else:
                        saldo = saldo - m.debit + m.credit

                    total_debit += m.debit
                    total_credit += m.credit
                    total_myr += m.amount_myr
                    total_usd += m.amount_usd

                    label = m.name

                    DATA_LINE.append({
                        'date'              : m.move_id.date,
                        'voucher_id'        : m.move_id.id,
                        'voucher_no'        : m.move_id.name,
                        'label'             : label,
                        # 'subgl_code'        : m.sub_account_id.code,
                        # 'subgl_id'          : m.sub_account_id.name,
                        'debit'             : m.debit,
                        'credit'            : m.credit,
                        'myr'               : m.amount_myr,
                        'usd'               : m.amount_usd,
                        'saldo'             : saldo,
                        'create_uid'        : m.create_uid.name,
                        })

                DATA_REPORT.append({
                    'account'               : coa.code + ' - ' + coa.name,
                    # 'mutasi'                : sorted(DATA_LINE, key=operator.itemgetter('date')),
                    'mutasi'                : DATA_LINE,
                    't_saldo_awal'          : saldo_awal,
                    't_debit'               : total_debit,
                    't_credit'              : total_credit,
                    't_myr'                 : total_myr,
                    't_usd'                 : total_usd,
                    't_saldo'               : saldo,
                    })

        return DATA_REPORT

    def get_balance_sheet_report_data(self, company_id, fiscalyear_id, period_id, is_detail, with_movement):
        DATA_AKTIVA = []
        DATA_LIABILITAS = []
        DATA_EKUITAS = []

        period_ids = self.env['account.period'].browse(period_id)

        neraca_ids = self.env['account.financial.report'].sudo().search([
            ('company_id.id', '=', company_id),
            ('name', '=', 'BALANCE SHEET'),
            ],limit=1)

        # AKTIVA
        aktiva_ids = self.env['account.financial.report'].sudo().search([
            ('id', 'child_of', neraca_ids.id),
            ('report_group', '=', 'Balance Sheet'),
            ('balance_sheet_type', '=', 'Aktiva'),
            ('id', '!=', neraca_ids.id),
            ], order='sequence asc')
        
        for l in aktiva_ids:

            saldo_awal_tahun = 0
            saldo_sd_bulan_lalu = 0
            mutasi_bulan_ini = 0
            saldo_sd_bulan_ini = 0

            if l.type == 'accounts':
                saldo_ids = self.env['account.move.line'].sudo().search([
                    ('account_id.id', 'in', l.account_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ])

                # AWAL TAHUN
                for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.fiscalyear_id.date_from):
                    saldo_awal_tahun = saldo_awal_tahun + l1.debit - l1.credit

                # SAMPAI DENGAN BULAN LALU
                for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.date_start):
                    saldo_sd_bulan_lalu = saldo_sd_bulan_lalu + l1.debit - l1.credit

                # MUTASI BULAN INI
                for l1 in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop):
                    mutasi_bulan_ini = mutasi_bulan_ini + l1.debit - l1.credit

                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                DATA_AKTIVA.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : 'view' if is_detail else 'account',
                    'saldo_awal_tahun'          : saldo_awal_tahun,
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                    })

                # DISPLAY ACCOUNT
                if is_detail:
                    for ch in l.account_ids:

                        t_saldo_awal_tahun      = 0
                        for z1 in saldo_ids.filtered(lambda x: x.date < period_ids.fiscalyear_id.date_from and x.account_id.id == ch.id):
                            t_saldo_awal_tahun  += t_saldo_awal_tahun + z1.debit - z1.credit

                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_saldo_sd_bulan_lalu   = t_credit - t_debit

                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_mutasi_bulan_ini      = t_credit - t_debit

                        if not with_movement or (with_movement and (t_saldo_sd_bulan_lalu != 0 or t_mutasi_bulan_ini != 0 or t_mutasi_bulan_ini !=0)):
                            DATA_AKTIVA.append({
                                'style'                     : False,
                                'code'                      : ch.code,
                                'name'                      : ch.name,
                                'type'                      : 'account',
                                'saldo_awal_tahun'          : t_saldo_awal_tahun,
                                'saldo_sd_bulan_lalu'       : t_saldo_sd_bulan_lalu,
                                'mutasi_bulan_ini'          : t_mutasi_bulan_ini,
                                'saldo_sd_bulan_ini'        : t_saldo_sd_bulan_lalu + t_mutasi_bulan_ini,
                                })

                    DATA_AKTIVA.append({
                        'style'                     : l.style_overwrite,
                        'code'                      : '',
                        'name'                      : 'Total ' + l.name,
                        'type'                      : 'value',
                        'saldo_awal_tahun'          : saldo_awal_tahun,
                        'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                        'mutasi_bulan_ini'          : mutasi_bulan_ini,
                        'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                        })

                    DATA_AKTIVA.append({
                        'style'                     : '',
                        'code'                      : '',
                        'name'                      : 'BREAK',
                        'type'                      : '',
                        'saldo_awal_tahun'          : 0,
                        'saldo_sd_bulan_lalu'       : 0,
                        'mutasi_bulan_ini'          : 0,
                        'saldo_sd_bulan_ini'        : 0,
                        })


            elif l.type == 'account_report':
                lst_item_report_ids = self.env['account.financial.report'].sudo().search([
                    ('id', 'child_of', l.account_report_id.id),
                    ('type', '=', 'accounts'),
                    ])

                for lst in lst_item_report_ids:
                    saldo_ids = self.env['account.move.line'].sudo().search([
                        ('account_id.id', 'in', lst.account_ids.ids),
                        ('move_id.state', '=', 'posted'),
                        ])

                    # AWAL TAHUN
                    for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.fiscalyear_id.date_from):
                        saldo_awal_tahun = saldo_awal_tahun + l1.debit - l1.credit

                    # SAMPAI DENGAN BULAN LALU
                    for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.date_start):
                        saldo_sd_bulan_lalu = saldo_sd_bulan_lalu + l1.debit - l1.credit

                    # MUTASI BULAN INI
                    for l1 in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop):
                        mutasi_bulan_ini = mutasi_bulan_ini + l1.debit - l1.credit

                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                item_type = ''
                if l.type == 'sum':
                    item_type = 'view'
                elif l.type == 'accounts':
                    item_type = 'account'
                elif l.type == 'account_report':
                    item_type = 'value'

                DATA_AKTIVA.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : item_type,
                    'saldo_awal_tahun'          : saldo_awal_tahun,
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                    })


            elif l.type == 'sum':
                DATA_AKTIVA.append({
                    'style'                     : 1,
                    'code'                      : '',
                    'name'                      : l.name,
                    'type'                      : '',
                    'saldo_awal_tahun'          : 0,
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })

            elif l.is_breakline:
                DATA_AKTIVA.append({
                    'style'                     : '',
                    'code'                      : '',
                    'name'                      : 'BREAK',
                    'type'                      : '',
                    'saldo_awal_tahun'          : 0,
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })


        # LIABILITAS
        liabilitas_ids = self.env['account.financial.report'].sudo().search([
            ('id', 'child_of', neraca_ids.id),
            ('report_group', '=', 'Balance Sheet'),
            ('balance_sheet_type', '=', 'Liabilitas'),
            ('id', '!=', neraca_ids.id),
            ], order='sequence asc')
        
        for l in liabilitas_ids:

            saldo_awal_tahun = 0
            saldo_sd_bulan_lalu = 0
            mutasi_bulan_ini = 0
            saldo_sd_bulan_ini = 0

            if l.type == 'accounts':
                saldo_ids = self.env['account.move.line'].sudo().search([
                    ('account_id.id', 'in', l.account_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ])

                # AWAL TAHUN
                for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.fiscalyear_id.date_from):
                    saldo_awal_tahun = saldo_awal_tahun + l1.debit - l1.credit

                # SAMPAI DENGAN BULAN LALU
                for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.date_start):
                    saldo_sd_bulan_lalu = saldo_sd_bulan_lalu + l1.debit - l1.credit

                # MUTASI BULAN INI
                for l1 in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop):
                    mutasi_bulan_ini = mutasi_bulan_ini + l1.debit - l1.credit

                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                DATA_LIABILITAS.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : 'view' if is_detail else 'account',
                    'saldo_awal_tahun'          : saldo_awal_tahun,
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                    })

                # DISPLAY ACCOUNT
                if is_detail:
                    for ch in l.account_ids:

                        t_saldo_awal_tahun      = 0
                        for z1 in saldo_ids.filtered(lambda x: x.date < period_ids.fiscalyear_id.date_from and x.account_id.id == ch.id):
                            t_saldo_awal_tahun  += t_saldo_awal_tahun + z1.debit - z1.credit

                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_saldo_sd_bulan_lalu   = t_credit - t_debit

                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_mutasi_bulan_ini      = t_credit - t_debit

                        if not with_movement or (with_movement and (t_saldo_sd_bulan_lalu != 0 or t_mutasi_bulan_ini != 0 or t_mutasi_bulan_ini !=0)):
                            DATA_LIABILITAS.append({
                                'style'                     : False,
                                'code'                      : ch.code,
                                'name'                      : ch.name,
                                'type'                      : 'account',
                                'saldo_awal_tahun'          : t_saldo_awal_tahun,
                                'saldo_sd_bulan_lalu'       : t_saldo_sd_bulan_lalu,
                                'mutasi_bulan_ini'          : t_mutasi_bulan_ini,
                                'saldo_sd_bulan_ini'        : t_saldo_sd_bulan_lalu + t_mutasi_bulan_ini,
                                })

                    DATA_LIABILITAS.append({
                        'style'                     : l.style_overwrite,
                        'code'                      : '',
                        'name'                      : 'Total ' + l.name,
                        'type'                      : 'value',
                        'saldo_awal_tahun'          : saldo_awal_tahun,
                        'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                        'mutasi_bulan_ini'          : mutasi_bulan_ini,
                        'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                        })

                    DATA_LIABILITAS.append({
                        'style'                     : '',
                        'code'                      : '',
                        'name'                      : 'BREAK',
                        'type'                      : '',
                        'saldo_awal_tahun'          : 0,
                        'saldo_sd_bulan_lalu'       : 0,
                        'mutasi_bulan_ini'          : 0,
                        'saldo_sd_bulan_ini'        : 0,
                        })

            elif l.type == 'account_report':
                lst_item_report_ids = self.env['account.financial.report'].sudo().search([
                    ('id', 'child_of', l.account_report_id.id),
                    ('type', '=', 'accounts'),
                    ])

                for lst in lst_item_report_ids:
                    saldo_ids = self.env['account.move.line'].sudo().search([
                        ('account_id.id', 'in', lst.account_ids.ids),
                        ('move_id.state', '=', 'posted'),
                        ])

                    # AWAL TAHUN
                    for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.fiscalyear_id.date_from):
                        saldo_awal_tahun = saldo_awal_tahun + l1.debit - l1.credit

                    # SAMPAI DENGAN BULAN LALU
                    for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.date_start):
                        saldo_sd_bulan_lalu = saldo_sd_bulan_lalu + l1.debit - l1.credit

                    # MUTASI BULAN INI
                    for l1 in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop):
                        mutasi_bulan_ini = mutasi_bulan_ini + l1.debit - l1.credit

                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                item_type = ''
                if l.type == 'sum':
                    item_type = 'view'
                elif l.type == 'accounts':
                    item_type = 'account'
                elif l.type == 'account_report':
                    item_type = 'value'

                DATA_LIABILITAS.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : item_type,
                    'saldo_awal_tahun'          : saldo_awal_tahun,
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                    })


            elif l.type == 'sum':
                DATA_LIABILITAS.append({
                    'style'                     : 1,
                    'code'                      : '',
                    'name'                      : l.name,
                    'type'                      : '',
                    'saldo_awal_tahun'          : 0,
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })

            elif l.is_breakline:
                DATA_LIABILITAS.append({
                    'style'                     : '',
                    'code'                      : '',
                    'name'                      : 'BREAK',
                    'type'                      : '',
                    'saldo_awal_tahun'          : 0,
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })

        # EKUTITAS
        ekuitas_ids = self.env['account.financial.report'].sudo().search([
            ('id', 'child_of', neraca_ids.id),
            ('report_group', '=', 'Balance Sheet'),
            ('balance_sheet_type', '=', 'Ekuitas'),
            ('id', '!=', neraca_ids.id),
            ], order='sequence asc')
        
        for l in ekuitas_ids:

            saldo_awal_tahun = 0
            saldo_sd_bulan_lalu = 0
            mutasi_bulan_ini = 0
            saldo_sd_bulan_ini = 0

            if l.type == 'accounts':
                saldo_ids = self.env['account.move.line'].sudo().search([
                    ('account_id.id', 'in', l.account_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ])

                # AWAL TAHUN
                for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.fiscalyear_id.date_from):
                    saldo_awal_tahun = saldo_awal_tahun + l1.debit - l1.credit

                # SAMPAI DENGAN BULAN LALU
                for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.date_start):
                    saldo_sd_bulan_lalu = saldo_sd_bulan_lalu + l1.debit - l1.credit

                # MUTASI BULAN INI
                for l1 in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop):
                    mutasi_bulan_ini = mutasi_bulan_ini + l1.debit - l1.credit

                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                DATA_EKUITAS.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : 'view' if is_detail else 'account',
                    'saldo_awal_tahun'          : saldo_awal_tahun,
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                    })

                # DISPLAY ACCOUNT
                if is_detail:
                    for ch in l.account_ids:

                        t_saldo_awal_tahun      = 0
                        for z1 in saldo_ids.filtered(lambda x: x.date < period_ids.fiscalyear_id.date_from and x.account_id.id == ch.id):
                            t_saldo_awal_tahun  += t_saldo_awal_tahun + z1.debit - z1.credit


                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_saldo_sd_bulan_lalu   = t_credit - t_debit

                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_mutasi_bulan_ini      = t_credit - t_debit

                        if not with_movement or (with_movement and (t_saldo_sd_bulan_lalu != 0 or t_mutasi_bulan_ini != 0 or t_mutasi_bulan_ini !=0)):
                            DATA_EKUITAS.append({
                                'style'                     : False,
                                'code'                      : ch.code,
                                'name'                      : ch.name,
                                'type'                      : 'account',
                                'saldo_awal_tahun'          : t_saldo_awal_tahun,
                                'saldo_sd_bulan_lalu'       : t_saldo_sd_bulan_lalu,
                                'mutasi_bulan_ini'          : t_mutasi_bulan_ini,
                                'saldo_sd_bulan_ini'        : t_saldo_sd_bulan_lalu + t_mutasi_bulan_ini,
                                })

                    DATA_EKUITAS.append({
                        'style'                     : l.style_overwrite,
                        'code'                      : '',
                        'name'                      : 'Total ' + l.name,
                        'type'                      : 'value',
                        'saldo_awal_tahun'          : saldo_awal_tahun,
                        'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                        'mutasi_bulan_ini'          : mutasi_bulan_ini,
                        'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                        })

                    DATA_EKUITAS.append({
                        'style'                     : '',
                        'code'                      : '',
                        'name'                      : 'BREAK',
                        'type'                      : '',
                        'saldo_awal_tahun'          : 0,
                        'saldo_sd_bulan_lalu'       : 0,
                        'mutasi_bulan_ini'          : 0,
                        'saldo_sd_bulan_ini'        : 0,
                        })


            elif l.type == 'account_report':
                lst_item_report_ids = self.env['account.financial.report'].sudo().search([
                    ('id', 'child_of', l.account_report_id.id),
                    ('type', '=', 'accounts'),
                    ])

                for lst in lst_item_report_ids:
                    saldo_ids = self.env['account.move.line'].sudo().search([
                        ('account_id.id', 'in', lst.account_ids.ids),
                        ('move_id.state', '=', 'posted'),
                        ])

                    # AWAL TAHUN
                    for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.fiscalyear_id.date_from):
                        saldo_awal_tahun = saldo_awal_tahun + l1.debit - l1.credit

                    # SAMPAI DENGAN BULAN LALU
                    for l1 in saldo_ids.filtered(lambda x: x.date < period_ids.date_start):
                        saldo_sd_bulan_lalu = saldo_sd_bulan_lalu + l1.debit - l1.credit

                    # MUTASI BULAN INI
                    for l1 in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop):
                        mutasi_bulan_ini = mutasi_bulan_ini + l1.debit - l1.credit

                
                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                item_type = ''
                if l.type == 'sum':
                    item_type = 'view'
                elif l.type == 'accounts':
                    item_type = 'account'
                elif l.type == 'account_report':
                    item_type = 'value'

                DATA_EKUITAS.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : item_type,
                    'saldo_awal_tahun'          : saldo_awal_tahun,
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                    })


            elif l.type == 'sum':
                DATA_EKUITAS.append({
                    'style'                     : 1,
                    'code'                      : '',
                    'name'                      : l.name,
                    'type'                      : '',
                    'saldo_awal_tahun'          : 0,
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })

            elif l.is_breakline:
                DATA_EKUITAS.append({
                    'style'                     : '',
                    'code'                      : '',
                    'name'                      : 'BREAK',
                    'type'                      : '',
                    'saldo_awal_tahun'          : 0,
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })

        return [DATA_AKTIVA, DATA_LIABILITAS, DATA_EKUITAS]

    def get_profit_loss_report_data(self, company_id, fiscalyear_id, period_id, is_detail, with_movement):
        DATA_REPORT = []

        report_ids = self.env['account.financial.report'].sudo().search([
            ('name', '=', 'PROFIT & LOSS'),
            ('company_id.id', '=', company_id),
            ],limit=1)

        report_item_ids = self.env['account.financial.report'].sudo().search([
            ('id', 'child_of', report_ids.id),
            ('report_group', '=', 'Profit and Loss'),
            ('id', '!=', report_ids.id),
            ], order='sequence asc')

        period_ids = self.env['account.period'].browse(period_id)

        for l in report_item_ids:

            saldo_sd_bulan_lalu = 0
            mutasi_bulan_ini = 0
            saldo_sd_bulan_ini = 0

            if l.type == 'accounts':
                saldo_ids = self.env['account.move.line'].sudo().search([
                    ('account_id.id', 'in', l.account_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ])

                debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                saldo_sd_bulan_lalu = credit - debit

                debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                mutasi_bulan_ini = credit - debit

                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                DATA_REPORT.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : 'view' if is_detail else 'account',
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu if not is_detail else 0,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini if not is_detail else 0,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini if not is_detail else 0,
                    })

                # DISPLAY ACCOUNT
                if is_detail:
                    for ch in l.account_ids:

                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_saldo_sd_bulan_lalu   = t_credit - t_debit

                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_mutasi_bulan_ini      = t_credit - t_debit

                        if not with_movement or (with_movement and (t_saldo_sd_bulan_lalu != 0 or t_mutasi_bulan_ini != 0 or t_mutasi_bulan_ini !=0)):
                            DATA_REPORT.append({
                                'style'                     : False,
                                'code'                      : ch.code,
                                'name'                      : ch.name,
                                'type'                      : 'account',
                                'saldo_sd_bulan_lalu'       : t_saldo_sd_bulan_lalu,
                                'mutasi_bulan_ini'          : t_mutasi_bulan_ini,
                                'saldo_sd_bulan_ini'        : t_saldo_sd_bulan_lalu + t_mutasi_bulan_ini,
                                })

                    DATA_REPORT.append({
                        'style'                     : l.style_overwrite,
                        'code'                      : '',
                        'name'                      : 'Total ' + l.name,
                        'type'                      : 'value',
                        'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                        'mutasi_bulan_ini'          : mutasi_bulan_ini,
                        'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                        })

                    DATA_REPORT.append({
                        'style'                     : '',
                        'code'                      : '',
                        'name'                      : 'BREAK',
                        'type'                      : '',
                        'saldo_sd_bulan_lalu'       : 0,
                        'mutasi_bulan_ini'          : 0,
                        'saldo_sd_bulan_ini'        : 0,
                        })


            elif l.type == 'account_report':
                if not l.use_formula:
                    lst_item_report_ids = self.env['account.financial.report'].sudo().search([
                        ('id', 'child_of', l.account_report_id.id),
                        ('type', '=', 'accounts'),
                        ('sequence', '>', l.account_report_id.sequence),
                        ('sequence', '<', l.sequence),
                        ])

                    saldo_sd_bulan_lalu = 0
                    mutasi_bulan_ini = 0
                    for lst in lst_item_report_ids:

                        saldo_ids = self.env['account.move.line'].sudo().search([
                            ('account_id.id', 'in', lst.account_ids.ids),
                            ('move_id.state', '=', 'posted'),
                            ])

                        debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                        credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                        saldo_sd_bulan_lalu += credit - debit

                        debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                        credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                        mutasi_bulan_ini += credit - debit

                else:
                    # ADDITION
                    for m in l.addition_ids:
                        if not m.use_formula:
                            saldo_ids = self.env['account.move.line'].sudo().search([
                                ('account_id.id', 'in', m.account_ids.ids),
                                ('move_id.state', '=', 'posted'),
                                ])

                            debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                            credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                            saldo_sd_bulan_lalu += credit - debit

                            debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                            credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                            mutasi_bulan_ini += credit - debit

                        # FORMULA
                        else:
                            for t in DATA_REPORT:
                                if t['name'] == m.name:
                                    saldo_sd_bulan_lalu += t['saldo_sd_bulan_lalu']
                                    mutasi_bulan_ini += t['mutasi_bulan_ini']
                                    saldo_sd_bulan_ini += t['saldo_sd_bulan_ini']


                    # DEDUCATION
                    for m in l.deduction_ids:
                        if not m.use_formula:
                            saldo_ids = self.env['account.move.line'].sudo().search([
                                ('account_id.id', 'in', m.account_ids.ids),
                                ('move_id.state', '=', 'posted'),
                                ])

                            debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                            credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                            saldo_sd_bulan_lalu += credit - debit

                            debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                            credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                            mutasi_bulan_ini += credit - debit

                        # FORMULA
                        else:
                            for t in DATA_REPORT:
                                if t['name'] == m.name:
                                    saldo_sd_bulan_lalu += t['saldo_sd_bulan_lalu']
                                    mutasi_bulan_ini += t['mutasi_bulan_ini']
                                    saldo_sd_bulan_ini += t['saldo_sd_bulan_ini']


                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                item_type = ''
                if l.type == 'sum':
                    item_type = 'view'
                elif l.type == 'accounts':
                    item_type = 'account'
                elif l.type == 'account_report':
                    item_type = 'value'

                DATA_REPORT.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : item_type,
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                    })


            elif l.type == 'sum':
                DATA_REPORT.append({
                    'style'                     : 1,
                    'code'                      : '',
                    'name'                      : l.name,
                    'type'                      : '',
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })

            elif l.is_breakline:
                DATA_REPORT.append({
                    'style'                     : '',
                    'code'                      : '',
                    'name'                      : 'BREAK',
                    'type'                      : '',
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })

        return DATA_REPORT

    def get_cashflow_report_data(self, company_id, fiscalyear_id, period_id, is_detail, with_movement):
        DATA_REPORT = []

        report_ids = self.env['dti.cashflow.items'].sudo().search([
            ('name', '=', 'Cashflow'),
            ('company_id.id', '=', company_id),
            ],limit=1)

        report_item_ids = self.env['dti.cashflow.items'].sudo().search([
            ('id', 'child_of', report_ids.id),
            ('report_group', '=', 'Cashflow'),
            ('id', '!=', report_ids.id),
            ], order='sequence asc')

        period_ids = self.env['account.period'].browse(period_id)

        for l in report_item_ids:

            saldo_sd_bulan_lalu = 0
            mutasi_bulan_ini = 0
            saldo_sd_bulan_ini = 0

            if l.type == 'accounts':
                saldo_ids = self.env['account.move.line'].sudo().search([
                    ('account_id.id', 'in', l.account_ids.ids),
                    ('move_id.state', '=', 'posted'),
                    ])

                debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                saldo_sd_bulan_lalu = credit - debit

                debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                mutasi_bulan_ini = credit - debit

                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                DATA_REPORT.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : 'view' if is_detail else 'account',
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu if not is_detail else 0,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini if not is_detail else 0,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini if not is_detail else 0,
                    })

                # DISPLAY ACCOUNT
                if is_detail:
                    for ch in l.account_ids:

                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start and x.account_id.id == ch.id))
                        t_saldo_sd_bulan_lalu   = t_credit - t_debit

                        t_debit                 = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_credit                = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop and x.account_id.id == ch.id))
                        t_mutasi_bulan_ini      = t_credit - t_debit

                        if not with_movement or (with_movement and (t_saldo_sd_bulan_lalu != 0 or t_mutasi_bulan_ini != 0 or t_mutasi_bulan_ini !=0)):
                            DATA_REPORT.append({
                                'style'                     : False,
                                'code'                      : ch.code,
                                'name'                      : ch.name,
                                'type'                      : 'account',
                                'saldo_sd_bulan_lalu'       : t_saldo_sd_bulan_lalu,
                                'mutasi_bulan_ini'          : t_mutasi_bulan_ini,
                                'saldo_sd_bulan_ini'        : t_saldo_sd_bulan_lalu + t_mutasi_bulan_ini,
                                })

                    DATA_REPORT.append({
                        'style'                     : l.style_overwrite,
                        'code'                      : '',
                        'name'                      : 'Total ' + l.name,
                        'type'                      : 'value',
                        'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                        'mutasi_bulan_ini'          : mutasi_bulan_ini,
                        'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                        })

                    DATA_REPORT.append({
                        'style'                     : '',
                        'code'                      : '',
                        'name'                      : 'BREAK',
                        'type'                      : '',
                        'saldo_sd_bulan_lalu'       : 0,
                        'mutasi_bulan_ini'          : 0,
                        'saldo_sd_bulan_ini'        : 0,
                        })


            elif l.type == 'account_report':
                if not l.use_formula:
                    lst_item_report_ids = self.env['dti.cashflow.items'].sudo().search([
                        ('id', 'child_of', l.account_report_id.id),
                        ('type', '=', 'accounts'),
                        ('sequence', '>', l.account_report_id.sequence),
                        ('sequence', '<', l.sequence),
                        ])

                    saldo_sd_bulan_lalu = 0
                    mutasi_bulan_ini = 0
                    for lst in lst_item_report_ids:

                        saldo_ids = self.env['account.move.line'].sudo().search([
                            ('account_id.id', 'in', lst.account_ids.ids),
                            ('move_id.state', '=', 'posted'),
                            ])

                        debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                        credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                        saldo_sd_bulan_lalu += credit - debit

                        debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                        credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                        mutasi_bulan_ini += credit - debit

                else:
                    # ADDITION
                    for m in l.addition_ids:
                        if not m.use_formula:
                            saldo_ids = self.env['account.move.line'].sudo().search([
                                ('account_id.id', 'in', m.account_ids.ids),
                                ('move_id.state', '=', 'posted'),
                                ])

                            debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                            credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                            saldo_sd_bulan_lalu += credit - debit

                            debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                            credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                            mutasi_bulan_ini += credit - debit

                        # FORMULA
                        else:
                            for t in DATA_REPORT:
                                if t['name'] == m.name:
                                    saldo_sd_bulan_lalu += t['saldo_sd_bulan_lalu']
                                    mutasi_bulan_ini += t['mutasi_bulan_ini']
                                    saldo_sd_bulan_ini += t['saldo_sd_bulan_ini']


                    # DEDUCATION
                    for m in l.deduction_ids:
                        if not m.use_formula:
                            saldo_ids = self.env['account.move.line'].sudo().search([
                                ('account_id.id', 'in', m.account_ids.ids),
                                ('move_id.state', '=', 'posted'),
                                ])

                            debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                            credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.fiscalyear_id.date_from and x.date < period_ids.date_start))
                            saldo_sd_bulan_lalu += credit - debit

                            debit = sum(l.debit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                            credit = sum(l.credit for l in saldo_ids.filtered(lambda x: x.date >= period_ids.date_start and x.date <= period_ids.date_stop))
                            mutasi_bulan_ini += credit - debit

                        # FORMULA
                        else:
                            for t in DATA_REPORT:
                                if t['name'] == m.name:
                                    saldo_sd_bulan_lalu += t['saldo_sd_bulan_lalu']
                                    mutasi_bulan_ini += t['mutasi_bulan_ini']
                                    saldo_sd_bulan_ini += t['saldo_sd_bulan_ini']


                saldo_sd_bulan_ini = saldo_sd_bulan_lalu + mutasi_bulan_ini

                item_type = ''
                if l.type == 'sum':
                    item_type = 'view'
                elif l.type == 'accounts':
                    item_type = 'account'
                elif l.type == 'account_report':
                    item_type = 'value'

                DATA_REPORT.append({
                    'style'                     : l.style_overwrite,
                    'code'                      : l.code_number,
                    'name'                      : l.name,
                    'type'                      : item_type,
                    'saldo_sd_bulan_lalu'       : saldo_sd_bulan_lalu,
                    'mutasi_bulan_ini'          : mutasi_bulan_ini,
                    'saldo_sd_bulan_ini'        : saldo_sd_bulan_ini,
                    })


            elif l.type == 'sum':
                DATA_REPORT.append({
                    'style'                     : 1,
                    'code'                      : '',
                    'name'                      : l.name,
                    'type'                      : '',
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })

            elif l.is_breakline:
                DATA_REPORT.append({
                    'style'                     : '',
                    'code'                      : '',
                    'name'                      : 'BREAK',
                    'type'                      : '',
                    'saldo_sd_bulan_lalu'       : 0,
                    'mutasi_bulan_ini'          : 0,
                    'saldo_sd_bulan_ini'        : 0,
                    })

        return DATA_REPORT