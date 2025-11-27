# SehatKuy Order Management - User Guide

## Feature 1: Map-Based Delivery Location Selection

### For Patients Creating Orders

#### How to Use:
1. Go to **Orders** → **Create New Order**
   - URL: `http://localhost:8000/pharmacy/orders/create/`

2. **Select Delivery Location on Map:**
   - The interactive map appears at the top of the form
   - Default center: Jakarta, Indonesia
   - **Click anywhere on the map** to select your delivery location
   - A green marker will appear showing your selected location

3. **Verify Coordinates:**
   - Below the map, you'll see read-only fields displaying:
     - **Latitude:** (example: -6.2088)
     - **Longitude:** (example: 106.8456)
   - These are automatically filled when you click the map

4. **Fill in Additional Details:**
   - **Alamat Pengiriman** (Delivery Address): Enter full address text
   - **Nomor Telepon Pengiriman** (Delivery Phone): Enter phone number
   - **Catatan Pesanan** (Order Notes): Optional additional notes

5. **Create Order:**
   - Click **"Buat Pesanan"** button
   - Your order is created with the selected delivery location
   - Next step: Add medicines to your order

#### Important Notes:
- The map coordinates are automatically saved with your order
- You can select different locations by clicking different areas
- The green marker shows your current selection
- Coordinates are stored as decimal degrees (e.g., -6.2088)

---

## Feature 2: Patient Order Confirmation

### For Patients Confirming Receipt

#### How to Use:

1. **Receive Your Order:**
   - Wait for admin to process and deliver your order
   - Order status will change from "Menunggu Konfirmasi" → "Dikonfirmasi" → "Dalam Pengiriman" → "Terkirim"

2. **Visit Order Detail Page:**
   - Go to **Pesanan Saya** (My Orders) → Select your order
   - Or directly access: `http://localhost:8000/pharmacy/orders/{order_id}/`

3. **Confirm Receipt:**
   - When order status is **"Terkirim"** (Delivered), you'll see:
     - **"Konfirmasi Penerimaan Obat"** button (green)
   - Click this button

4. **Confirmation Page:**
   - Review your order details:
     - Order number
     - Delivery address
     - Phone number
     - Total price
     - List of medicines received
   - Verify all medicines match what you ordered

5. **Submit Confirmation:**
   - Click **"Konfirmasi Penerimaan Obat"** button
   - System records:
     - Status changes to **"Diterima Pasien"** (Received by Patient)
     - Receipt timestamp is recorded
   - You'll see success message: "Terima kasih! Obat telah dikonfirmasi diterima."

#### After Confirmation:
- Order detail page shows:
  - Status: "Diterima Pasien"
  - Confirmation time: Displayed on the page
  - Order is marked as complete

---

## Workflow Visualization

```
PATIENT FLOW:
┌─────────────────────────────────────┐
│  Create Order (Select Location)    │
│  - Click map to select delivery    │
│  - Coordinates auto-saved          │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Add Medicines to Order            │
│  - Select medicines from pharmacy  │
│  - Set quantities                  │
│  - Confirm order                   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Order Processing (Admin)          │
│  - Status: Dikonfirmasi            │
│  - Status: Sedang Diproses         │
│  - Status: Siap Dikirim            │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Order Shipped & Delivered         │
│  - Status: Dalam Pengiriman        │
│  - Status: Terkirim                │
│  - Confirmation button becomes     │
│    available                       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Patient Confirms Receipt          │
│  - Click confirmation button       │
│  - Review order details            │
│  - Submit confirmation             │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Order Complete                    │
│  - Status: Diterima Pasien         │
│  - Receipt timestamp recorded      │
│  - Order marked complete           │
└─────────────────────────────────────┘
```

---

## Coordinate System Reference

### Location Format:
- **Latitude:** North-South position (-90 to +90 degrees)
  - Negative = South
  - Positive = North
  - Example: -6.2088 (South of Equator - Jakarta area)

- **Longitude:** East-West position (-180 to +180 degrees)
  - Negative = West
  - Positive = East
  - Example: 106.8456 (East - Jakarta area)

### Example Locations:
- **Jakarta:** -6.2088, 106.8456
- **Bandung:** -6.9175, 107.6123
- **Surabaya:** -7.2575, 112.7521
- **Medan:** 3.1957, 98.6722

### Precision:
- All coordinates are stored with 6 decimal places
- This provides precision to approximately 0.1 meters

---

## Order Status Codes

| Status | Label | Meaning |
|--------|-------|---------|
| pending | Menunggu Konfirmasi | Awaiting system confirmation |
| confirmed | Dikonfirmasi | Admin has confirmed order |
| processing | Sedang Diproses | Order is being prepared |
| ready | Siap Dikirim | Order ready for shipment |
| shipped | Dalam Pengiriman | Order is in transit |
| **delivered** | **Terkirim** | **Order delivered to patient** |
| **received** | **Diterima Pasien** | **Patient confirmed receipt** |
| completed | Selesai | Order is complete |
| cancelled | Dibatalkan | Order was cancelled |

---

## Troubleshooting

### Map Not Loading:
- **Issue:** Map appears blank
- **Solution:** 
  - Check internet connection
  - Refresh page
  - Clear browser cache
  - Check browser console for errors

### Coordinates Not Saving:
- **Issue:** Delivery coordinates show as empty
- **Solution:**
  - Click on the map to set coordinates
  - Ensure click registers (marker appears)
  - Check hidden fields are filled (F12 → Inspector → find 'delivery_latitude')

### Confirmation Button Not Appearing:
- **Issue:** "Konfirmasi Penerimaan" button not visible
- **Solution:**
  - Check order status is "delivered" (Terkirim)
  - Ensure you're logged in as the patient who placed the order
  - Refresh the page

### Cannot Submit Confirmation:
- **Issue:** Form submission fails
- **Solution:**
  - Ensure you're on the correct confirmation page
  - Check if order status changed to "delivered"
  - Try again or contact admin

---

## Admin Notes

### Managing Orders:
1. View all orders: **Admin Panel** → **Orders**
2. Change order status: Edit order → Update status
3. Track deliveries: View order → See delivery map
4. Monitor confirmations: Check "Status" column for "Diterima Pasien"

### Key Information:
- Delivery coordinates are stored in `delivery_latitude` and `delivery_longitude` fields
- Receipt timestamp is recorded in `received_at` field
- Confirmation can only be done by the patient who owns the order
- Confirmation is permanent and cannot be undone

---

## Quick Links

**Patient Actions:**
- Create Order: `/pharmacy/orders/create/`
- View My Orders: `/pharmacy/orders/`
- Order Detail: `/pharmacy/orders/{id}/`
- Confirm Receipt: `/pharmacy/orders/{id}/confirm-receipt/`

**Admin Actions:**
- View All Orders: `/adminpanel/` (or `/users/admin/dashboard/`)
- Manage Medicines: `/pharmacy/medicines/`
- View Deliveries: `/pharmacy/delivery/{order_id}/map/`

---

## Support

For issues or questions:
1. Contact admin panel
2. Check order status in detail page
3. Review order history and timestamps
4. Contact system administrator if needed

---

**Last Updated:** November 26, 2025
**Version:** 1.0 - Initial Release
