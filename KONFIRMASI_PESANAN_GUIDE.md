# PANDUAN: Mengubah Status Pesanan ke "Delivered" untuk Testing

## Masalah
Pasien tidak melihat tombol "Konfirmasi Penerimaan" karena status pesanan belum diubah menjadi "Delivered" (Terkirim).

## Solusi

### Cara 1: Menggunakan Django Admin (PALING MUDAH)

1. **Buka Admin Panel:**
   - URL: `http://127.0.0.1:8000/admin/`
   - Login dengan akun admin

2. **Pergi ke Pesanan (Pharmacy › Medicine Orders):**
   - Klik pada "Pharmacy"
   - Klik "Medicine orders"

3. **Pilih Pesanan:**
   - Cari pesanan yang ingin diubah statusnya
   - Klik untuk membukanya

4. **Ubah Status:**
   - Cari field "Status"
   - Ubah dari "Dikonfirmasi" menjadi "Terkirim" (Delivered)
   - Klik "Simpan"

5. **Verifikasi:**
   - Kembali ke halaman pesanan
   - Refresh halaman (`Ctrl+F5`)
   - Sekarang tombol "Konfirmasi Penerimaan" akan muncul

---

### Cara 2: Menggunakan Bulk Action (LEBIH CEPAT untuk banyak pesanan)

1. **Buka Admin Panel:**
   - URL: `http://127.0.0.1:8000/admin/`

2. **Pergi ke Pesanan:**
   - Pharmacy › Medicine Orders

3. **Pilih Pesanan yang Ingin Diubah:**
   - Centang checkbox di sebelah pesanan yang ingin diubah
   - Atau centang semua dengan "Select all"

4. **Gunakan Action:**
   - Di bagian bawah, pilih dari dropdown: "Ubah status ke Terkirim (Delivered)"
   - Klik "Go"

5. **Konfirmasi:**
   - Sistem akan menampilkan pesan sukses
   - Status pesanan langsung berubah untuk semua yang dipilih

---

### Cara 3: Menggunakan Command Line (Untuk Developer)

```bash
cd "d:\semester 5\sehatkuy\SehatKuy"
venv\Scripts\python.exe manage.py shell
```

Lalu di shell Python:

```python
from pharmacy.models import MedicineOrder

# Update semua pesanan menjadi delivered
MedicineOrder.objects.all().update(status='delivered')

# Atau untuk pesanan spesifik:
order = MedicineOrder.objects.get(order_number='ORD-20251126110630-1')
order.status = 'delivered'
order.save()
```

---

## Setelah Mengubah Status

1. **Login sebagai pasien (tidak admin)**
2. **Buka halaman pesanan:** `/pharmacy/orders/`
3. **Klik pesanan yang sudah diubah statusnya**
4. **Di bagian "Aksi" (sidebar kanan), sekarang akan muncul:**
   - ✅ Tombol "Konfirmasi Penerimaan" (hijau)

5. **Klik tombol untuk:**
   - Melihat halaman konfirmasi dengan detail pesanan
   - Mengkonfirmasi penerimaan obat
   - Melihat timestamp penerimaan

---

## Status yang Perlu untuk Menampilkan Tombol

**Tombol "Konfirmasi Penerimaan" hanya muncul ketika:**
- ✓ Status pesanan = "Terkirim" (Delivered)
- ✓ User adalah pasien pemilik pesanan

**Status pesanan yang tersedia:**
1. pending → Menunggu Konfirmasi
2. confirmed → Dikonfirmasi
3. processing → Sedang Diproses
4. ready → Siap Dikirim
5. shipped → Dalam Pengiriman
6. **delivered → Terkirim** ← (Status yang diperlukan!)
7. received → Diterima Pasien
8. completed → Selesai
9. cancelled → Dibatalkan

---

## Urutan Status yang Benar

```
Pending (Menunggu Konfirmasi)
   ↓ Admin mengkonfirmasi
Confirmed (Dikonfirmasi)
   ↓ Admin memproses
Processing (Sedang Diproses)
   ↓ Admin siapkan
Ready (Siap Dikirim)
   ↓ Kurir ambil
Shipped (Dalam Pengiriman)
   ↓ Kurir antar
Delivered (Terkirim) ← Pasien bisa klik tombol di sini!
   ↓ Pasien klik "Konfirmasi Penerimaan"
Received (Diterima Pasien)
   ↓ 
Completed (Selesai)
```

---

## Admin Panel Improvements

Kami sudah menambahkan fitur di admin:

### 1. **Status Badge dengan Warna**
- Setiap status punya warna berbeda untuk mudah diidentifikasi
- Hijau untuk "Received" (berhasil dikonfirmasi)
- Biru untuk "Delivered" (siap dikonfirmasi pasien)

### 2. **Bulk Actions**
- Pilih multiple pesanan
- Ubah status semua sekaligus dengan satu klik
- Action: "Ubah status ke Terkirim (Delivered)"

### 3. **Filter Improvements**
- Filter by status
- Filter by received_at (timestamp konfirmasi)
- Filter by created date

### 4. **Tampilan yang Lebih Baik**
- Kolom received_at ditampilkan di list view
- Koordinat delivery di-readonly sehingga tidak bisa diubah sembarangan
- Informasi lebih lengkap di fieldsets

---

## Troubleshooting

### Tombol masih tidak muncul setelah ubah status?
1. Refresh halaman (Ctrl+F5 atau Cmd+Shift+R)
2. Logout dan login kembali
3. Cek di browser console (F12) untuk error
4. Pastikan Anda login sebagai pasien, bukan admin

### Status tidak berubah di admin?
1. Klik "Simpan" atau "Save", jangan hanya "Lanjutkan Editing"
2. Tunggu halaman selesai di-reload
3. Kembali ke list pesanan dan cek ulang

### Pesanan tidak ada di list?
1. Cek filter (mungkin sudah di-filter by status)
2. Gunakan search: cari order number atau username pasien
3. Nonaktifkan filter dengan klik "Clear all filters"

---

## Sekarang Sudah Siap!

✅ Admin panel sudah terupdate dengan fitur untuk mudah mengubah status
✅ Tombol konfirmasi akan muncul setelah status diubah ke "Delivered"
✅ Pasien bisa klik tombol untuk konfirmasi penerimaan

**Silakan test sekarang!**
