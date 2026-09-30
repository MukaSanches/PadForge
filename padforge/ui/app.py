from __future__ import annotations
import os,time,tkinter as tk
from tkinter import ttk,messagebox
from typing import Dict
from padforge import __version__
from padforge.core.calibration import CalibrationSession
from padforge.core.controllers import ControllerConfigStore,controller_key
from padforge.core.models import AxisCalibration
from padforge.core.profiles import ProfileStore
from padforge.runtime import PadForgeRuntime
from padforge.system.settings import Settings,app_data_dir
from padforge.system import autostart,virtual_driver

BG='#0b0f14'; PANEL='#121821'; CARD='#18212c'; TEXT='#e8eef5'; MUTED='#91a0b2'; ACCENT='#4aa3ff'; GOOD='#55d187'; WARN='#ffbe55'; BAD='#ff667a'

class PadForgeApp(tk.Tk):
    def __init__(self,builtin_profiles:str):
        super().__init__(); self.title(f'PadForge {__version__}'); self.geometry('1040x700'); self.minsize(900,600); self.configure(bg=BG)
        self.settings_data=Settings.load()
        self.store=ProfileStore(builtin_profiles,os.path.join(app_data_dir(),'profiles.json')); self.store.load()
        self.controllers=ControllerConfigStore(os.path.join(app_data_dir(),'controllers.json'))
        self.runtime=PadForgeRuntime(self.store,self.controllers,poll_hz=self.settings_data.poll_hz)
        self.runtime.set_profile(self.settings_data.profile_id,manual=True); self.runtime.auto_profile=self.settings_data.auto_profile
        self._device_by_label:Dict[str,int]={}; self._device_key_by_instance:Dict[int,str]={}; self._profile_by_label:Dict[str,str]={}; self._overlay=None
        self._style(); self._build(); self.protocol('WM_DELETE_WINDOW',self._close); self.runtime.start(); self.after(80,self._refresh)

    def _style(self):
        s=ttk.Style(self)
        try:s.theme_use('clam')
        except Exception:pass
        s.configure('TCombobox',fieldbackground=CARD,background=CARD,foreground=TEXT,arrowcolor=TEXT)
        s.configure('TCheckbutton',background=PANEL,foreground=TEXT); s.map('TCheckbutton',background=[('active',PANEL)])

    def _button(self,parent,text,cmd,primary=False):
        b=tk.Button(parent,text=text,command=cmd,relief='flat',bd=0,bg=ACCENT if primary else CARD,fg='#07111b' if primary else TEXT,activebackground='#6bb5ff' if primary else '#223042',font=('Segoe UI',10,'bold'),pady=9,cursor='hand2'); b.pack(fill='x',pady=4); return b

    def _card(self,parent,title):
        f=tk.Frame(parent,bg=PANEL,highlightthickness=1,highlightbackground='#202b37'); f.pack(fill='x',pady=(0,13))
        tk.Label(f,text=title,bg=PANEL,fg=TEXT,font=('Segoe UI',11,'bold')).pack(anchor='w',padx=16,pady=(13,8))
        body=tk.Frame(f,bg=PANEL); body.pack(fill='x',padx=16,pady=(0,14)); return body

    def _build(self):
        top=tk.Frame(self,bg=PANEL,height=68); top.pack(fill='x'); top.pack_propagate(False)
        tk.Label(top,text='PADFORGE',bg=PANEL,fg=TEXT,font=('Segoe UI',20,'bold')).pack(side='left',padx=24)
        tk.Label(top,text='ANY CONTROLLER. ANY GAME.',bg=PANEL,fg=ACCENT,font=('Segoe UI',9,'bold')).pack(side='left')
        self.pill=tk.Label(top,text='INICIANDO',bg=WARN,fg=BG,font=('Segoe UI',9,'bold'),padx=12,pady=5); self.pill.pack(side='right',padx=24)
        root=tk.Frame(self,bg=BG); root.pack(fill='both',expand=True,padx=22,pady=18)
        left=tk.Frame(root,bg=BG); left.pack(side='left',fill='both',expand=True)
        right=tk.Frame(root,bg=BG,width=310); right.pack(side='right',fill='y',padx=(16,0)); right.pack_propagate(False)

        body=self._card(left,'CONTROLE E PERFIL')
        row=tk.Frame(body,bg=PANEL); row.pack(fill='x')
        a=tk.Frame(row,bg=PANEL); a.pack(side='left',fill='x',expand=True,padx=(0,7))
        b=tk.Frame(row,bg=PANEL); b.pack(side='left',fill='x',expand=True,padx=(7,0))
        tk.Label(a,text='Controle físico',bg=PANEL,fg=MUTED).pack(anchor='w'); self.device=ttk.Combobox(a,state='readonly'); self.device.pack(fill='x',pady=(5,0)); self.device.bind('<<ComboboxSelected>>',self._device_changed)
        tk.Label(b,text='Perfil do jogo',bg=PANEL,fg=MUTED).pack(anchor='w'); self.profile=ttk.Combobox(b,state='readonly'); self.profile.pack(fill='x',pady=(5,0)); self.profile.bind('<<ComboboxSelected>>',self._profile_changed)
        for p in self.store.all(): self._profile_by_label[p.name]=p.id
        self.profile['values']=list(self._profile_by_label)
        p=self.store.get(self.runtime.manual_profile_id)
        if p:self.profile.set(p.name)

        body=self._card(left,'ANALOG DOCTOR — AO VIVO')
        self.canvas=tk.Canvas(body,bg=PANEL,height=215,highlightthickness=0); self.canvas.pack(fill='x')
        self.live=tk.Label(body,text='Aguardando controle...',bg=PANEL,fg=MUTED,font=('Consolas',9),justify='left'); self.live.pack(anchor='w',pady=(6,0))

        body=self._card(left,'STATUS')
        self.status=tk.Label(body,text='-',bg=PANEL,fg=TEXT,font=('Consolas',9),justify='left',wraplength=650); self.status.pack(anchor='w')
        self.error=tk.Label(body,text='',bg=PANEL,fg=BAD,font=('Segoe UI',9),justify='left',wraplength=650); self.error.pack(anchor='w',pady=(6,0))

        body=self._card(right,'CONFIGURAÇÃO')
        self._button(body,'Configurar controle completo',self._map_controller,True)
        self._button(body,'Analog Doctor — calibrar',self._calibrate)
        self._button(body,'Abrir overlay',self._toggle_overlay)
        self._button(body,'Reiniciar motor',self._restart)
        self._button(body,'Verificar saída virtual',self._probe)
        self._button(body,'Instalar / reparar driver virtual',self._install_driver)

        body=self._card(right,'AUTOMAÇÃO')
        self.auto=tk.BooleanVar(value=self.settings_data.auto_profile); ttk.Checkbutton(body,text='Perfil automático pelo jogo',variable=self.auto,command=self._toggle_auto).pack(anchor='w',pady=4)
        self.start=tk.BooleanVar(value=autostart.is_enabled()); ttk.Checkbutton(body,text='Iniciar com o Windows',variable=self.start,command=self._toggle_start).pack(anchor='w',pady=4)
        tk.Label(body,text='Mapeamento e calibração ficam vinculados ao controle físico; trocar de jogo não apaga a configuração.',bg=PANEL,fg=MUTED,wraplength=270,justify='left').pack(anchor='w',pady=(10,0))

    def _device_changed(self,_=None):
        iid=self._device_by_label.get(self.device.get()); self.runtime.select_device(iid)
        if iid is not None:self.settings_data.selected_device_key=self._device_key_by_instance.get(iid,''); self.settings_data.save()

    def _profile_changed(self,_=None):
        pid=self._profile_by_label.get(self.profile.get())
        if pid:self.runtime.set_profile(pid,manual=True); self.settings_data.profile_id=pid; self.settings_data.save()

    def _toggle_auto(self):
        self.runtime.auto_profile=bool(self.auto.get()); self.settings_data.auto_profile=bool(self.auto.get()); self.settings_data.save()

    def _toggle_start(self):
        if not autostart.set_enabled(bool(self.start.get())): messagebox.showwarning('PadForge','Não foi possível alterar a inicialização automática.')

    def _restart(self): self.runtime.stop(); self.runtime.start()

    def _probe(self):
        ok,msg=virtual_driver.virtual_output_probe(); (messagebox.showinfo if ok else messagebox.showwarning)('PadForge',msg)

    def _install_driver(self):
        ok,msg=virtual_driver.launch_vigem_installer(); (messagebox.showinfo if ok else messagebox.showwarning)('PadForge',msg)

    def _selected_config(self):
        cfg=self.runtime.selected_controller_config()
        if cfg is None: messagebox.showwarning('PadForge','Conecte e selecione um controle primeiro.')
        return cfg

    def _map_controller(self):
        cfg=self._selected_config()
        if not cfg:return
        steps=[('button','SOUTH','botão inferior (X/A)'),('button','EAST','botão direito (O/B)'),('button','WEST','botão esquerdo (□/X)'),('button','NORTH','botão superior (△/Y)'),('button','L1','L1'),('button','R1','R1'),('button','L2','L2'),('button','R2','R2'),('button','SELECT','Select/Back'),('button','START','Start'),('button','L3','clique do analógico esquerdo'),('button','R3','clique do analógico direito'),('dpad','DPAD_UP','D-pad para cima'),('dpad','DPAD_DOWN','D-pad para baixo'),('dpad','DPAD_LEFT','D-pad para esquerda'),('dpad','DPAD_RIGHT','D-pad para direita'),('axis','LX','analógico esquerdo para a DIREITA',1.0),('axis','LY','analógico esquerdo para BAIXO',-1.0),('axis','RX','analógico direito para a DIREITA',1.0),('axis','RY','analógico direito para BAIXO',-1.0)]
        win=tk.Toplevel(self); win.title('PadForge — Configurar controle'); win.geometry('560x260'); win.configure(bg=PANEL); win.transient(self)
        title=tk.Label(win,text='',bg=PANEL,fg=TEXT,font=('Segoe UI',15,'bold'),wraplength=500); title.pack(padx=24,pady=(28,10))
        raw_label=tk.Label(win,text='',bg=PANEL,fg=MUTED,font=('Consolas',9)); raw_label.pack(padx=24,pady=8)
        hint=tk.Label(win,text='Pressione/mova apenas o comando solicitado. O PadForge aprende o índice real do seu adaptador.',bg=PANEL,fg=MUTED,wraplength=500,justify='center'); hint.pack(padx=24,pady=8)
        st={'i':0,'prev':set(),'base':None,'entered':0.0}
        def enter():
            if not win.winfo_exists():return
            if st['i']>=len(steps):
                self.controllers.update(cfg); win.destroy(); messagebox.showinfo('PadForge','Mapeamento salvo. Agora rode o Analog Doctor para calibrar os sticks.'); return
            kind,key,label,*_=steps[st['i']]; title.config(text=f'{st["i"]+1}/{len(steps)} — {label}'); raw=self.runtime.raw_state(); st['prev']={i for i,v in (raw.buttons.items() if raw else []) if v}; st['base']=dict(raw.axes) if raw else {}; st['entered']=time.monotonic(); win.after(220,poll)
        def advance(): st['i']+=1; win.after(260,enter)
        def poll():
            if not win.winfo_exists() or st['i']>=len(steps):return
            raw=self.runtime.raw_state()
            if raw is None:win.destroy();return
            raw_label.config(text=f'Eixos {raw.axes}   Botões {[i for i,v in raw.buttons.items() if v]}   HAT {raw.hats}')
            step=steps[st['i']]; kind,key=step[0],step[1]
            if kind=='button':
                cur={i for i,v in raw.buttons.items() if v}; fresh=cur-st['prev']
                if fresh and time.monotonic()-st['entered']>.15:cfg.mapping.button_map[key]=min(fresh); advance(); return
                st['prev']=cur
            elif kind=='dpad':
                expected={'DPAD_UP':(0,1),'DPAD_DOWN':(0,-1),'DPAD_LEFT':(-1,0),'DPAD_RIGHT':(1,0)}[key]
                for hi,val in raw.hats.items():
                    if val==expected:
                        cfg.mapping.dpad_hat=hi; cfg.mapping.dpad_buttons.clear()
                        if key=='DPAD_UP':st['i']+=4; win.after(260,enter)
                        else:advance()
                        return
                cur={i for i,v in raw.buttons.items() if v}; fresh=cur-st['prev']
                if fresh and time.monotonic()-st['entered']>.15:cfg.mapping.dpad_hat=None; cfg.mapping.dpad_buttons[key]=min(fresh); advance(); return
                st['prev']=cur
            else:
                desired=float(step[3]); base=st['base']; candidates=[(abs(raw.axes.get(i,0)-base.get(i,0)),i,raw.axes.get(i,0)-base.get(i,0)) for i in raw.axes if abs(raw.axes.get(i,0)-base.get(i,0))>=.45]
                if candidates:
                    _,idx,delta=max(candidates); cfg.mapping.axis_map[key]=idx; cal=cfg.calibration.get(key,AxisCalibration()); cal.invert=delta*desired<0; cfg.calibration[key]=cal; advance(); return
            win.after(25,poll)
        enter()

    def _calibrate(self):
        cfg=self._selected_config()
        if not cfg:return
        win=tk.Toplevel(self); win.title('Analog Doctor'); win.geometry('520x220'); win.configure(bg=PANEL); win.transient(self)
        title=tk.Label(win,text='Deixe os analógicos soltos',bg=PANEL,fg=TEXT,font=('Segoe UI',15,'bold')); title.pack(pady=(32,8))
        detail=tk.Label(win,text='Medindo o centro por 2 segundos...',bg=PANEL,fg=MUTED,font=('Segoe UI',10)); detail.pack()
        session=CalibrationSession(); start=time.monotonic()
        def tick():
            raw=self.runtime.raw_state()
            if raw is None:win.destroy();return
            elapsed=time.monotonic()-start
            if elapsed<2.0:
                session.observe(raw.axes,neutral=True); detail.config(text=f'Centro: {max(0,2-elapsed):.1f}s'); win.after(20,tick); return
            if elapsed<7.0:
                session.observe(raw.axes,neutral=False); title.config(text='Gire os dois analógicos até as bordas'); detail.config(text=f'Faixa completa: {max(0,7-elapsed):.1f}s'); win.after(20,tick); return
            learned=session.calibration_for_mapping(cfg.mapping.axis_map)
            for axis,cal in learned.items():
                if axis in cfg.calibration:cal.invert=cfg.calibration[axis].invert
                cfg.calibration[axis]=cal
            self.controllers.update(cfg); win.destroy(); messagebox.showinfo('Analog Doctor','Calibração salva para este controle.')
        tick()

    def _toggle_overlay(self):
        if self._overlay and self._overlay.winfo_exists():self._overlay.destroy(); self._overlay=None; return
        self._overlay=tk.Toplevel(self); self._overlay.title('PadForge Overlay'); self._overlay.configure(bg='#05070a'); self._overlay.attributes('-topmost',True); self._overlay.geometry('420x130+20+20')
        self._overlay_label=tk.Label(self._overlay,text='PadForge',bg='#05070a',fg=TEXT,font=('Consolas',10),justify='left'); self._overlay_label.pack(anchor='w',padx=12,pady=10)

    def _draw(self):
        c=self.canvas; c.delete('all'); w=max(200,c.winfo_width()); h=max(160,c.winfo_height()); st=self.runtime.latest_state()
        for cx,cy,label,ax,ay in [(w*.24,h*.46,'L','LX','LY'),(w*.52,h*.46,'R','RX','RY')]:
            r=54; c.create_oval(cx-r,cy-r,cx+r,cy+r,outline='#344354',width=2); c.create_line(cx-r,cy,cx+r,cy,fill='#263441'); c.create_line(cx,cy-r,cx,cy+r,fill='#263441'); x=st.axes.get(ax,0); y=st.axes.get(ay,0); c.create_oval(cx+x*r-7,cy-y*r-7,cx+x*r+7,cy-y*r+7,fill=ACCENT,outline=''); c.create_text(cx,cy+r+16,text=f'{label} {x:+.2f} {y:+.2f}',fill=MUTED,font=('Consolas',8))
        pressed=[k for k,v in st.buttons.items() if v]; c.create_text(w*.78,24,text='BOTÕES ATIVOS',fill=MUTED,font=('Segoe UI',9,'bold'),anchor='n'); c.create_text(w*.78,50,text='\n'.join(pressed[:10]) or '—',fill=GOOD if pressed else MUTED,font=('Consolas',9,'bold'),anchor='n')
        self.live.config(text=f'{self.runtime.status.device_name} | LT {st.axes.get("LT",0):.2f} RT {st.axes.get("RT",0):.2f} | ID {self.runtime.status.controller_key[:8] or "—"}')

    def _refresh(self):
        if not self.winfo_exists():return
        devices=self.runtime.devices(); labels=[]; self._device_by_label.clear(); self._device_key_by_instance.clear(); desired=None
        for d in devices:
            key=controller_key(d.guid,d.name); label=f'{d.name} • {d.axes} eixos / {d.buttons} botões'; labels.append(label); self._device_by_label[label]=d.instance_id; self._device_key_by_instance[d.instance_id]=key
            if key==self.settings_data.selected_device_key:desired=label
        self.device['values']=labels
        if devices and self.runtime.selected_instance is None:
            pick=desired or labels[0]; self.device.set(pick); self.runtime.select_device(self._device_by_label[pick])
        elif devices:
            cur=next((label for label,iid in self._device_by_label.items() if iid==self.runtime.selected_instance),None)
            if cur:self.device.set(cur)
        else:self.device.set('')
        active=self.store.get(self.runtime.profile_id)
        if active and self.runtime.auto_profile:self.profile.set(active.name)
        s=self.runtime.status; ok=s.running and not s.error and bool(devices); self.pill.config(text='ATIVO' if ok else ('SEM CONTROLE' if not devices else 'ATENÇÃO'),bg=GOOD if ok else WARN)
        self.status.config(text=f'Perfil: {s.profile_name}\nSaída: {s.output_name}\nLoop: {s.input_hz:.0f} Hz | Físicos: {s.physical_count} | Virtuais: {s.virtual_count}\nProcesso: {s.foreground_process or "—"}'); self.error.config(text=s.error); self._draw()
        if self._overlay and self._overlay.winfo_exists():
            st=self.runtime.latest_state(); pressed=[k for k,v in st.buttons.items() if v]; self._overlay_label.config(text=f'PADFORGE • {s.profile_name}\n{s.device_name}\nLX {st.axes["LX"]:+.2f} LY {st.axes["LY"]:+.2f} RX {st.axes["RX"]:+.2f} RY {st.axes["RY"]:+.2f}\n{", ".join(pressed) or "nenhum botão"}')
        self.after(50,self._refresh)

    def _close(self): self.runtime.stop(); self.destroy()
