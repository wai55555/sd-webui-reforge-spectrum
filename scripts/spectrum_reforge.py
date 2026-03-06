import sys
import os
import math
import torch
import gradio as gr

from modules import scripts

# Add the parent directory to sys.path to easily import the spectrum_core
extension_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from spectrum_core.forecaster import FastChebyshevForecaster
from modules import scripts
import math
import torch
import modules.shared as shared

class SpectrumScript(scripts.Script):
    def title(self):
        return "Spectrum Accelerator"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        import gradio as gr
        with gr.Accordion("Spectrum Accelerator", open=False, elem_id="spectrum_accordion"):
            enabled = gr.Checkbox(label="Enable Spectrum", value=False)
            with gr.Row():
                w = gr.Slider(label="w (Blend Weight)", minimum=0.0, maximum=1.0, step=0.05, value=0.40)
                m = gr.Slider(label="m (Chebyshev Complexity)", minimum=1, maximum=8, step=1, value=3)
                lam = gr.Slider(label="lam (Ridge Regularization)", minimum=0.0, maximum=2.0, step=0.05, value=1.0)
            with gr.Row():
                window_size = gr.Slider(label="Window Size", minimum=1, maximum=10, step=1, value=2)
                flex_window = gr.Slider(label="Flex Window", minimum=0.0, maximum=2.0, step=0.05, value=0.20)
                warmup_steps = gr.Slider(label="Warmup Steps", minimum=0, maximum=20, step=1, value=1)
            with gr.Row():
                stop_caching_offset = gr.Slider(label="Stop Caching Offset (from end)", minimum=0, maximum=100, step=1, value=1)
        
        return [enabled, w, m, lam, window_size, flex_window, warmup_steps, stop_caching_offset]

    def process(self, p, *args):
        # reForge/A1111 の仕様により gr.Accordion の状態が args[0] に挿入されることがある
        # UIコンポーネント数(8個)より多い場合は先頭を読み飛ばす
        if len(args) > 8:
            args = args[1:]
            
        # UI側から無効化されたかどうかのチェック
        enabled = args[0] if args else False
        
        # ADetailer や Hires fix の二次パス等、本体以外の生成プロセスを検知
        # str(type(p)) による判定に加え、属性チェックを併用
        p_type_name = str(type(p))
        is_secondary = (
            getattr(p, "_in_adetailer", False) or 
            "Postprocessed" in p_type_name or 
            getattr(p, "is_hr_pass", False) # Hiresパスの明示的チェック
        )
        
        if is_secondary:
            self.remove_patch_force()
            return

        # 以前の状態を完全に破棄
        if hasattr(p, "_spectrum_state"):
            del p._spectrum_state
        p._spectrum_state = None
        
        if enabled:
            # ログ出力を控えめにし、stdoutへの過剰な干渉を避ける
            # (reForge の時間計測が stdout の進捗バーをパースしている可能性があるため)
            sys.stdout.write("[Spectrum] Enabled for main sampling.\n")
            sys.stdout.flush()
        else:
            self.remove_patch_force()

    def process_before_every_sampling(self, p, *args, **kwargs):
        """サンプリング開始の直前に呼ばれる"""
        if len(args) > 8:
            args = args[1:]
        
        if not args or not args[0]: # Not enabled
            return
            
        # 二次プロセスのガード (ADetailer 等)
        p_type_name = str(type(p))
        if getattr(p, "_in_adetailer", False) or "Postprocessed" in p_type_name:
            return

        enabled, w, m, lam, window_size, flex_window, warmup_steps, stop_caching_offset = args
        
        # ターゲット UNet を取得
        import modules.shared as shared
        unet = getattr(getattr(shared.sd_model, "forge_objects", None), "unet", None)
        if not unet:
            return

        # 状態リセット・準備
        if getattr(p, "_spectrum_state", None) is None:
            p._spectrum_state = {
                "forecaster": None, "cnt": 0, "num_cached": 0, 
                "curr_ws": float(window_size), "last_t": None
            }
            
        state = p._spectrum_state
        w_f, m_i, lam_f = float(w), int(m), float(lam)
        total_steps = p.steps
        stop_caching_step = max(0, total_steps - stop_caching_offset)

        # パッチが当たっていることを確認し、スキップの準備
        def spectrum_unet_wrapper(model_function, kwargs_unet):
            x = kwargs_unet.get("input")
            timestep = kwargs_unet.get("timestep")
            c = kwargs_unet.get("c", {})
            if x is None or timestep is None:
                return model_function(**kwargs_unet)

            t_scalar = timestep[0].item() if isinstance(timestep, torch.Tensor) else float(timestep)
            
            # 世代リセット検知
            if state["last_t"] is None or t_scalar > state["last_t"] + 10:
                state.update({"cnt": 0, "num_cached": 0, "curr_ws": float(window_size), "forecaster": None})
            state["last_t"] = t_scalar
            
            cnt = state["cnt"]
            do_actual = True
            
            if cnt >= warmup_steps and cnt < stop_caching_step:
                do_actual = (state["num_cached"] + 1) % math.floor(state["curr_ws"]) == 0

            if do_actual:
                out = model_function(x, timestep, **c)
                if state["forecaster"] is None:
                    state["forecaster"] = FastChebyshevForecaster(m=m_i, lam=lam_f)
                state["forecaster"].update(cnt, out)
                if cnt >= warmup_steps: 
                    state["curr_ws"] += flex_window
                state["num_cached"] = 0
            else:
                out = state["forecaster"].predict(cnt, w=w_f).to(x.dtype)
                state["num_cached"] += 1

            state["cnt"] += 1
            
            return out

        # Forge由来のラップ関数を使う
        try:
            unet.set_model_unet_function_wrapper(spectrum_unet_wrapper)
        except Exception:
            unet.model_options["model_function_wrapper"] = spectrum_unet_wrapper

    def remove_patch_force(self):
        import modules.shared as shared
        # shared.sd_model だけでなく、現在のアクティブなモデルからも取得を試みる
        unet = getattr(getattr(shared.sd_model, "forge_objects", None), "unet", None)
        if not unet:
            return
            
        # 完全にキーを削除してサンプラーを元の状態に戻す
        if "model_function_wrapper" in unet.model_options:
            wrap = unet.model_options["model_function_wrapper"]
            # 自分のラッパー、あるいは異常な None の場合に削除
            if wrap is None or (hasattr(wrap, "__name__") and wrap.__name__ == "spectrum_unet_wrapper"):
                del unet.model_options["model_function_wrapper"]
                print("[Spectrum] Extension DISABLED. UNet patch removed safely.")
        
        # Forgeの内部データ構造もクリア
        try:
            if hasattr(unet, "set_model_unet_function_wrapper"):
                # 内部辞書の書き換えを伴うため、Noneをセットせず直接辞書を触ったあとに状態のみリセット
                pass
        except Exception:
            pass

