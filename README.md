# sd-webui-reforge-spectrum

[日本語版はこちら (README_JP.md)](README_JP.md)

An extension for Stable Diffusion WebUI reForge that accelerates image generation by skipping UNet computations using Chebyshev polynomial forecasting.

## 🚀 Overview
Spectrum Accelerator implements an efficient "skip-and-predict" strategy for the UNet sampling process. By analyzing the trajectory of previous steps, it forecasts the next latent state, allowing the GPU to rest during skipped steps.

### Expected Performance (Example Results)
Comparison using SDXL (WAI Illustrious v14) with **28 Steps / Euler a**.

| Setting | Time (Total) | Time (UNet Only) | Improvement |
| :--- | :--- | :--- | :--- |
| **OFF (No Hires)** | 10.4s | ~10.4s | Baseline |
| **ON (No Hires)** | **5.4s** | ~5.4s | **~2x Faster** |
| **OFF (with Hires)** | 26.7s | - | Baseline |
| **ON (with Hires)** | **21.9s** | - | **Saved 4.8s** (Same as main UNet gain) |

> [!NOTE]
> Spectrum only accelerates the **main UNet sampling loop**. Post-processing (VAE, Hires pass, ADetailer) is not affected, which explains why the total time gain appears smaller in high-resolution workflows.

## 🖼 Comparison Samples
*Identical Seed: 764278507, Euler a, 28 Steps*

| OFF (10.4s) | ON (5.4s) |
| :---: | :---: |
| ![Original](sample_img/28step_nohires_Euler%20a%2010.4s%20764278507-waiNSFWIllustrious_v140.webp) | ![Spectrum ON](sample_img/spectrum_28step_nohires_Euler%20a_5.4s%20764278507-waiNSFWIllustrious_v140.webp) |

| OFF with Hires (26.7s) | ON with Hires (21.9s) |
| :---: | :---: |
| ![Hires OFF](sample_img/28step_hires_Euler%20a%2026.7s%20764278507-waiNSFWIllustrious_v140.webp) | ![Hires ON](sample_img/spectrum_28step_hires_Euler%20a%2021.9s%20764278507-waiNSFWIllustrious_v140.webp) |

## 🛠 Parameters & Recommended Values

| Parameter | Range | Recommended | Description |
| :--- | :--- | :--- | :--- |
| **w (Blend Weight)** | 0.0 - 1.0 | **0.40** | Blends Taylor expansion and Chebyshev prediction. |
| **m (Complexity)** | 1 - 8 | **3** | Order of Chebyshev polynomials. |
| **Window Size** | 1 - 10 | **2** | How many steps to skip before a real calculation. |
| **Flex Window** | 0.0 - 2.0 | **0.20** | Gradually increases window size during sampling. |
| **Warmup Steps** | 0 - 20 | **4** | Real steps at the start to establish trajectory. |
| **Stop Offset** | 0 - 100 | **3** | Stop skipping at the very end to preserve micro-details. |

## 📜 Credits & References
This extension is based on the research and implementations below:

*   **Paper**: [Adaptive Spectral Feature Forecasting for Diffusion Sampling Acceleration](https://arxiv.org/abs/2603.01623)
*   **Project Page**: [https://hanjq17.github.io/Spectrum/](https://hanjq17.github.io/Spectrum/)
*   **Official Implementation**: [hanjq17/Spectrum](https://github.com/hanjq17/Spectrum)
*   **ComfyUI Implementation**: [ruwwww/ComfyUI-Spectrum-sdxl](https://github.com/ruwwww/comfyui-spectrum-sdxl)

### Authors (Original Research)
Jiaqi Han, Juntong Shi, Puheng Li, Haotian Ye, Qiushan Guo, Stefano Ermon (Stanford University & ByteDance)

## ⚖️ License
This project is licensed under the **MIT License**.
