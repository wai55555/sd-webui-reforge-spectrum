# sd-webui-reforge-spectrum

[日本語版はこちら (README_JP.md)](README_JP.md)

An extension for Stable Diffusion WebUI reForge that accelerates image generation by skipping UNet computations using Chebyshev polynomial forecasting.

## 🚀 Overview
Spectrum Accelerator implements an efficient "skip-and-predict" strategy for the UNet sampling process. By analyzing the trajectory of previous steps, it forecasts the next latent state, allowing the GPU to rest during skipped steps.

### Expected Performance
*   **UNet Speedup**: Up to **2x - 2.5x** increase in iterations per second (it/s).
*   **Total Generation Time**: **20% - 50% reduction**, depending on post-processing overhead (VAE, Adetailer, etc.).

## 🛠 Parameters & Recommended Values

| Parameter | Range | Recommended | Description |
| :--- | :--- | :--- | :--- |
| **w (Blend Weight)** | 0.0 - 1.0 | **0.40** | Blends Taylor expansion and Chebyshev prediction. Higher = faster but riskier. |
| **m (Complexity)** | 1 - 8 | **3** | Order of Chebyshev polynomials. |
| **Window Size** | 1 - 10 | **2** | How many steps to skip before a real calculation. 2 means every other step is predicted. |
| **Flex Window** | 0.0 - 2.0 | **0.20** | Gradually increases window size as sampling progresses. |
| **Warmup Steps** | 0 - 20 | **1** | Real calculation steps at the start before skipping begins. |
| **Stop Offset** | 0 - 100 | **1** | Stops skipping near the end of sampling to ensure final image crispness. |

## 📦 Installation
1. Open the **Extensions** tab in your reForge WebUI.
2. Select **Install from URL**.
3. Paste this repository URL and click **Install**.
4. Restart your WebUI.

---
*Special thanks to the reForge community for debugging and optimization support.*
