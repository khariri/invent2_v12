import logging

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class DJBCMutasiWizard(models.TransientModel):
    _name='djbc.mutasiwizardv3'

    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')
    djbc_category_id = fields.Many2one(comodel_name="djbc.categs", string="DJBC Category", required=False, )
    kategori = fields.Char(string="Kategori")
    
    @api.multi 	
    def generate_laporan(self):
        cr=self.env.cr
        # _logger.info(self.djbc_category_id.id)
        cr.execute("select djbc_mutasi_v3(%s,%s,%s)",(self.date_start, self.date_end, self.djbc_category_id.id))
        waction = self.env.ref("djbc_mutasi_v3.""mutasi_v3_action")
        result = waction.read()[0]
        return result

    @api.multi
    def generate_laporan_xls(self):
        cr=self.env.cr
        cr.execute("select djbc_mutasi_v3(%s,%s,%s)",(self.date_start, self.date_end, self.djbc_category_id.id))
        data = {
            'model': 'djbc.mutasiwizardv3',
            'form': self.read()[0]
        }
        
        return self.env.ref('djbc_mutasi_v3.mutasi_v3_xlsx').report_action(self, data=data)


    @api.onchange('date_end')
    @api.multi
    def onchange_date(self):
        res={}
        if self.date_start>self.date_end:
            res = {'warning':{
                'title':('Warning'),
                'message':('Tanggal Akhir Lebih Kecil Dari Tanggal Mulai')}}
        if res:
            return res


    @api.onchange('djbc_category_id')
    @api.multi
    def onchange_kategori(self):
        self.kategori = self.djbc_category_id.name
        return


