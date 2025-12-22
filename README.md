# Nove

# Nove V1: AI-Powered Bridal Discovery
> The "Magic Mirror" experience powered by SAM 3, ANNY, and Stitch.

## 1. Vision
Nove is a high-end generative fitting room designed to eliminate the friction and emotional stress of bridal shopping. By leveraging state-of-the-art computer vision, we provide brides with a high-fidelity, private, and emotionally intelligent virtual try-on (VTO) experience.

## 2. Technical Stack
* **Segmentation:** SAM 3 (Segment Anything Model) - *Pixel-perfect body isolation.*
* **Warping Engine:** ANNY (Animation-over-any) - *Dynamic garment draping.*
* **Orchestration:** Stitch - *Backend pipeline management.*
* **Client:** React Native / Expo.

## 3. The "Stitch" Pipeline (Logic Flow)

The system operates as a generative pipe rather than a simple overlay tool:

| Stage | Input | Action | Output |
| :--- | :--- | :--- | :--- |
| **Ingress** | Mobile RAW | Client-side pose validation (MediaPipe). | Validated Payload |
| **Masking** | SAM 3 | Isolate body; segment into: Skin, Base Clothing, Environment. | Binary Part-Masks |
| **Fitting** | ANNY | Warp 2D/3D dress mesh onto SAM-defined coordinates. | Warped Asset |
| **Blending** | Post-Processor | Match grain, shadows, and lighting to the original photo. | Final Render |

[Image of a flowchart showing the integration of SAM 3 and ANNY models in an AI image processing pipeline]

## 4. Feature Requirements (MVP)

### A. The Studio (Capture)
* **Active Guidance:** UI "Ghost Overlay" to ensure a standardized A-pose.
* **Privacy-First:** Local pre-processing of silhouette masks.
* **Validation:** Automated rejection of poor lighting or occluded limbs.

### B. The Gallery (Discovery)
* **Vibe-Based Filtering:** Search by aesthetic (e.g., "Modern Minimalist") rather than just technical tags.
* **Parallel Processing:** Pre-segmenting the active silhouette while the user browses.

### C. The Magic Moment (VTO)
* **Real-time Reveal:** Shimmering animation to mask server-side inference latency (5–7s).
