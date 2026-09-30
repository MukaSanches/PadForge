from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox

from . import __version__
from .engine import PadForgeEngine
from .input_backend import PygameInputBackend
from .models import LOGICAL_BUTTONS, AxisCalibration
from .output_backend import X360Output, NullOutput
from .profile_manager import ProfileManager
from .settings import load_mapping, save_mapping, load_calibrations, save_calibrations


class PadForgeApp(tk.Tk):
    BG = "#0f1117"
    PANEL = "#171b24"
    TEXT = "#eef2f7"
    MUTED = "#94a3b8"

    def __init__(self):
        super().__init__()
        self.title(f"PadForge {__version__}")
        self.geometry("980x690")
        self.minsize(820, 600)
        self.configure(bg=self.BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.mapping = load_mapping()
        self.calibrations = load_calibrations()
        self.profiles = ProfileManager()
        self.input = None
        self.engine = None
        self.output = X360Output()
        self.devices_cache = []

        self._style()
        self._ui()
        self.after(250, self.refresh_devices)
        self.after(33, self.refresh_live)

    def _style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TFrame", background=self.BG)
        s.configure("Panel.TFrame", background=self.PANEL)
        s.configure("TLabel", background=self.BG, foreground=self.TEXT, font=("Segoe UI", 10))
        s.configure("Muted.TLabel", foreground=self.MUTED)
        s.configure("Title.TLabel", foreground=self.TEXT, font=("Segoe UI Semibold", 20))
        s.configure("Section.TLabel", background=self.PANEL, foreground=self.TEXT, font=("Segoe UI Semibold", 12))
        s.configure("TButton", padding=8, font=("Segoe UI Semibold", 9))
        s.configure("TNotebook.Tab", padding=(14, 8))

    def panel(self, parent):
        return ttk.Frame(parent, style="Panel.TFrame", padding=16)

    def _ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=(18, 8))
        ttk.Label(header, text="PadForge", style="Title.TLabel").pack(side="left")
        self.status = tk.StringVar(value="Aguardando controle")
        ttk.Label(header, textvariable=self.status, style="Muted.TLabel").pack(side="right")

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=18, pady=(6, 18))
        self.dashboard = ttk.Frame(tabs)
        self.mapping_tab = ttk.Frame(tabs)
        self.profiles_tab = ttk.Frame(tabs)
        self.diagnostics = ttk.Frame(tabs)
        tabs.add(self.dashboard, text="Dashboard")
        tabs.add(self.mapping_tab, text="Mapeamento")
        tabs.add(self.profiles_tab, text="Perfis")
        tabs.add(self.diagnostics, text="Diagnóstico")
        self._dashboard_ui()
        self._mapping_ui()
        self._profiles_ui()
        self._diagnostics_ui()

    def _dashboard_ui(self):
        box = self.panel(self.dashboard)
        box.pack(fill="x", padx=8, pady=8)
        ttk.Label(box, text="Controle", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.device_combo = ttk.Combobox(box, state="readonly", width=58)
        self.device_combo.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(box, text="Atualizar", command=self.refresh_devices).grid(row=1, column=1, padx=8)
        ttk.Button(box, text="Conectar", command=self.connect_device).grid(row=1, column=2)
        box.columnconfigure(0, weight=1)

        box = self.panel(self.dashboard)
        box.pack(fill="x", padx=8, pady=8)
        ttk.Label(box, text="Saída", style="Section.TLabel").pack(anchor="w")
        virtual = "Xbox 360 virtual pronto" if self.output.available else "Monitor apenas: XInput virtual indisponível"
        ttk.Label(box, text=virtual, style="Muted.TLabel").pack(anchor="w", pady=(8, 0))

        box = self.panel(self.dashboard)
        box.pack(fill="x", padx=8, pady=8)
        ttk.Label(box, text="Perfil ativo", style="Section.TLabel").pack(anchor="w")
        names = self.profiles.names()
        self.profile_name = tk.StringVar(value=names[0] if names else "Default")
        combo = ttk.Combobox(box, textvariable=self.profile_name, values=names, state="readonly", width=40)
        combo.pack(anchor="w", pady=(8, 0))
        combo.bind("<<ComboboxSelected>>", self.change_profile)
        self.auto_profile = tk.BooleanVar(value=True)
        ttk.Checkbutton(box, text="Trocar automaticamente pelo jogo em primeiro plano", variable=self.auto_profile,
                        command=self.toggle_auto).pack(anchor="w", pady=(8, 0))

        box = self.panel(self.dashboard)
        box.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(box, text="Entrada ao vivo", style="Section.TLabel").pack(anchor="w")
        self.live = tk.StringVar(value="Conecte um controle para começar.")
        ttk.Label(box, textvariable=self.live, style="Muted.TLabel", justify="left", wraplength=820).pack(anchor="w", pady=(10, 0))

    def _mapping_ui(self):
        box = self.panel(self.mapping_tab)
        box.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(box, text="Mapeamento físico → lógico", style="Section.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(box, text="Use os índices mostrados no Diagnóstico. SDL preenche automaticamente quando reconhece o controle.",
                  style="Muted.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(4, 12))
        self.button_vars = {}
        names = [x for x in LOGICAL_BUTTONS if not x.startswith("dpad_")] + ["lt", "rt"]
        for i, logical in enumerate(names):
            row, col = 2 + i // 2, (i % 2) * 2
            ttk.Label(box, text=logical.upper(), style="Section.TLabel").grid(row=row, column=col, sticky="w", pady=4)
            default = self.mapping.buttons.get(logical, self.mapping.triggers_as_buttons.get(logical, -1))
            var = tk.StringVar(value=str(default))
            ttk.Combobox(box, textvariable=var, values=[str(n) for n in range(32)], width=8).grid(row=row, column=col + 1, sticky="w")
            self.button_vars[logical] = var

        row = 2 + (len(names) + 1) // 2 + 1
        ttk.Label(box, text="Eixos", style="Section.TLabel").grid(row=row, column=0, columnspan=4, sticky="w", pady=(10, 4))
        self.axis_vars = {}
        for i, logical in enumerate(("lx", "ly", "rx", "ry")):
            r, c = row + 1 + i // 2, (i % 2) * 2
            ttk.Label(box, text=logical.upper(), style="Section.TLabel").grid(row=r, column=c, sticky="w", pady=4)
            var = tk.StringVar(value=str(self.mapping.axes.get(logical, i)))
            ttk.Combobox(box, textvariable=var, values=[str(n) for n in range(16)], width=8).grid(row=r, column=c + 1, sticky="w")
            self.axis_vars[logical] = var
        ttk.Button(box, text="Salvar mapeamento", command=self.save_mapping_ui).grid(row=row + 4, column=0, sticky="w", pady=(16, 0))

    def _profiles_ui(self):
        box = self.panel(self.profiles_tab)
        box.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(box, text="Retro Modernizer + perfis de jogo", style="Section.TLabel").pack(anchor="w")
        listing = tk.Listbox(box, bg="#10141c", fg=self.TEXT, selectbackground="#5f7cff", borderwidth=0,
                             highlightthickness=0, font=("Segoe UI", 10))
        listing.pack(fill="both", expand=True, pady=(10, 0))
        for profile in self.profiles.profiles:
            listing.insert("end", f"{profile.name} · {profile.category} · deadzone {int(profile.deadzone*100)}%")

    def _diagnostics_ui(self):
        box = self.panel(self.diagnostics)
        box.pack(fill="both", expand=True, padx=8, pady=8)
        ttk.Label(box, text="Diagnóstico + Analog Doctor", style="Section.TLabel").pack(anchor="w")
        bar = ttk.Frame(box, style="Panel.TFrame")
        bar.pack(fill="x", pady=(8, 10))
        ttk.Button(bar, text="Calibrar analógicos", command=self.start_calibration).pack(side="left")
        self.calibration_status = tk.StringVar(value="Pronto")
        ttk.Label(bar, textvariable=self.calibration_status, style="Muted.TLabel").pack(side="left", padx=10)
        self.raw = tk.Text(box, bg="#0b0e14", fg="#d8dee9", insertbackground="white", borderwidth=0,
                           font=("Consolas", 10))
        self.raw.pack(fill="both", expand=True)
        self._set_raw("Nenhum controle conectado.")

    def _set_raw(self, text):
        self.raw.configure(state="normal")
        self.raw.delete("1.0", "end")
        self.raw.insert("1.0", text)
        self.raw.configure(state="disabled")

    def refresh_devices(self):
        try:
            if self.input is None:
                self.input = PygameInputBackend(self.mapping, self.calibrations)
            self.devices_cache = self.input.devices()
            self.device_combo["values"] = [
                f"{d.index}: {d.name} | {d.axes} eixos | {d.buttons} botões | {'SDL' if d.sdl_mapped else 'raw'}"
                for d in self.devices_cache
            ]
            if self.devices_cache and self.device_combo.current() < 0:
                self.device_combo.current(0)
            self.status.set(f"{len(self.devices_cache)} controle(s) detectado(s)")
        except Exception as exc:
            self.status.set(f"Entrada indisponível: {exc}")

    def connect_device(self):
        if not self.devices_cache:
            self.refresh_devices()
        if not self.devices_cache:
            messagebox.showwarning("PadForge", "Nenhum controle foi detectado.")
            return
        pos = max(0, self.device_combo.current())
        info = self.input.connect(self.devices_cache[pos].index)
        save_mapping(self.mapping)
        self.engine = PadForgeEngine(self.input, self.output if self.output.available else NullOutput(), self.profiles)
        profile = self.profiles.get(self.profile_name.get())
        if profile:
            self.engine.set_profile(profile)
        self.engine.auto_profile = self.auto_profile.get()
        self.engine.start()
        mode = "SDL automático" if info.sdl_mapped else "raw/manual"
        self.status.set(f"Conectado: {info.name} · {mode}")

    def change_profile(self, _event=None):
        if self.engine:
            profile = self.profiles.get(self.profile_name.get())
            if profile:
                self.engine.set_profile(profile)

    def toggle_auto(self):
        if self.engine:
            self.engine.auto_profile = self.auto_profile.get()

    def save_mapping_ui(self):
        for logical, var in self.button_vars.items():
            try:
                idx = int(var.get())
            except ValueError:
                continue
            target = self.mapping.triggers_as_buttons if logical in ("lt", "rt") else self.mapping.buttons
            target[logical] = idx
        for logical, var in self.axis_vars.items():
            try:
                self.mapping.axes[logical] = int(var.get())
            except ValueError:
                pass
        save_mapping(self.mapping)
        if self.input:
            self.input.mapping = self.mapping
        self.status.set("Mapeamento salvo")

    def refresh_live(self):
        if self.engine:
            state = self.engine.state
            pressed = [k.upper() for k, v in state.buttons.items() if v]
            axes = "  ".join(f"{k.upper()} {state.axes.get(k, 0):+.2f}" for k in ("lx", "ly", "rx", "ry", "lt", "rt"))
            self.live.set(f"Botões: {', '.join(pressed) if pressed else 'nenhum'}\n{axes}\nPerfil: {self.engine.profile.name}")
            snap = self.engine.raw or {}
            lines = ["AXES"] + [f"  a{i}: {v:+.4f}" for i, v in enumerate(snap.get("axes", []))]
            lines += ["", "BUTTONS"] + [f"  b{i}: {'ON' if v else 'off'}" for i, v in enumerate(snap.get("buttons", []))]
            lines += ["", "HATS"] + [f"  h{i}: {v}" for i, v in enumerate(snap.get("hats", []))]
            self._set_raw("\n".join(lines))
            if self.profile_name.get() != self.engine.profile.name:
                self.profile_name.set(self.engine.profile.name)
        self.after(33, self.refresh_live)

    def start_calibration(self):
        if not self.input or not self.input.joystick:
            messagebox.showwarning("PadForge", "Conecte um controle antes de calibrar.")
            return
        self.cal_phase, self.cal_ticks = "center", 0
        self.center_samples = {n: [] for n in ("lx", "ly", "rx", "ry")}
        self.range_samples = {n: [] for n in ("lx", "ly", "rx", "ry")}
        self.calibration_status.set("Solte os analógicos e deixe no centro...")
        self.after(20, self._calibration_step)

    def _calibration_step(self):
        snap = self.input.raw_snapshot() if self.input else {"axes": []}
        axes = snap.get("axes", [])
        target = self.center_samples if self.cal_phase == "center" else self.range_samples
        for logical in target:
            idx = self.mapping.axes.get(logical, -1)
            if 0 <= idx < len(axes):
                target[logical].append(float(axes[idx]))
        self.cal_ticks += 1
        if self.cal_phase == "center" and self.cal_ticks >= 50:
            self.cal_phase, self.cal_ticks = "range", 0
            self.calibration_status.set("Gire os dois analógicos até todos os limites...")
        elif self.cal_phase == "range" and self.cal_ticks >= 200:
            self._finish_calibration()
            return
        self.after(20, self._calibration_step)

    def _finish_calibration(self):
        report = []
        for logical in self.center_samples:
            center_values = self.center_samples[logical]
            if not center_values:
                continue
            center = sum(center_values) / len(center_values)
            all_values = center_values + self.range_samples[logical]
            jitter = max((abs(v - center) for v in center_values), default=0.0)
            dz = max(0.04, min(0.18, jitter * 2.5 + 0.02))
            self.calibrations[logical] = AxisCalibration(center=center, minimum=min(all_values), maximum=max(all_values), deadzone=dz)
            report.append(f"{logical.upper()} DZ {dz:.2f}")
        save_calibrations(self.calibrations)
        if self.input:
            self.input.calibrations = self.calibrations
        self.calibration_status.set("Calibrado · " + " | ".join(report))
        self.status.set("Analog Doctor concluído")

    def on_close(self):
        if self.engine:
            self.engine.stop()
        else:
            self.output.close()
        if self.input:
            self.input.close()
        self.destroy()


def main():
    PadForgeApp().mainloop()


if __name__ == "__main__":
    main()
