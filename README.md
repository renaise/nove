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

## 5. Prototype Status (V0.1) ✅

**🎉 Working Prototype Built with Claude Opus 4.5!**

The Stitch Engine prototype is now operational with the following features:

### ✅ Completed
- [x] **AI Orchestration:** Full Claude Opus 4.5 integration for intelligent image analysis
- [x] **Bride Pipeline:** Upload, validation, and A-pose detection
- [x] **Boutique Pipeline:** Garment upload and quality assessment
- [x] **Virtual Try-On API:** Complete REST API with WebSocket support
- [x] **Real-time Updates:** WebSocket broadcasting for processing status
- [x] **Quality Validation:** AI-powered image quality checks and recommendations
- [x] **API Documentation:** Comprehensive docs in `API.md`

### 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Run the server
python run.py
```

**Server:** http://localhost:8000
**API Docs:** http://localhost:8000/docs
**Setup Guide:** See `SETUP.md`

### 🧠 AI Features (Opus 4.5)

The prototype uses Claude Opus 4.5 for:
- ✨ A-pose detection and body analysis
- ✨ Background separation validation ("white dress on white wall" problem)
- ✨ Size compatibility prediction
- ✨ Style matching insights
- ✨ Processing parameter optimization

### 📋 Next Steps (Production)

- [ ] **SAM 3 Integration:** Replace placeholder segmentation with real SAM 3
- [ ] **ANNY Integration:** Replace placeholder renders with actual fabric warping
- [ ] **Database:** Add PostgreSQL for inventory and user management
- [ ] **Authentication:** OAuth 2.0 for boutiques, JWT for brides
- [ ] **Lead Export:** Build PDF generator for the "Stylist Packet"
- [ ] **Stripe Connect:** Integrate split-payment logic for booking fees
- [ ] **CDN:** Set up CloudFront/CloudFlare for render delivery
- [ ] **Monitoring:** Add Sentry and Datadog

### 📁 Project Structure

```
nove/
├── stitch/              # Stitch Engine backend
│   ├── main.py          # FastAPI application
│   ├── orchestrator.py  # Opus 4.5 AI orchestration
│   ├── pipelines/       # Processing pipelines
│   └── utils/           # Image utilities
├── tests/               # Test suite
├── API.md              # API documentation
├── SETUP.md            # Setup guide
└── requirements.txt    # Python dependencies
```

### 🔗 Resources

- **Setup Instructions:** `SETUP.md`
- **API Documentation:** `API.md`
- **Run Server:** `python run.py`
