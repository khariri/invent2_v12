from odoo import fields, api, models
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning

class AccountPeriod(models.Model):
    _name           = "account.period"

    name                    = fields.Char('Period Name', required=True)
    code                    = fields.Char('Code', size=12)
    date_start              = fields.Date('Start of Period', required=True)
    date_stop               = fields.Date('End of Period', required=True)
    fiscalyear_id           = fields.Many2one('account.fiscal.year', 'Fiscal Year', required=True, index=True, ondelete='cascade')
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name of the period must be unique!'),
    ]

    def _check_duration(self):
        obj_period = self
        if obj_period.date_stop < obj_period.date_start:
            return False
        return True

    def _check_year_limit(self):
        for obj_period in self:
            if obj_period.fiscalyear_id.date_to < obj_period.date_stop or \
               obj_period.fiscalyear_id.date_to < obj_period.date_start or \
               obj_period.fiscalyear_id.date_from > obj_period.date_start or \
               obj_period.fiscalyear_id.date_from > obj_period.date_stop:
                return False

            pids = self.search([('date_to','>=',obj_period.date_start),('date_from','<=',obj_period.date_stop),('id','<>',obj_period.id)])
            if pids:
                return False
        return True

    _constraints = [
        (_check_duration, 'Error!\nThe duration of the Period(s) is/are invalid.', ['date_to']),
        (_check_year_limit, 'Error!\nThe period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the fiscal year.', ['date_to'])
    ]