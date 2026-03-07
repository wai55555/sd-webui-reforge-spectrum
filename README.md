# sd-webui-reforge-spectrum

[日本語版はこちら (README_JP.md)](README_JP.md)

An extension for Stable Diffusion WebUI reForge that accelerates image generation by skipping UNet computations using Chebyshev polynomial forecasting.

## 🚀 Overview
Spectrum Accelerator implements an efficient "skip-and-predict" strategy for the UNet sampling process. By analyzing the trajectory of previous steps, it forecasts the next latent state, allowing the GPU to rest during skipped steps.

### Expected Performance (Example Results)
Comparison using SDXL (**checkpoint: :waiNSFWIllustrious_v140**) with **28 Steps**.

| Sampler | Setting | Time (Total) | Improvement |
| :--- | :--- | :--- | :--- |
| **Euler a** | OFF (No Hires) | 10.4s | Baseline |
| **Euler a** | **ON (No Hires)** | **5.4s** | **~2x Faster** |
| **Euler a** | OFF (with Hires) | 26.7s | Baseline |
| **Euler a** | **ON (with Hires)** | **21.9s** | Saved 4.8s |
| **DPM++ 2M SDE** | OFF (No Hires) | 24.9s | Baseline |
| **DPM++ 2M SDE** | **ON (No Hires)** | **20.6s** | Saved 4.3s |
| **DPM++ 2M SDE** | OFF (with Hires) | 9.8s | Baseline |
| **DPM++ 2M SDE** | **ON (with Hires)** | **5.2s** | **~2x Faster** |
| **DPM++ SDE** | OFF (No Hires) | 18.7s | Baseline |
| **DPM++ SDE** | **ON (No Hires)** | **15.3s** | Saved 3.4s |
| **DPM++ SDE** | OFF (with Hires) | 40.9s | Baseline |
| **DPM++ SDE** | **ON (with Hires)** | **36.6s** | Saved 4.3s |

> [!NOTE]
> Spectrum only accelerates the **main UNet sampling loop**. Post-processing (VAE, Hires pass, ADetailer) is not affected.

## 🖼 Comparison Samples
*Checkpoint: :waiNSFWIllustrious_v140*

### Euler a (28 Steps)
| OFF (10.4s) | ON (5.4s) |
| :---: | :---: |
| ![Original](sample_img/28step_nohires_Euler%20a%2010.4s%20764278507-waiNSFWIllustrious_v140.webp) | ![Spectrum ON](sample_img/spectrum_28step_nohires_Euler%20a_5.4s%20764278507-waiNSFWIllustrious_v140.webp) |

### DPM++ 2M SDE (28 Steps)
| OFF (24.9s) | ON (20.6s) |
| :---: | :---: |
| ![OFF](sample_img/28step_nohires_DPM++%202M%20SDE%2024.9s%20%20199638700-waiNSFWIllustrious_v140.webp) | ![ON](sample_img/spectrum_28step_nohires_DPM++%202M%20SDE%2020.6s%20199638700-waiNSFWIllustrious_v140.webp) |

### DPM++ SDE (28 Steps)
| OFF (18.7s) | ON (15.3s) |
| :---: | :---: |
| ![OFF](sample_img/28step_nohires_DPM++%20SDE%2018.7s%20199638700-waiNSFWIllustrious_v140.webp) | ![ON](sample_img/spectrum_28step_nohires_DPM++%20SDE%2015.3s%20%20199638700-waiNSFWIllustrious_v140.webp) |

### Hires. fix Comparison (28 Steps)

| Sampler | OFF | ON |
| :--- | :---: | :---: |
| **Euler a** | ![OFF](sample_img/28step_hires_Euler%20a%2026.7s%20764278507-waiNSFWIllustrious_v140.webp) (26.7s) | ![ON](sample_img/spectrum_28step_hires_Euler%20a%2021.9s%20764278507-waiNSFWIllustrious_v140.webp) (**21.9s**) |
| **DPM++ 2M SDE**| ![OFF](sample_img/28step_hires_DPM++%202M%20SDE%209.8s%20199638700-waiNSFWIllustrious_v140.webp) (9.8s) | ![ON](sample_img/spectrum_28step_hires_DPM++%202M%20SDE%205.2s%20199638700-waiNSFWIllustrious_v140.webp) (**5.2s**) |
| **DPM++ SDE** | ![OFF](sample_img/28step_hires_DPM++%20SDE%2040.9s%20%20199638700-waiNSFWIllustrious_v140.webp) (40.9s) | ![ON](sample_img/spectrum_28step_hires_DPM++%20SDE%2036.6s%20199638700-waiNSFWIllustrious_v140.webp) (**36.6s**) |

## 🛠 Parameters & Recommended Values

| Parameter | Range | Recommended | Description |
| :--- | :--- | :--- | :--- |
| **w (Blend Weight)** | 0.0 - 1.0 | **0.40** | Blends Taylor expansion and Chebyshev prediction. |
| **m (Complexity)** | 1 - 8 | **3** | Order of Chebyshev polynomials. |
| **Window Size** | 1 - 10 | **2** | How many steps to skip before a real calculation. |
| **Flex Window** | 0.0 - 2.0 | **0.20** | Gradually increases window size during sampling. |
| **Warmup Steps** | 0 - 20 | **4** | Real steps at the start to establish trajectory. |
| **Stop Offset** | 0 - 100 | **3** | Stop skipping at the very end to preserve micro-details. |

## 📦 Installation
1. Open the **Extensions** tab in your reForge WebUI.
2. Select **Install from URL**.
3. Paste the repository URL and click **Install**.
4. Restart your WebUI.

## 📜 Credits & References
*   **Paper**: [Adaptive Spectral Feature Forecasting for Diffusion Sampling Acceleration](https://arxiv.org/abs/2603.01623)
*   **Project Page**: [https://hanjq17.github.io/Spectrum/](https://hanjq17.github.io/Spectrum/)
*   **Official Implementation**: [hanjq17/Spectrum](https://github.com/hanjq17/Spectrum)
*   **ComfyUI Implementation**: [ruwwww/ComfyUI-Spectrum-sdxl](https://github.com/ruwwww/comfyui-spectrum-sdxl)

## ⚖️ License
This project is licensed under the **MIT License**.
