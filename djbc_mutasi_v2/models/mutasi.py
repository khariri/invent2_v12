from odoo import models, fields, api

class DJBCMutasi(models.Model):
    _name='djbc.mutasi_v2'
    _description='DJBC Laporan Mutasi v2'

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
        v_saldo_awal float;
		v_saldo_awal_in float;
		v_saldo_awal_out float;
		v_pemasukan float;
		v_pengeluaran float;
		v_saldo_akhir float;
		v_selisih float;
		v_penyesuaian float;
		v_penyesuaian_in float;
		v_penyesuaian_out float;
		v_stock_opname float;
		v_date_start TIMESTAMP;
		v_date_end TIMESTAMP;
		--v_nama_barang TEXT;
		--v_kode_barang TEXT;
		v_lokasi_barang TEXT;
		v_lokasi_id INTEGER;
		v_lokasi_adj_id INTEGER;
		v_so_exist TIMESTAMP;
		v_keterangan TEXT;
		v_lokasi_adjustment TEXT;
		query TEXT;
		rec RECORD;
		
		v_so_id INTEGER;
		v_so_date DATE;
		v_so_name TEXT;
		--v_djbc_category TEXT;

		v_cursor CURSOR FOR select x.id as product_id, y.name as product_name, y.default_code as product_code 
			from product_product x, product_template y where x.product_tmpl_id = y.id 
			and y.djbc_category_id=v_djbc_category_id; 

		v_location CURSOR FOR
			select t1.id, t1.name as location, t2.name as warehouse  
				from stock_location t1
				join stock_location t2 on t2.id = t1.location_id
				where t1.is_stock_location = 'TRUE';
		   
BEGIN
	delete from djbc_mutasi_v2;
	
	v_date_start = date_start;
	v_date_end = date_end;
	--v_djbc_category = djbc_category;
	--v_kode_barang='bj01';
	--v_nama_barang='bj01';
	v_lokasi_barang='WH/Stock';
	v_lokasi_adjustment='Inventory adjustment';
	
	-- select id from stock_location where complete_name like '%'||v_lokasi_barang into v_lokasi_id;
	select id from stock_location where complete_name like '%'||v_lokasi_adjustment into v_lokasi_adj_id;

	RAISE NOTICE 'lokasi stock id in %', v_lokasi_id;
	RAISE NOTICE 'lokasi adj id %', v_lokasi_adj_id;
	
	--query:='select x.id as product_id, y.name as product_name, y.default_code as product_code 
	--	from product_product x, product_template y where x.product_tmpl_id = y.id 
	--	and y.djbc_category=%','bb';
	
	for loc in v_location loop
		v_lokasi_id = loc.id;
	
	FOR rec IN v_cursor LOOP
		v_saldo_awal_in=0;
		v_saldo_awal_out=0;
		v_saldo_awal=0;
		v_saldo_akhir=0;
		v_pemasukan=0;
		v_pengeluaran=0;
		v_keterangan='sesuai';
		
		raise notice 'product id %', rec.product_id;
		raise notice 'product name %', rec.product_name;

		--select sum(qty_done) from stock_move_line x, product_product y, product_template z 
		--	where x.product_id=y.id and y.product_tmpl_id=z.id and z.name=v_nama_barang
		--	and x.date<=v_date_start and location_dest_id=v_lokasi_id and location_id<>v_lokasi_id into v_saldo_awal_in;

		select sum(qty_done) from stock_move_line x 
			join stock_picking t1 on t1.id = x.picking_id
			-- join stock_picking_type t2 on t2.id = t1.picking_type_id	 
			where x.product_id=rec.product_id and x.state='done'
			--and x.location_dest_id = loc.id
			and date(t1.date_done)<v_date_start
			-- and t2.move_type like 'in'  
			and x.location_dest_id=v_lokasi_id and x.location_id<>v_lokasi_id 
			into v_saldo_awal_in;

		if v_saldo_awal_in is NULL then
			v_saldo_awal_in=0;
		end if;

		RAISE NOTICE 'saldo awal in %', v_saldo_awal_in;

		--select sum(qty_done) from stock_move_line x, product_product y, product_template z 
		--	where x.product_id=y.id and y.product_tmpl_id=z.id and z.name=v_nama_barang 
		--	and x.date<=v_date_start and location_dest_id<>v_lokasi_id and location_id=v_lokasi_id into v_saldo_awal_out;
		
		select sum(qty_done) from stock_move_line x 
			join stock_picking t1 on t1.id = x.picking_id
			-- join stock_picking_type t2 on t2.id = t1.picking_type_id
			where x.product_id=rec.product_id and x.state='done'
			and date(t1.date_done)<v_date_start 
			-- and t2.move_type like 'out'
			-- and x.location_id = loc.id
			and x.location_dest_id<>v_lokasi_id and x.location_id=v_lokasi_id 
			into v_saldo_awal_out;
		
		if v_saldo_awal_out is NULL then
			v_saldo_awal_out=0;
		end if;

		RAISE NOTICE 'saldo awal out %', v_saldo_awal_out;

		v_saldo_awal=v_saldo_awal_in-v_saldo_awal_out;
		
		RAISE NOTICE 'saldo awal %', v_saldo_awal;

			
		select x.id, date(x.date), x.name from stock_inventory x 
			where x.djbc_mark and x.state='done' and date(x.date) =v_date_end
			and x.location_id = v_lokasi_id
			ORDER BY date DESC LIMIT 1 into v_so_id, v_so_date, v_so_name;
		
		v_stock_opname=0;
		v_penyesuaian=0;
		v_selisih=0;
		v_penyesuaian_in=0;
		v_penyesuaian_out=0;
		v_keterangan='';

		if v_so_id is NULL then

			
		else
			select sum(qty_done) from stock_move_line x 
				where x.product_id=rec.product_id and x.reference='INV:' || v_so_name
				and date(x.date)=v_so_date 
				and location_dest_id=v_lokasi_id and x.state='done' and
				location_id=v_lokasi_adj_id into v_penyesuaian_in;

			
			if v_penyesuaian_in is NULL then
				v_penyesuaian_in=0;
			end if;

			RAISE NOTICE 'penyesuaian in %', v_penyesuaian_in;

				
			select sum(qty_done) from stock_move_line x 
				where x.product_id=rec.product_id and x.reference='INV:' || v_so_name
				and date(x.date)=v_so_date  and location_dest_id=v_lokasi_adj_id 
				and location_id=v_lokasi_id and x.state='done' 
				into v_penyesuaian_out;
						
			if v_penyesuaian_out is NULL then
				v_penyesuaian_out=0;
			end if;

			RAISE NOTICE 'penyesuaian out %', vb_penyesuaian_out;

			v_penyesuaian = v_penyesuaian_in - v_penyesuaian_out;

			RAISE NOTICE 'penyesuaian %', v_penyesuaian;
	
			select sum(product_qty) from stock_inventory_line x
				where x.product_id=rec.product_id and x.inventory_id=v_so_id into v_stock_opname;

		end if;

		-- if v_so_id is NULL then

			-- RAISE NOTICE 'ga ada stock opname';

		
			select sum(qty_done) from stock_move_line x
				join stock_picking t1 on t1.id = x.picking_id
				-- join stock_picking_type t2 on t2.id = t1.picking_type_id 
				where x.product_id=rec.product_id and x.state='done'
				and date(t1.date_done)>=v_date_start and date(t1.date_done)<=v_date_end
				-- and t2.move_type like 'in'
				-- and x.location_dest_id = loc.id 
				and x.location_dest_id=v_lokasi_id and x.location_id<>v_lokasi_id 
				into v_pemasukan;
			
			if v_pemasukan is NULL then 
				v_pemasukan=0;
			end if;

				
			select sum(qty_done) from stock_move_line x 
				join stock_picking t1 on t1.id = x.picking_id
				-- join stock_picking_type t2 on t2.id = t1.picking_type_id
				where x.product_id=rec.product_id and x.state='done'
				and date(t1.date_done)>=v_date_start and date(t1.date_done)<=v_date_end  
				and x.location_dest_id<>v_lokasi_id and x.location_id=v_lokasi_id
				-- and t2.move_type like 'out'
				-- and x.location_id = loc.id 
				into v_pengeluaran;
			
			if v_pengeluaran is NULL then 
				v_pengeluaran=0;
			end if;

		
		
		
			if v_so_id is not NULL then
				
				v_pemasukan = v_pemasukan - v_penyesuaian_in;
				v_pengeluaran = v_pengeluaran - v_penyesuaian_out;


			end if;

			v_saldo_akhir = v_saldo_awal + v_pemasukan - v_pengeluaran + v_penyesuaian;
						
			if v_so_id is not NULL then	
						
				v_selisih = v_stock_opname - v_saldo_akhir;
			end if;

			if v_selisih>0 then
				v_keterangan='lebih';
			end if;

			if v_selisih<0 then
				v_keterangan='kurang';
			end if;

			if v_selisih=0 then
				v_keterangan='sesuai';
			end if;

			-- v_keterangan= v_keterangan + 'tgl so:' + v_so_exist;

		-- end if;

		RAISE NOTICE 'pemasukan %', v_pemasukan;
		RAISE NOTICE 'pengeluaran %', v_pengeluaran;
		RAISE NOTICE 'stock opname %', v_stock_opname;
		RAISE NOTICE 'saldo akhir %', v_saldo_akhir;
		RAISE NOTICE 'selisih %', v_selisih;
		RAISE NOTICE 'keterangan %', v_keterangan;

		insert into djbc_mutasi_v2 (kode_barang, nama_barang, saldo_awal, pemasukan, pengeluaran, penyesuaian, stock_opname, saldo_akhir, selisih, keterangan, location, warehouse, tgl_mulai, tgl_akhir)
			values (rec.product_code,rec.product_name,v_saldo_awal, v_pemasukan, v_pengeluaran, v_penyesuaian, v_stock_opname, v_saldo_akhir, v_selisih, v_keterangan, loc.location, loc.warehouse, v_date_start, v_date_end); 
	
	end loop;
	end loop;
END;



$BODY$
LANGUAGE plpgsql;
        """
        )
    

