# Nove V1: The Digital Stylist
> Bridging the gap between body proportions and the "Yes" Dress.

## 1. The Stylist Pipeline
Nove uses a 4-stage intelligent flow to move from raw photo to curated vision.

| Stage | Action | Technology | Goal |
| :--- | :--- | :--- | :--- |
| **1. Capture** | Silhouette Upload | SAM 3 + MediaPipe | Extract clean body mask + 12-point landmarks. |
| **2. Analysis** | Proportion Logic | Custom CV Model | Determine shoulder-to-waist and waist-to-hip ratios. |
| **3. Curation** | Silhouette Match | Recommendation Engine | Map proportions to styles (e.g., A-Line, Mermaid, Ballgown). |
| **4. Vision** | Generative Try-On | Nano Banana Pro | Render 3 high-fidelity "Hero" previews to sell the vision. |

## 2. Updated User Story: "The Guided Discovery"
1. **The Scan:** User uploads a silhouette.
2. **The Feedback:** "We've analyzed your proportions. Your frame is beautifully suited for **A-Line** and **Empire Waist** silhouettes."
3. **The Gallery:** App filters the boutique database to show *only* matching styles first.
4. **The Vision:** User taps "See the Vision." Nano Banana Pro generates a photorealistic render of her in the top-recommended style.

## 3. The "Stitch Contract" Update (V2)
The API payload must now include "Stylist Metadata":
* **Request:** Includes `body_ratios` and `target_silhouette_category`.
* **Response:** Returns `recommendation_logic` (Why this dress was chosen) to display as UI copy.



## 4. Boutique-End Integration
Boutiques now tag their inventory by **Silhouette Type**. 
* **Value Prop:** We don't just send them a lead; we send them a lead who already knows which silhouette flutters her frame, shortening the 90-minute appointment to 45 minutes.
