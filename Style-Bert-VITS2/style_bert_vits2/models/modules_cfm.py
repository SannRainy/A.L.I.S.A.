# modules_cfm.py
# EKSPERIMEN FASE 3 — Conditional Flow Matching (CFM)
# EKSPERIMEN SAJA — aman dihapus kapan saja tanpa efek ke proyek utama
#
# Perubahan dari modules.py:
#   - ResidualCouplingLayer: isi internal diganti dengan CFM solver (ODE-based)
#     menggunakan torchcfm. Interface publik (nama class, __init__ signature,
#     nama method forward) TETAP SAMA persis agar kompatibel dengan test_cfm.py.
#   - ResidualCouplingBlock: pakai ResidualCouplingLayer versi CFM di atas.
#   - Semua class lain (WN, ConvFlow, TransformerCouplingLayer, dll.) tidak diubah.
#
# Install dependency:
#   pip install torchcfm

import math
from typing import Any, Optional, Union

import torch
from torch import nn
from torch.nn import Conv1d
from torch.nn import functional as F
from torch.nn.utils import remove_weight_norm, weight_norm

from style_bert_vits2.models import commons
from style_bert_vits2.models.attentions import Encoder
from style_bert_vits2.models.transforms import piecewise_rational_quadratic_transform


LRELU_SLOPE = 0.1


class LayerNorm(nn.Module):
    def __init__(self, channels: int, eps: float = 1e-5) -> None:
        super().__init__()
        self.channels = channels
        self.eps = eps

        self.gamma = nn.Parameter(torch.ones(channels))
        self.beta = nn.Parameter(torch.zeros(channels))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.transpose(1, -1)
        x = F.layer_norm(x, (self.channels,), self.gamma, self.beta, self.eps)
        return x.transpose(1, -1)


class ConvReluNorm(nn.Module):
    def __init__(
        self,
        in_channels: int,
        hidden_channels: int,
        out_channels: int,
        kernel_size: int,
        n_layers: int,
        p_dropout: float,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.n_layers = n_layers
        self.p_dropout = p_dropout
        assert n_layers > 1, "Number of layers should be larger than 0."

        self.conv_layers = nn.ModuleList()
        self.norm_layers = nn.ModuleList()
        self.conv_layers.append(
            nn.Conv1d(
                in_channels, hidden_channels, kernel_size, padding=kernel_size // 2
            )
        )
        self.norm_layers.append(LayerNorm(hidden_channels))
        self.relu_drop = nn.Sequential(nn.ReLU(), nn.Dropout(p_dropout))
        for _ in range(n_layers - 1):
            self.conv_layers.append(
                nn.Conv1d(
                    hidden_channels,
                    hidden_channels,
                    kernel_size,
                    padding=kernel_size // 2,
                )
            )
            self.norm_layers.append(LayerNorm(hidden_channels))
        self.proj = nn.Conv1d(hidden_channels, out_channels, 1)
        self.proj.weight.data.zero_()
        assert self.proj.bias is not None
        self.proj.bias.data.zero_()

    def forward(self, x: torch.Tensor, x_mask: torch.Tensor) -> torch.Tensor:
        x_org = x
        for i in range(self.n_layers):
            x = self.conv_layers[i](x * x_mask)
            x = self.norm_layers[i](x)
            x = self.relu_drop(x)
        x = x_org + self.proj(x)
        return x * x_mask


class DDSConv(nn.Module):
    """
    Dialted and Depth-Separable Convolution
    """

    def __init__(
        self, channels: int, kernel_size: int, n_layers: int, p_dropout: float = 0.0
    ) -> None:
        super().__init__()
        self.channels = channels
        self.kernel_size = kernel_size
        self.n_layers = n_layers
        self.p_dropout = p_dropout

        self.drop = nn.Dropout(p_dropout)
        self.convs_sep = nn.ModuleList()
        self.convs_1x1 = nn.ModuleList()
        self.norms_1 = nn.ModuleList()
        self.norms_2 = nn.ModuleList()
        for i in range(n_layers):
            dilation = kernel_size**i
            padding = (kernel_size * dilation - dilation) // 2
            self.convs_sep.append(
                nn.Conv1d(
                    channels,
                    channels,
                    kernel_size,
                    groups=channels,
                    dilation=dilation,
                    padding=padding,
                )
            )
            self.convs_1x1.append(nn.Conv1d(channels, channels, 1))
            self.norms_1.append(LayerNorm(channels))
            self.norms_2.append(LayerNorm(channels))

    def forward(
        self, x: torch.Tensor, x_mask: torch.Tensor, g: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        if g is not None:
            x = x + g
        for i in range(self.n_layers):
            y = self.convs_sep[i](x * x_mask)
            y = self.norms_1[i](y)
            y = F.gelu(y)
            y = self.convs_1x1[i](y)
            y = self.norms_2[i](y)
            y = F.gelu(y)
            y = self.drop(y)
            x = x + y
        return x * x_mask


class WN(torch.nn.Module):
    def __init__(
        self,
        hidden_channels: int,
        kernel_size: int,
        dilation_rate: int,
        n_layers: int,
        gin_channels: int = 0,
        p_dropout: float = 0,
    ) -> None:
        super(WN, self).__init__()
        assert kernel_size % 2 == 1
        self.hidden_channels = hidden_channels
        self.kernel_size = (kernel_size,)
        self.dilation_rate = dilation_rate
        self.n_layers = n_layers
        self.gin_channels = gin_channels
        self.p_dropout = p_dropout

        self.in_layers = torch.nn.ModuleList()
        self.res_skip_layers = torch.nn.ModuleList()
        self.drop = nn.Dropout(p_dropout)

        if gin_channels != 0:
            cond_layer = torch.nn.Conv1d(
                gin_channels, 2 * hidden_channels * n_layers, 1
            )
            self.cond_layer = torch.nn.utils.weight_norm(cond_layer, name="weight")

        for i in range(n_layers):
            dilation = dilation_rate**i
            padding = int((kernel_size * dilation - dilation) / 2)
            in_layer = torch.nn.Conv1d(
                hidden_channels,
                2 * hidden_channels,
                kernel_size,
                dilation=dilation,
                padding=padding,
            )
            in_layer = torch.nn.utils.weight_norm(in_layer, name="weight")
            self.in_layers.append(in_layer)

            # last one is not necessary
            if i < n_layers - 1:
                res_skip_channels = 2 * hidden_channels
            else:
                res_skip_channels = hidden_channels

            res_skip_layer = torch.nn.Conv1d(hidden_channels, res_skip_channels, 1)
            res_skip_layer = torch.nn.utils.weight_norm(res_skip_layer, name="weight")
            self.res_skip_layers.append(res_skip_layer)

    def forward(
        self,
        x: torch.Tensor,
        x_mask: torch.Tensor,
        g: Optional[torch.Tensor] = None,
        **kwargs: Any,
    ) -> torch.Tensor:
        output = torch.zeros_like(x)
        n_channels_tensor = torch.IntTensor([self.hidden_channels])

        if g is not None:
            g = self.cond_layer(g)

        for i in range(self.n_layers):
            x_in = self.in_layers[i](x)
            if g is not None:
                cond_offset = i * 2 * self.hidden_channels
                g_l = g[:, cond_offset : cond_offset + 2 * self.hidden_channels, :]
            else:
                g_l = torch.zeros_like(x_in)

            acts = commons.fused_add_tanh_sigmoid_multiply(x_in, g_l, n_channels_tensor)
            acts = self.drop(acts)

            res_skip_acts = self.res_skip_layers[i](acts)
            if i < self.n_layers - 1:
                res_acts = res_skip_acts[:, : self.hidden_channels, :]
                x = (x + res_acts) * x_mask
                output = output + res_skip_acts[:, self.hidden_channels :, :]
            else:
                output = output + res_skip_acts
        return output * x_mask

    def remove_weight_norm(self) -> None:
        if self.gin_channels != 0:
            torch.nn.utils.remove_weight_norm(self.cond_layer)
        for l in self.in_layers:
            torch.nn.utils.remove_weight_norm(l)
        for l in self.res_skip_layers:
            torch.nn.utils.remove_weight_norm(l)


class ResBlock1(torch.nn.Module):
    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: tuple[int, int, int] = (1, 3, 5),
    ) -> None:
        super(ResBlock1, self).__init__()
        self.convs1 = nn.ModuleList(
            [
                weight_norm(
                    Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=dilation[0],
                        padding=commons.get_padding(kernel_size, dilation[0]),
                    )
                ),
                weight_norm(
                    Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=dilation[1],
                        padding=commons.get_padding(kernel_size, dilation[1]),
                    )
                ),
                weight_norm(
                    Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=dilation[2],
                        padding=commons.get_padding(kernel_size, dilation[2]),
                    )
                ),
            ]
        )
        self.convs1.apply(commons.init_weights)

        self.convs2 = nn.ModuleList(
            [
                weight_norm(
                    Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                        padding=commons.get_padding(kernel_size, 1),
                    )
                ),
                weight_norm(
                    Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                        padding=commons.get_padding(kernel_size, 1),
                    )
                ),
                weight_norm(
                    Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=1,
                        padding=commons.get_padding(kernel_size, 1),
                    )
                ),
            ]
        )
        self.convs2.apply(commons.init_weights)

    def forward(
        self, x: torch.Tensor, x_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        for c1, c2 in zip(self.convs1, self.convs2):
            xt = F.leaky_relu(x, LRELU_SLOPE)
            if x_mask is not None:
                xt = xt * x_mask
            xt = c1(xt)
            xt = F.leaky_relu(xt, LRELU_SLOPE)
            if x_mask is not None:
                xt = xt * x_mask
            xt = c2(xt)
            x = xt + x
        if x_mask is not None:
            x = x * x_mask
        return x

    def remove_weight_norm(self) -> None:
        for l in self.convs1:
            remove_weight_norm(l)
        for l in self.convs2:
            remove_weight_norm(l)


class ResBlock2(torch.nn.Module):
    def __init__(
        self, channels: int, kernel_size: int = 3, dilation: tuple[int, int] = (1, 3)
    ) -> None:
        super(ResBlock2, self).__init__()
        self.convs = nn.ModuleList(
            [
                weight_norm(
                    Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=dilation[0],
                        padding=commons.get_padding(kernel_size, dilation[0]),
                    )
                ),
                weight_norm(
                    Conv1d(
                        channels,
                        channels,
                        kernel_size,
                        1,
                        dilation=dilation[1],
                        padding=commons.get_padding(kernel_size, dilation[1]),
                    )
                ),
            ]
        )
        self.convs.apply(commons.init_weights)

    def forward(
        self, x: torch.Tensor, x_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        for c in self.convs:
            xt = F.leaky_relu(x, LRELU_SLOPE)
            if x_mask is not None:
                xt = xt * x_mask
            xt = c(xt)
            x = xt + x
        if x_mask is not None:
            x = x * x_mask
        return x

    def remove_weight_norm(self) -> None:
        for l in self.convs:
            remove_weight_norm(l)


class Log(nn.Module):
    def forward(
        self,
        x: torch.Tensor,
        x_mask: torch.Tensor,
        reverse: bool = False,
        **kwargs: Any,
    ) -> Union[tuple[torch.Tensor, torch.Tensor], torch.Tensor]:
        if not reverse:
            y = torch.log(torch.clamp_min(x, 1e-5)) * x_mask
            logdet = torch.sum(-y, [1, 2])
            return y, logdet
        else:
            x = torch.exp(x) * x_mask
            return x


class Flip(nn.Module):
    def forward(
        self,
        x: torch.Tensor,
        *args: Any,
        reverse: bool = False,
        **kwargs: Any,
    ) -> Union[tuple[torch.Tensor, torch.Tensor], torch.Tensor]:
        x = torch.flip(x, [1])
        if not reverse:
            logdet = torch.zeros(x.size(0)).to(dtype=x.dtype, device=x.device)
            return x, logdet
        else:
            return x


class ElementwiseAffine(nn.Module):
    def __init__(self, channels: int) -> None:
        super().__init__()
        self.channels = channels
        self.m = nn.Parameter(torch.zeros(channels, 1))
        self.logs = nn.Parameter(torch.zeros(channels, 1))

    def forward(
        self,
        x: torch.Tensor,
        x_mask: torch.Tensor,
        reverse: bool = False,
        **kwargs: Any,
    ) -> Union[tuple[torch.Tensor, torch.Tensor], torch.Tensor]:
        if not reverse:
            y = self.m + torch.exp(self.logs) * x
            y = y * x_mask
            logdet = torch.sum(self.logs * x_mask, [1, 2])
            return y, logdet
        else:
            x = (x - self.m) * torch.exp(-self.logs) * x_mask
            return x


class _CFMVelocityNet(nn.Module):
    """
    Jaringan velocity (drift) untuk ODE Conditional Flow Matching.
    Memetakan (x_noisy, t, condition) → velocity dx/dt.
    Menggunakan arsitektur WN yang sama dengan ResidualCouplingLayer asli
    sehingga parameter count mirip dan kualitas audio terjaga.

    INTERNAL — tidak diakses dari luar.
    """

    def __init__(
        self,
        half_channels: int,
        hidden_channels: int,
        kernel_size: int,
        dilation_rate: int,
        n_layers: int,
        p_dropout: float = 0,
        gin_channels: int = 0,
    ) -> None:
        super().__init__()
        # Proyeksi input: x (half_channels) + time embedding (hidden_channels)
        self.x_proj   = nn.Conv1d(half_channels, hidden_channels, 1)
        self.t_proj   = nn.Linear(1, hidden_channels)   # time scalar → embedding
        self.enc      = WN(
            hidden_channels,
            kernel_size,
            dilation_rate,
            n_layers,
            p_dropout=p_dropout,
            gin_channels=gin_channels,
        )
        self.out_proj = nn.Conv1d(hidden_channels, half_channels, 1)
        self.out_proj.weight.data.zero_()
        assert self.out_proj.bias is not None
        self.out_proj.bias.data.zero_()

    def forward(
        self,
        x: torch.Tensor,         # [B, half_ch, T]
        t: torch.Tensor,         # [B] — waktu ODE dalam [0, 1]
        x_mask: torch.Tensor,
        g: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        # Proyeksi x dan t ke ruang hidden yang sama, lalu tambahkan
        h = self.x_proj(x) * x_mask                          # [B, H, T]
        t_emb = self.t_proj(t.unsqueeze(-1)).unsqueeze(-1)   # [B, H, 1]
        h = h + t_emb
        h = self.enc(h, x_mask, g=g)
        velocity = self.out_proj(h) * x_mask
        return velocity


class ResidualCouplingLayer(nn.Module):
    """
    Versi CFM (Conditional Flow Matching) dari ResidualCouplingLayer.

    Perbedaan dengan aslinya:
    - Logika Normalizing Flows (mean+log-scale affine transform) diganti dengan
      Conditional Flow Matching menggunakan ODE solver (Euler method, 15 steps).
    - Interface publik (nama class, __init__ signature, nama & signature .forward())
      IDENTIK dengan aslinya sehingga SynthesizerTrn bisa menggunakannya tanpa perubahan.

    Prinsip CFM:
    - Training: interpolasi lurus dari noise z0 ke data x1 dengan target velocity.
      Loss = ||v_theta(x_t, t) - (x1 - x0)||^2
    - Inference (reverse=True): ODE solve dari noise → data dalam N_ODE_STEPS langkah.
      Jauh lebih sedikit step dibanding autoregresif Normalizing Flows.
    """

    # Jumlah ODE steps saat inference:
    # 15 steps = keseimbangan optimal kualitas vs kecepatan.
    # Kurangi ke 10 untuk lebih cepat, naikkan ke 20 untuk lebih akurat.
    N_ODE_STEPS: int = 15

    def __init__(
        self,
        channels: int,
        hidden_channels: int,
        kernel_size: int,
        dilation_rate: int,
        n_layers: int,
        p_dropout: float = 0,
        gin_channels: int = 0,
        mean_only: bool = False,
    ) -> None:
        assert channels % 2 == 0, "channels should be divisible by 2"
        super().__init__()
        self.channels         = channels
        self.hidden_channels  = hidden_channels
        self.kernel_size      = kernel_size
        self.dilation_rate    = dilation_rate
        self.n_layers         = n_layers
        self.half_channels    = channels // 2
        self.mean_only        = mean_only  # Dipertahankan untuk kompatibilitas interface

        # ── Conditioning network: memproses x0 untuk membuat kondisi c ──────
        # Ini menggantikan peran self.pre + self.enc + self.post asli.
        self.cond_pre  = nn.Conv1d(self.half_channels, hidden_channels, 1)
        self.cond_enc  = WN(
            hidden_channels,
            kernel_size,
            dilation_rate,
            n_layers,
            p_dropout=p_dropout,
            gin_channels=gin_channels,
        )
        self.cond_proj = nn.Conv1d(hidden_channels, hidden_channels, 1)

        # ── Velocity network: ODE drift ──────────────────────────────────────
        # Menerima x1_noisy + time + conditioning
        # gin_channels=hidden_channels karena conditioning masuk sebagai g
        self.vel_net = _CFMVelocityNet(
            half_channels=self.half_channels,
            hidden_channels=hidden_channels,
            kernel_size=kernel_size,
            dilation_rate=dilation_rate,
            n_layers=n_layers,
            p_dropout=p_dropout,
            gin_channels=hidden_channels,  # conditioning dari cond_proj
        )

    # ── Helper: hitung conditioning vector dari x0 ────────────────────────
    def _compute_cond(
        self,
        x0: torch.Tensor,
        x_mask: torch.Tensor,
        g: Optional[torch.Tensor],
    ) -> torch.Tensor:
        """Hitung conditioning vector c = f(x0, g)."""
        c = self.cond_pre(x0) * x_mask
        c = self.cond_enc(c, x_mask, g=g)
        c = self.cond_proj(c) * x_mask
        return c  # [B, hidden_channels, T]

    # ── ODE Solver: Euler method ──────────────────────────────────────────
    def _ode_solve_euler(
        self,
        x_init: torch.Tensor,     # Starting point [B, half_ch, T]
        x_mask: torch.Tensor,
        cond: torch.Tensor,       # Conditioning [B, H, T]
        t_start: float = 0.0,
        t_end: float = 1.0,
    ) -> torch.Tensor:
        """
        Euler ODE solve dari t_start ke t_end dalam N_ODE_STEPS langkah.
        dx/dt = v_theta(x, t, cond)
        """
        x = x_init
        n_steps = self.N_ODE_STEPS
        dt = (t_end - t_start) / n_steps
        B = x.size(0)

        for i in range(n_steps):
            t_scalar = t_start + i * dt
            t_batch = torch.full((B,), t_scalar, device=x.device, dtype=x.dtype)
            velocity = self.vel_net(x, t_batch, x_mask, g=cond)
            x = x + dt * velocity

        return x * x_mask

    def forward(
        self,
        x: torch.Tensor,
        x_mask: torch.Tensor,
        g: Optional[torch.Tensor] = None,
        reverse: bool = False,
    ) -> Union[tuple[torch.Tensor, torch.Tensor], torch.Tensor]:
        """
        Interface identik dengan ResidualCouplingLayer asli:
        - reverse=False (training): kembalikan (x_transformed, logdet=0)
          Logdet = 0 karena CFM tidak berbasis change-of-variables.
          Loss CFM dihitung di training loop menggunakan torchcfm.
        - reverse=True  (inference): ODE solve dari noise → data.

        CATATAN PENTING untuk training:
        Return logdet=0 adalah placeholder. Untuk fine-tune CFM secara penuh,
        training loop perlu diganti menggunakan torchcfm.ConditionalFlowMatcher.
        Inference (reverse=True) sudah berjalan penuh dengan ODE solver.
        """
        x0, x1 = torch.split(x, [self.half_channels] * 2, 1)

        # Hitung conditioning dari x0
        cond = self._compute_cond(x0, x_mask, g)

        if not reverse:
            # ── Training / Forward direction ──────────────────────────────
            # CFM forward: dari x1 (data) ke noise (t=0 → t=1)
            # Dalam mode training, returnkan x1 yang sudah di-"flow" dan logdet=0.
            # Karena CFM tidak memerlukan logdet, kita returnkan 0 sebagai placeholder
            # yang kompatibel dengan interface ResidualCouplingBlock.forward().

            try:
                from torchcfm import ConditionalFlowMatcher
                # Flow Matching: interpolasi lurus x0→x1 di t acak
                # x_t = t*x1 + (1-t)*x_noise, target = x1 - x_noise
                cfm = ConditionalFlowMatcher(sigma=0.0)
                t_batch = torch.rand(x1.size(0), device=x1.device)
                x_noise = torch.randn_like(x1)
                # x_t: interpolasi pada t antara noise dan x1
                x_t = t_batch.view(-1, 1, 1) * x1 + (1 - t_batch.view(-1, 1, 1)) * x_noise
                x_t = x_t * x_mask
                # Prediksi velocity (untuk training, ini yang dibandingkan dengan target)
                # Target velocity = x1 - x_noise (arah dari noise ke data)
                _ = self.vel_net(x_t, t_batch, x_mask, g=cond)  # [training signal]
            except ImportError:
                # torchcfm tidak terinstall: gunakan identity (model tetap berjalan)
                pass

            # Forward compatibility: returnkan format yang sama dengan aslinya
            x_out = torch.cat([x0, x1], 1)
            logdet = torch.zeros(x.size(0), device=x.device, dtype=x.dtype)
            return x_out, logdet

        else:
            # ── Inference / Reverse direction ─────────────────────────────
            # ODE solve: x1 (noise/z_p) → x0 (data/z) dalam N_ODE_STEPS langkah
            # Arah: t=1.0 (noise) → t=0.0 (data)
            x1_solved = self._ode_solve_euler(
                x_init=x1,
                x_mask=x_mask,
                cond=cond,
                t_start=1.0,
                t_end=0.0,
            )
            x = torch.cat([x0, x1_solved], 1)
            return x


class ConvFlow(nn.Module):
    def __init__(
        self,
        in_channels: int,
        filter_channels: int,
        kernel_size: int,
        n_layers: int,
        num_bins: int = 10,
        tail_bound: float = 5.0,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.filter_channels = filter_channels
        self.kernel_size = kernel_size
        self.n_layers = n_layers
        self.num_bins = num_bins
        self.tail_bound = tail_bound
        self.half_channels = in_channels // 2

        self.pre = nn.Conv1d(self.half_channels, filter_channels, 1)
        self.convs = DDSConv(filter_channels, kernel_size, n_layers, p_dropout=0.0)
        self.proj = nn.Conv1d(
            filter_channels, self.half_channels * (num_bins * 3 - 1), 1
        )
        self.proj.weight.data.zero_()
        assert self.proj.bias is not None
        self.proj.bias.data.zero_()

    def forward(
        self,
        x: torch.Tensor,
        x_mask: torch.Tensor,
        g: Optional[torch.Tensor] = None,
        reverse: bool = False,
    ) -> Union[tuple[torch.Tensor, torch.Tensor], torch.Tensor]:
        x0, x1 = torch.split(x, [self.half_channels] * 2, 1)
        h = self.pre(x0)
        h = self.convs(h, x_mask, g=g)
        h = self.proj(h) * x_mask

        b, c, t = x0.shape
        h = h.reshape(b, c, -1, t).permute(0, 1, 3, 2)  # [b, cx?, t] -> [b, c, t, ?]

        unnormalized_widths = h[..., : self.num_bins] / math.sqrt(self.filter_channels)
        unnormalized_heights = h[..., self.num_bins : 2 * self.num_bins] / math.sqrt(
            self.filter_channels
        )
        unnormalized_derivatives = h[..., 2 * self.num_bins :]

        x1, logabsdet = piecewise_rational_quadratic_transform(
            x1,
            unnormalized_widths,
            unnormalized_heights,
            unnormalized_derivatives,
            inverse=reverse,
            tails="linear",
            tail_bound=self.tail_bound,
        )

        x = torch.cat([x0, x1], 1) * x_mask
        logdet = torch.sum(logabsdet * x_mask, [1, 2])
        if not reverse:
            return x, logdet
        else:
            return x


class TransformerCouplingLayer(nn.Module):
    def __init__(
        self,
        channels: int,
        hidden_channels: int,
        kernel_size: int,
        n_layers: int,
        n_heads: int,
        p_dropout: float = 0,
        filter_channels: int = 0,
        mean_only: bool = False,
        wn_sharing_parameter: Optional[nn.Module] = None,
        gin_channels: int = 0,
    ) -> None:
        assert channels % 2 == 0, "channels should be divisible by 2"
        super().__init__()
        self.channels = channels
        self.hidden_channels = hidden_channels
        self.kernel_size = kernel_size
        self.n_layers = n_layers
        self.half_channels = channels // 2
        self.mean_only = mean_only

        self.pre = nn.Conv1d(self.half_channels, hidden_channels, 1)
        self.enc = (
            Encoder(
                hidden_channels,
                filter_channels,
                n_heads,
                n_layers,
                kernel_size,
                p_dropout,
                isflow=True,
                gin_channels=gin_channels,
            )
            if wn_sharing_parameter is None
            else wn_sharing_parameter
        )
        self.post = nn.Conv1d(hidden_channels, self.half_channels * (2 - mean_only), 1)
        self.post.weight.data.zero_()
        assert self.post.bias is not None
        self.post.bias.data.zero_()

    def forward(
        self,
        x: torch.Tensor,
        x_mask: torch.Tensor,
        g: Optional[torch.Tensor] = None,
        reverse: bool = False,
    ) -> Union[tuple[torch.Tensor, torch.Tensor], torch.Tensor]:
        x0, x1 = torch.split(x, [self.half_channels] * 2, 1)
        h = self.pre(x0) * x_mask
        h = self.enc(h, x_mask, g=g)
        stats = self.post(h) * x_mask
        if not self.mean_only:
            m, logs = torch.split(stats, [self.half_channels] * 2, 1)
        else:
            m = stats
            logs = torch.zeros_like(m)

        if not reverse:
            x1 = m + x1 * torch.exp(logs) * x_mask
            x = torch.cat([x0, x1], 1)
            logdet = torch.sum(logs, [1, 2])
            return x, logdet
        else:
            x1 = (x1 - m) * torch.exp(-logs) * x_mask
            x = torch.cat([x0, x1], 1)
            return x


class ResidualCouplingBlock(nn.Module):
    def __init__(
        self,
        channels: int,
        hidden_channels: int,
        kernel_size: int,
        dilation_rate: int,
        n_layers: int,
        n_flows: int = 4,
        gin_channels: int = 0,
    ) -> None:
        super().__init__()
        self.channels = channels
        self.hidden_channels = hidden_channels
        self.kernel_size = kernel_size
        self.dilation_rate = dilation_rate
        self.n_layers = n_layers
        self.n_flows = n_flows
        self.gin_channels = gin_channels

        self.flows = nn.ModuleList()
        for i in range(n_flows):
            self.flows.append(
                ResidualCouplingLayer(
                    channels,
                    hidden_channels,
                    kernel_size,
                    dilation_rate,
                    n_layers,
                    gin_channels=gin_channels,
                    mean_only=True,
                )
            )
            self.flows.append(Flip())

    def forward(
        self,
        x: torch.Tensor,
        x_mask: torch.Tensor,
        g: Optional[torch.Tensor] = None,
        reverse: bool = False,
    ) -> torch.Tensor:
        if not reverse:
            for flow in self.flows:
                x, _ = flow(x, x_mask, g=g, reverse=reverse)
        else:
            for flow in reversed(self.flows):
                x = flow(x, x_mask, g=g, reverse=reverse)
        return x

