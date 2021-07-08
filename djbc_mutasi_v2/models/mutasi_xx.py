from odoo import models, fields, api

class DJBCMutasi(models.Model):
    _name='djbc.mutasi_v2'
    _description='DJBC Laporan Mutasi'

    tgl_mulai = fields.Date(string = 'Tanggal Mulai')
    tgl_akhir = fields.Date(string = 'Tanggal Akhir')
    kode_barang=fields.Char (string='Kode Barang')
    nama_barang=fields.Char (string='Nama Barang')
    saldo_awal=fields.Float(string='Saldo Awal')
    pemasukan=fields.Float(string='Pemasukan')
    pengeluaran=fields.Float(string='Pengeluaran')
    penyesuaian=fields.Float(string='Penyesuaian')
    stock_opname=fields.Float(string='Stock Opname')
    saldo_akhir=fields.Float(string='Saldo Akhir')
    selisih=fields.Float(string='Selisih')
    keterangan=fields.Char(string='Keterangan')
    location=fields.Char(string='Location')
    warehouse=fields.Char(string='Warehouse')

    @api.model_cr
    def init(self):
        self.env.cr.execute("""
        DROP FUNCTION IF EXISTS djbc_mutasi_v2(DATE, DATE, INTEGER);
        CREATE OR REPLACE FUNCTION djbc_mutasi_v2(date_start DATE, date_end DATE, v_djbc_category_id INTEGER)
RETURNS VOID AS $BODY$

DECLARE
	v_date_start TIMESTAMP;
	v_date_end TIMESTAMP;


BEGIN
	v_date_start = date_start;
	v_date_end = date_end;
	delete from djbc_mutasi_v2;

    IF ( v_djbc_category_id IN (2,17,18,21,23)) THEN
        insert into djbc_mutasi_v2 (kode_barang, nama_barang, saldo_awal, pemasukan, pengeluaran, penyesuaian, stock_opname, saldo_akhir, selisih, keterangan, location, warehouse, tgl_mulai, tgl_akhir)
			select A.default_code as product_code,A.nama as product_name,B.saldo_awal as v_saldo_awal,A.pemasukan as v_pemasukan,
				A.pengeluaran as v_pengeluaran,0.00,0.00,(B.saldo_awal+A.pemasukan-A.pengeluaran) as v_saldo_akhir,0.00,' sesuai','WH/Stock','WH',v_date_start,v_date_end
				from
				(
					with _stock as (
						select s.reference,s.product_id,s.qty_done as transfer,spt.name as picking,p.state as st_pick,sm.unbuild_id,mrp.state as st_prod,
							s.date,sm.date_backdating,s.lot_produced_id from stock_move_line s
							left join stock_move sm on s.move_id=sm.id
							left join stock_picking p on s.picking_id=p.id
							left join stock_picking_type spt on sm.picking_type_id=spt.id
							left join mrp_production mrp on s.production_id=mrp.id

						where ((sm.date_backdating is not null and (sm.date_backdating >= v_date_start and sm.date_backdating <= v_date_end)) or
							(sm.date_backdating is null and (s.date >= v_date_start and s.date <= v_date_end))) and sm.state='done'
					)

						--header
						select pp.id,pp.default_code,tmp.name as nama,tmp.djbc_category_id as kategori,case when m.pemasukan is null then 0.00 else m.pemasukan end as pemasukan,
							case when k.pengeluaran is null then 0.00 else k.pengeluaran end as pengeluaran
							from ( select id,product_tmpl_id,default_code from product_product GROUP BY id ) pp
									left join product_template tmp on pp.product_tmpl_id=tmp.id
									left join djbc_categs d on tmp.djbc_category_id=d.id

						--Transaksi Masuk
						left join (
						select s.product_id,sum(s.transfer) as pemasukan from _stock s
						where (((s.picking='Adjustment In' or s.picking='Receipts') and s.st_pick='done') or (s.picking is null and s.unbuild_id is not null)) or
						(s.picking='Manufacturing' and s.st_prod='done' and s.lot_produced_id is null)
						group by s.product_id ) m on pp.id=m.product_id

						--Transaksi Keluar
						left join (
						select s.product_id, sum(s.transfer) as pengeluaran from _stock s
						where ((s.picking='Adjustment Out' or s.picking='Delivery Orders' or s.picking='Pemusnahan' or s.picking='Pengrusakan') and s.st_pick='done') or
						(s.picking='Manufacturing' and s.st_prod='done' and s.lot_produced_id is not null)
						group by s.product_id ) k on pp.id=k.product_id
						where tmp.djbc_category_id=v_djbc_category_id
						--where d.name = 'HASIL PRODUKSI'--'BARANG SETENGAH JADI'--'LIMBAH'--'SISA PENGEMAS'--'SISA / SCRAP'--'HASIL PRODUKSI'
				) as A


				-- Query Saldo
				left join (
					with _saldo as (
						select s.reference,s.product_id,s.qty_done as transfer,spt.name as picking,p.state as st_pick,sm.unbuild_id,mrp.state as st_prod,
						s.date,sm.date_backdating,s.lot_produced_id from stock_move_line s
						left join stock_move sm on s.move_id=sm.id
						left join stock_picking p on s.picking_id=p.id
						left join stock_picking_type spt on sm.picking_type_id=spt.id
						left join mrp_production mrp on s.production_id=mrp.id

						where ((sm.date_backdating is not null and (sm.date_backdating < v_date_start) or
							(sm.date_backdating is null and (s.date < v_date_start))) and sm.state='done'
						)
					)

						--header
						select pp.id,case when m.pemasukan is null and k.pengeluaran is not null then (0-k.pengeluaran) when m.pemasukan is not null and k.pengeluaran is null then m.pemasukan
							when m.pemasukan is null and k.pengeluaran is null then 0.00 else m.pemasukan-k.pengeluaran end as saldo_awal
							from ( select id,product_tmpl_id,default_code from product_product GROUP BY id ) pp
									left join product_template tmp on pp.product_tmpl_id=tmp.id
									left join djbc_categs d on tmp.djbc_category_id=d.id

						--Transaksi Masuk
						left join (
						select s.product_id,sum(s.transfer) as pemasukan from _saldo s
						where (((s.picking='Adjustment In' or s.picking='Receipts') and s.st_pick='done') or (s.picking is null and s.unbuild_id is not null)) or
																(s.picking='Manufacturing' and s.st_prod='done' and s.lot_produced_id is null)
						group by s.product_id ) m on pp.id=m.product_id

						--Transaksi Keluar
						left join (
						select s.product_id,sum(s.transfer) as pengeluaran from _saldo s
						where ((s.picking='Adjustment Out' or s.picking='Delivery Orders' or s.picking='Pemusnahan' or s.picking='Pengrusakan') and s.st_pick='done')
						or 	(s.picking='Manufacturing' and s.st_prod='done' and s.lot_produced_id is null)
						group by s.product_id ) k on pp.id=k.product_id
						where tmp.djbc_category_id=v_djbc_category_id
						--where d.name =  'HASIL PRODUKSI'--'BARANG SETENGAH JADI'--'LIMBAH'--'SISA PENGEMAS'--'SISA / SCRAP'--'HASIL PRODUKSI'
				) B on A.id=B.id;
	ELSE
		insert into djbc_mutasi_v2 (kode_barang, nama_barang, saldo_awal, pemasukan, pengeluaran, penyesuaian, stock_opname, saldo_akhir, selisih, keterangan, location, warehouse, tgl_mulai, tgl_akhir)
			select A.default_code,A.nama,B.saldo_awal,A.pemasukan,A.pengeluaran,0.00,0.00,(B.saldo_awal+A.pemasukan-A.pengeluaran) as saldo_akhir,
				0.00,' sesuai','WH/Stock','WH',v_date_start,v_date_end from (with _stock as (
				select s.reference,s.product_id,s.qty_done as transfer,spt.name as picking,p.state as st_pick,sm.unbuild_id,mrp.state as st_prod,
				s.date,sm.date_backdating from stock_move_line s
				left join stock_move sm on s.move_id=sm.id
				left join stock_picking p on s.picking_id=p.id
				left join stock_picking_type spt on sm.picking_type_id=spt.id
				left join mrp_production mrp on s.production_id=mrp.id

				where ((sm.date_backdating is not null and (sm.date_backdating >= v_date_start and sm.date_backdating <= v_date_end)) or
						(sm.date_backdating is null and (s.date >= v_date_start and s.date <= v_date_end))) and sm.state='done'
						)

				--header
				select pp.id,pp.default_code,tmp.name as nama,d.name as kategori,case when m.pemasukan is null then 0.00 else m.pemasukan end as pemasukan,
					case when k.pengeluaran is null then 0.00 else k.pengeluaran end as pengeluaran
					from ( select id,product_tmpl_id,default_code from product_product GROUP BY id ) pp
							left join product_template tmp on pp.product_tmpl_id=tmp.id
							left join djbc_categs d on tmp.djbc_category_id=d.id

				--Transaksi Masuk
				left join (
				select s.product_id,sum(s.transfer) as pemasukan from _stock s
				where (((s.picking='Adjustment In' or s.picking='Receipts') and s.st_pick='done') or (s.picking is null and s.unbuild_id is not null))
				group by s.product_id ) m on pp.id=m.product_id

				--Transaksi Keluar
				left join (
				select s.product_id, sum(s.transfer) as pengeluaran from _stock s
				where ((s.picking='Adjustment Out' or s.picking='Delivery Orders' or s.picking='Pemusnahan' or s.picking='Pengrusakan') and s.st_pick='done') or
														(s.picking='Manufacturing' and s.st_prod='done')
				group by s.product_id ) k on pp.id=k.product_id
				where tmp.djbc_category_id = v_djbc_category_id
				-- where d.name = 'BARANG CONTOH'--'BARANG KONSUMSI'--'BARANG MODAL SPARE PART'--'BAHAN BAKAR'--'PENGEMAS'--'BARANG MODAL MESIN & PERALATAN'--'BAHAN BAKU & PENOLONG'
				) as A


				-- Query Saldo
				left join (
				with _saldo as (
				select s.reference,s.product_id,s.qty_done as transfer,spt.name as picking,p.state as st_pick,sm.unbuild_id,mrp.state as st_prod,
				s.date,sm.date_backdating from stock_move_line s
				left join stock_move sm on s.move_id=sm.id
				left join stock_picking p on s.picking_id=p.id
				left join stock_picking_type spt on sm.picking_type_id=spt.id
				left join mrp_production mrp on s.production_id=mrp.id

				where ((sm.date_backdating is not null and (sm.date_backdating < v_date_start) or
						(sm.date_backdating is null and (s.date < v_date_start ))) and sm.state='done'
						)
				)

				--header
				select pp.id,case when m.pemasukan is null and k.pengeluaran is not null then (0-k.pengeluaran) when m.pemasukan is not null and k.pengeluaran is null then m.pemasukan
					when m.pemasukan is null and k.pengeluaran is null then 0.00 else m.pemasukan-k.pengeluaran end as saldo_awal
					from ( select id,product_tmpl_id,default_code from product_product GROUP BY id ) pp
							left join product_template tmp on pp.product_tmpl_id=tmp.id
							left join djbc_categs d on tmp.djbc_category_id=d.id

				--Transaksi Masuk
				left join (
				select s.product_id,sum(s.transfer) as pemasukan from _saldo s
				where (((s.picking='Adjustment In' or s.picking='Receipts') and s.st_pick='done') or (s.picking is null and s.unbuild_id is not null))
				group by s.product_id ) m on pp.id=m.product_id

				--Transaksi Keluar
				left join (
				select s.product_id,sum(s.transfer) as pengeluaran from _saldo s
				where ((s.picking='Adjustment Out' or s.picking='Delivery Orders' or s.picking='Pemusnahan' or s.picking='Pengrusakan') and s.st_pick='done') or
														(s.picking='Manufacturing' and s.st_prod='done')
				group by s.product_id ) k on pp.id=k.product_id
				where tmp.djbc_category_id = v_djbc_category_id
				-- where d.name = 'BARANG CONTOH'--'BARANG KONSUMSI'--'BARANG MODAL SPARE PART'--'BAHAN BAKAR'--'PENGEMAS'--'BARANG MODAL MESIN & PERALATAN'--'BAHAN BAKU & PENOLONG'
				) B on A.id=B.id;
    END IF;
END;



$BODY$
LANGUAGE plpgsql;
        """
        )

# for rec in csr loop

# 		insert into djbc_mutasi (kode_barang, nama_barang, saldo_awal, pemasukan, pengeluaran, penyesuaian, stock_opname, saldo_akhir, selisih, keterangan, location, warehouse, tgl_mulai, tgl_akhir)
# 			values (rec.product_code,rec.product_name,rec.v_saldo_awal,rec.v_pemasukan,rec.v_pengeluaran, 0.00, 0.00,rec.v_saldo_akhir, 0.00, 'sesuai', 'WH/Stock', 'WH', v_date_start,v_date_end);

# 	end loop;

