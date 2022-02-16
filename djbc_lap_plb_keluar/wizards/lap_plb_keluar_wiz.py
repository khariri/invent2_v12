from odoo import models, fields, api


class DJBCPLBKeluarWizard(models.TransientModel):
    _name = "djbc.lap.plb.keluar.wizard"
    date_start = fields.Date(string='Date Start')
    date_end = fields.Date(string='Date End')

    @api.multi
    def call_djbc_lap_plb_keluar(self):
        cr = self.env.cr
        cr.execute("select djbc_lap_plb_keluar(%s,%s)",(self.date_start, self.date_end))
        waction = self.env.ref("djbc_lap_plb_keluar.""lap_plb_keluar_action")
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

    @api.multi
    def generate_laporan_xls(self):
        cr=self.env.cr
        cr.execute("select djbc_lap_plb_keluar(%s,%s)",(self.date_start, self.date_end))
        data = {
            'model': 'djbc.lap.plb.keluar.wizard',
            'form': self.read()[0]
        }
        
        return self.env.ref('djbc_lap_plb_keluar.pengeluaran_plb_xlsx').report_action(self, data=data)
