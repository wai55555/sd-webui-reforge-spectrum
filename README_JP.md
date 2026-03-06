# sd-webui-reforge-spectrum (日本語版)

[English README is here](README.md)

Stable Diffusion WebUI reForge 用の拡張機能です。チェビシェフ多項式を用いた予測（Forecasting）アルゴリズムにより、UNet の計算を適宜スキップすることで画像生成を高速化します。

## 🚀 原理と概要
Spectrum Accelerator は、サンプリング工程における UNet の出力を「毎回計算するのではなく、過去の軌跡から予測する」という戦略をとります。

1.  **実計算**: 指定された間隔（Window Size）で通常の GPU 計算を行います。
2.  **階差分析**: 過去数ステップの latent の変化を分析し、次の状態を近似します。
3.  **予測スキップ**: 近似予測値を用いることで UNet 計算をスキップし、処理速度を向上させます。

### 📊 生成速度の実測結果
SDXL (WAI Illustrious v14) / 28 Steps / Euler a での検証。

| 設定 | 合計時間 | UNet単体時間（推定） | 向上の目安 |
| :--- | :--- | :--- | :--- |
| **OFF (通常の生成)** | 10.4s | ~10.4s | 基準 |
| **ON (加速有効)** | **5.4s** | ~5.4s | **約2倍の高速化** |
| **OFF (Hiresあり)** | 26.7s | - | 基準 |
| **ON (Hiresあり)** | **21.9s** | - | **約4.8秒短縮** (UNet分) |

> [!NOTE]
> 本拡張機能は **メインの UNet サンプリングループのみ** を加速します。VAEデコード、Hires. fix の二次パス、ADetailer などの処理は影響を受けないため、それらが含まれるワークフローでは全体に対する短縮率は小さく見えますが、UNet 部の高速化は確実に機能しています。

## 🖼 比較サンプル
*Seed: 764278507, Euler a, 28 Steps*

| OFF (10.4s) | ON (5.4s) |
| :---: | :---: |
| ![Original](sample_img/28step_nohires_Euler%20a%2010.4s%20764278507-waiNSFWIllustrious_v140.webp) | ![Spectrum ON](sample_img/spectrum_28step_nohires_Euler%20a_5.4s%20764278507-waiNSFWIllustrious_v140.webp) |

| OFF with Hires (26.7s) | ON with Hires (21.9s) |
| :---: | :---: |
| ![Hires OFF](sample_img/28step_hires_Euler%20a%2026.7s%20764278507-waiNSFWIllustrious_v140.webp) | ![Hires ON](sample_img/spectrum_28step_hires_Euler%20a%2021.9s%20764278507-waiNSFWIllustrious_v140.webp) |

## 🛠 パラメータ設定と推奨値

| パラメータ | 範囲 | 推奨値 | 説明 |
| :--- | :--- | :--- | :--- |
| **w (Blend Weight)** | 0.0 - 1.0 | **0.40** | 予測の混合比。高いほど高速ですが画質が変化しやすくなります。 |
| **m (Complexity)** | 1 - 8 | **3** | チェビシェフ多項式の次数。 |
| **Window Size** | 1 - 10 | **2** | 何ステップごとに実計算を行うか。`2` は「1回計算・1回スキップ」です。 |
| **Flex Window** | 0.0 - 2.0 | **0.20** | サンプリングが進むにつれてWindow Sizeを動的に拡大します。 |
| **Warmup Steps** | 0 - 20 | **4** | 開始直後の助走ステップ。軌跡の安定化に必要です。 |
| **Stop Offset** | 0 - 100 | **3** | 終了間際のスキップを停止し、細部（瞳や質感を）を保護します。 |

## 📜 クレジットと参考文献
本プロジェクトは、以下の研究および実装に基づいています。

*   **論文**: [Adaptive Spectral Feature Forecasting for Diffusion Sampling Acceleration](https://arxiv.org/abs/2603.01623)
*   **プロジェクトページ**: [https://hanjq17.github.io/Spectrum/](https://hanjq17.github.io/Spectrum/)
*   **公式リポジトリ**: [hanjq17/Spectrum](https://github.com/hanjq17/Spectrum)
*   **ComfyUI 実装**: [ruwwww/ComfyUI-Spectrum-sdxl](https://github.com/ruwwww/comfyui-spectrum-sdxl)

### 著者 (Original Research)
Jiaqi Han, Juntong Shi, Puheng Li, Haotian Ye, Qiushan Guo, Stefano Ermon (Stanford University & ByteDance)

## ⚖️ ライセンス
本プロジェクトは **MIT License** の下で公開されています。
