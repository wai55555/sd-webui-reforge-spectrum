import torch

class FastChebyshevForecaster:
    def __init__(self, m: int = 4, lam: float = 1.0):
        self.M = m
        self.K = max(m + 1, 6) 
        self.lam = lam
        self.H_buf = []  
        self.T_buf = []
        self.shape = None
        self.dtype = None
        self.coef = None

    def _taus(self, t: float) -> float:
        return (t / 50.0) * 2.0 - 1.0

    def _build_design(self, taus: torch.Tensor, dtype: torch.dtype) -> torch.Tensor:
        taus = taus.reshape(-1, 1).to(dtype)
        T = [torch.ones((taus.shape[0], 1), device=taus.device, dtype=dtype)]
        if self.M > 0:
            T.append(taus)
            for _ in range(2, self.M + 1):
                T.append(2 * taus * T[-1] - T[-2])
        return torch.cat(T[:self.M + 1], dim=1)

    def update(self, cnt: int, h: torch.Tensor):
        if self.shape is not None and h.shape != self.shape:
            self.H_buf.clear()
            self.T_buf.clear()
        
        self.shape = h.shape
        self.dtype = h.dtype
        
        # 保存時は float32 に統一し、Cholesky 分解などの計算精度を担保する
        self.H_buf.append(h.view(-1).to(torch.float32))
        self.T_buf.append(self._taus(cnt))

        if len(self.H_buf) > self.K:
            self.H_buf.pop(0)
            self.T_buf.pop(0)

        self._solve_coefficients()

    def _solve_coefficients(self):
        device = self.H_buf[-1].device
        
        try:
            H = torch.stack(self.H_buf, dim=0)
            T_tensor = torch.tensor(self.T_buf, dtype=torch.float32, device=device)
            X = self._build_design(T_tensor, torch.float32)
            
            # ridge回帰の正則化項
            lamI = self.lam * torch.eye(self.M + 1, device=device, dtype=torch.float32)
            XtX = X.T @ X + lamI
            
            L = torch.linalg.cholesky(XtX)
            XtH = X.T @ H
            self.coef = torch.cholesky_solve(XtH, L)
        except Exception:
            # 万が一Cholesky分解に失敗した場合は回帰予測を諦めてフォールバックする
            self.coef = None

    def predict(self, cnt: int, w: float) -> torch.Tensor:
        if self.coef is None:
            return self.H_buf[-1].to(self.dtype).view(self.shape)

        device = self.coef.device
        tau_star = torch.tensor([self._taus(cnt)], device=device, dtype=torch.float32)
        x_star = self._build_design(tau_star, torch.float32) 
        
        pred_cheb = (x_star @ self.coef).squeeze(0)

        if len(self.H_buf) >= 2:
            h_i = self.H_buf[-1]
            h_im1 = self.H_buf[-2]
            h_taylor = h_i + 0.5 * (h_i - h_im1) 
        else:
            h_taylor = self.H_buf[-1]

        res = (1 - w) * h_taylor + w * pred_cheb
        
        # 極端に大きな値が生成された安全用クランプ (通常は引っかからない)
        clamp_val = 30.0
        out = torch.clamp(res, -clamp_val, clamp_val).to(self.dtype).view(self.shape)
            
        return out
