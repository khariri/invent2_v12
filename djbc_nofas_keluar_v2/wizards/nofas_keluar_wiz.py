from odoo import models, fields, api


class DJBCNofasKeluarV2Wizard(models.TransientModel):
    _name = "djbc.nofas.keluar.v2.wizard"
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')

    @api.multi
    def call_djbc_nofas_keluar_v2(self):
        cr = self.env.cr
        cr.execute("select djbc_nofas_keluar_v2(%s,%s)",(self.date_start, self.date_end))
        waction = self.env.ref("djbc_nofas_keluar_v2.""nofas_keluar_v2_action")
        result = waction.read()[0]
        return result

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
