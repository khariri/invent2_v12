import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class DJBCNofasPemusnahan(models.Model):
    _name = 'djbc.nofas_musnah'
    _description = 'DJBC Laporan Pemusnahan'
    _rec_name = 'no_pemusnahan'

    no_pemusnahan = fields.Char(string='Nomor Pemusnahan')
    tgl_pemusnahan = fields.Date(string='Tanggal Pemusnahan')
    kode_barang=fields.Char(string='Kode Barang')
    nama_barang=fields.Char(string='Nama Barang')
    jumlah = fields.Float(string='Jumlah')
    satuan = fields.Char(string='Satuan')
    location = fields.Char(string='Location')
    warehouse = fields.Char(string='Warehouse')

    @api.model_cr
    def init(self):
        self.env.cr.execute("""
        DROP FUNCTION IF EXISTS djbc_nofas_musnah(DATE, DATE);
        CREATE OR REPLACE FUNCTION djbc_nofas_musnah(date_start DATE, date_end DATE)
RETURNS VOID AS $BODY$
DECLARE
    
    csr cursor for
        select y.nomor_pemusnahan as no_pemusnahan,
            y.tanggal_pemusnahan as tgl_pemusnahan,
            xz.default_code as kode_barang,
            xz.name as nama_barang,
            xx.product_uom_qty as jumlah,
            yx.name as satuan,            
            t5.name as location,
            t8.name as warehouse
        from stock_move xx
        join stock_picking y on xx.picking_id=y.id
        join stock_picking_type t6 on t6.id = y.picking_type_id
        join res_partner z on z.id=y.partner_id
        left join res_partner t7 on t7.id = y.owner_id
        join stock_location t5 on t5.id = xx.location_id
        join stock_location t8 on t8.id = t5.location_id
        join stock_move_line t1 on t1.move_id = xx.id
        join product_product xy on xy.id=xx.product_id
        join product_template xz on xz.id=xy.product_tmpl_id        
        join uom_uom yx on yx.id=xx.product_uom
        
        where xx.state='done' 
        and t6.name like ('Pemusnahan')
        -- and t6.move_type like 'in'
        and y.tanggal_pemusnahan >= date_start and y.tanggal_pemusnahan<=date_end
        order by y.tanggal_pemusnahan;
    
    v_wh text;
           
BEGIN
    delete from djbc_nofas_musnah;
    -- v_wh='WH/Stock';
    
    for rec in csr loop
        insert into djbc_nofas_musnah (no_pemusnahan, tgl_pemusnahan, kode_barang,
            nama_barang, jumlah, satuan, location, warehouse) 
            values (rec.no_pemusnahan, rec.tgl_pemusnahan,
                rec.kode_barang, rec.nama_barang, rec.jumlah, rec.satuan, 
                rec.location, rec.warehouse) ;
        -- update stock_move set djbc_masuk_flag=TRUE where id=rec.id;
    end loop;
        
END;

$BODY$
LANGUAGE plpgsql;
        """)