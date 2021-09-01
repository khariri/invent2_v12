from odoo import fields, api, models
from odoo.exceptions import Warning
from datetime import datetime
from dateutil.relativedelta import relativedelta

class AccountFiscalYearId(models.Model):
    _inherit = 'account.fiscal.year'

    period_ids              = fields.One2many('account.period', 'fiscalyear_id', 'Periods')

    def _check_duration(self):
        obj_fy = self
        if obj_fy.date_to < obj_fy.date_from:
            return False
        return True

        _constraints = [
        (_check_duration, 'Error!\nThe start date of a fiscal year must precede its end date.', ['date_from','date_to'])
    ]

    @api.multi
    def create_period(self,interv=None):
        if interv != 3 :
            interv = 1
        period_obj = self.env['account.period']
        for fy in self:
            ds = fy.date_from
            while ds < fy.date_to:
                de = ds + relativedelta(months=interv, days=-1)
                if de > fy.date_to:
                    de = fy.date_to
                period_obj.create({
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=interv)
        return True 