# sd-webui-reforge-spectrum (日本語版)

[English README is here](README.md)

Stable Diffusion WebUI reForge 用の拡張機能です。チェビシェフ多項式を用いた予測（Forecasting）アルゴリズムにより、UNet の計算を適宜スキップすることで画像生成を高速化します。

## 🚀 原理と概要
Spectrum Accelerator は、サンプリング工程における UNet の出力を「毎回計算するのではなく、過去の軌跡から予測する」という戦略をとります。

1.  **実計算**: 指定された間隔（Window Size）で通常の GPU 計算を行います。
2.  **階差分析**: 過去数ステップの latent の変化を分析し、次の状態を近似します。
3.  **予測スキップ**: 近似予測値を用いることで UNet 計算をスキップし、処理速度を向上させます。

### 📊 生成速度の実測結果
SDXL (**checkpoint: :waiNSFWIllustrious_v140**) / 28 Steps での検証。

| サンプラー | 設定 | 合計時間 | 向上の目安 |
| :--- | :--- | :--- | :--- |
| **Euler a** | OFF (通常の生成) | 10.4s | 基準 |
| **Euler a** | **ON (加速有効)** | **5.4s** | **約2倍の高速化** |
| **Euler a** | OFF (Hiresあり) | 26.7s | 基準 |
| **Euler a** | **ON (Hiresあり)** | **21.9s** | 約4.8秒短縮 |
| **DPM++ 2M SDE** | OFF (通常の生成) | 24.9s | 基準 |
| **DPM++ 2M SDE** | **ON (加速有効)** | **20.6s** | 約4.3秒短縮 |
| **DPM++ 2M SDE** | OFF (Hiresあり) | 9.8s | 基準 |
| **DPM++ 2M SDE** | **ON (Hiresあり)** | **5.2s** | **約2倍の高速化** |
| **DPM++ SDE** | OFF (通常の生成) | 18.7s | 基準 |
| **DPM++ SDE** | **ON (加速有効)** | **15.3s** | 約3.4秒短縮 |
| **DPM++ SDE** | OFF (Hiresあり) | 40.9s | 基準 |
| **DPM++ SDE** | **ON (Hiresあり)** | **36.6s** | 約4.3秒短縮 |

> [!NOTE]
> 本拡張機能は **メインの UNet サンプリングループのみ** を加速します。VAEデコード、Hires. fix の二次パス、ADetailer などの処理は影響を受けないため、それらが含まれるワークフローでは全体に対する短縮率は小さく見えます。

## 🖼 比較サンプル
*Checkpoint: :waiNSFWIllustrious_v140*

### 通常生成 (28 Steps)
サンプラーごとの ON/OFF 比較。

| サンプラー | OFF | ON |
| :--- | :---: | :---: |
| **Euler a** | ![Original](sample_img/28step_nohires_Euler%20a%2010.4s%20764278507-waiNSFWIllustrious_v140.webp) (10.4s) | ![Spectrum ON](sample_img/spectrum_28step_nohires_Euler%20a_5.4s%20764278507-waiNSFWIllustrious_v140.webp) (**5.4s**) |
| **DPM++ 2M SDE**| ![OFF](sample_img/28step_nohires_DPM++%202M%20SDE%2024.9s%20%20199638700-waiNSFWIllustrious_v140.webp) (24.9s) | ![ON](sample_img/spectrum_28step_nohires_DPM++%202M%20SDE%2020.6s%20199638700-waiNSFWIllustrious_v140.webp) (**20.6s**) |
| **DPM++ SDE** | ![OFF](sample_img/28step_nohires_DPM++%20SDE%2018.7s%20199638700-waiNSFWIllustrious_v140.webp) (18.7s) | ![ON](sample_img/spectrum_28step_nohires_DPM++%20SDE%2015.3s%20%20199638700-waiNSFWIllustrious_v140.webp) (**15.3s**) |

### Hires. fix 有効時 (28 Steps)
高解像度化プロセスとの共存比較。

| サンプラー | OFF | ON |
| :--- | :---: | :---: |
| **Euler a** | ![OFF](sample_img/28step_hires_Euler%20a%2026.7s%20764278507-waiNSFWIllustrious_v140.webp) (26.7s) | ![ON](sample_img/spectrum_28step_hires_Euler%20a%2021.9s%20764278507-waiNSFWIllustrious_v140.webp) (**21.9s**) |
| **DPM++ 2M SDE**| ![OFF](sample_img/28step_hires_DPM++%202M%20SDE%209.8s%20199638700-waiNSFWIllustrious_v140.webp) (9.8s) | ![ON](sample_img/spectrum_28step_hires_DPM++%202M%20SDE%205.2s%20199638700-waiNSFWIllustrious_v140.webp) (**5.2s**) |
| **DPM++ SDE** | ![OFF](sample_img/28step_hires_DPM++%20SDE%2040.9s%20%20199638700-waiNSFWIllustrious_v140.webp) (40.9s) | ![ON](sample_img/spectrum_28step_hires_DPM++%20SDE%2036.6s%20199638700-waiNSFWIllustrious_v140.webp) (**36.6s**) |

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
*   **論文**: [Adaptive Spectral Feature Forecasting for Diffusion Sampling Acceleration](https://arxiv.org/abs/2603.01623)
*   **プロジェクトページ**: [https://hanjq17.github.io/Spectrum/](https://hanjq17.github.io/Spectrum/)
*   **公式リポジトリ**: [hanjq17/Spectrum](https://github.com/hanjq17/Spectrum)
*   **ComfyUI 実装**: [ruwwww/ComfyUI-Spectrum-sdxl](https://github.com/ruwwww/comfyui-spectrum-sdxl)

## ⚖️ ライセンス
本プロジェクトは **MIT License** の下で公開されています。
