# Nove V1: The Bridal Gown Virtual Try On
> Powering the "Magic Mirror" for Brides and the "Digital Showroom" for Boutiques.

## 1. Executive Summary
Nove is an AI-orchestrated marketplace that connects high-intent brides with local boutique inventory through a hyper-realistic Virtual Try-On (VTO) experience. We use **SAM 3** for body and garment segmentation and **ANNY** for dynamic fabric warping, all orchestrated via the **Stitch** backend.

## 2. Technical Core: The Stitch Engine
Nove utilizes a server-side pipeline to ensure high-fidelity renders without taxing mobile hardware.

| Stage | Actor | Technology | Output |
| :--- | :--- | :--- | :--- |
| **Ingress (B2C)** | Bride | Mobile SDK / MediaPipe | Validated A-Pose Silhouette |
| **Ingress (B2B)** | Boutique | Mobile SDK / SAM 3 | Background-removed Garment Asset |
| **Processing** | Stitch | SAM 3 | Part-Level Segmentation Mask |
| **Fitting** | Stitch | ANNY | Warped, Physics-Aware Garment |
| **Egress** | App | Web-Sockets | The "Magic Moment" Render |



## 3. Dual-Sided User Flows

### A. The Bride's Journey (Discovery)
1. **The Vault:** Secure silhouette capture with on-device privacy masking.
2. **The Rack:** Browse localized inventory from partner boutiques.
3. **The Try-On:** Trigger a 'Stitch' request to see the dress warped to her unique shape.
4. **The Conversion:** Book a physical fitting. The app sends a "Lookbook" (renders + silhouette data) to the stylist.

### B. The Boutique's Journey (Inventory Ingestion)
1. **The Capture:** Take a photo of a dress on a mannequin in-store.
2. **Automated Digitization:** SAM 3 strips the background and normalizes the lighting.
3. **The Lead:** Receive high-intent booking requests including the bride's AI-generated "try-on" photos, reducing appointment time by 40%.

## 4. Revenue Model
* **Booking Fee:** $25 per appointment scheduled via Nove.
* **Discovery Fee:** Small micro-transaction to "unlock" unlimited try-ons for a specific boutique's inventory.
* **Lead Gen Revenue Share:** Commission on the final dress sale (Attributed via QR code at checkout).

## 5. Technical Implementation Checklist (Stitch Pipeline)

- [ ] **Boutique Asset Filter:** Fine-tune SAM 3 to distinguish between "White Dress" and "White Studio Wall."
- [ ] **Anchor Point Mapping:** Map ANNY warp points to standard boutique mannequin dimensions.
- [ ] **Lead Export:** Build a PDF generator for the "Stylist Packet."
- [ ] **Stripe Connect:** Integrate split-payment logic for booking fee revenue shares.
