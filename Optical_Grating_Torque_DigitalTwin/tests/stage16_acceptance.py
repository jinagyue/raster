"""Stage-16 integrated platform acceptance."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; WORKSPACE=ROOT.parent
if str(WORKSPACE) not in sys.path: sys.path.insert(0,str(WORKSPACE))
from Optical_Grating_Torque_DigitalTwin.config.parameter import parameter
from Optical_Grating_Torque_DigitalTwin.control.torque_controller import TorqueController
from Optical_Grating_Torque_DigitalTwin.matlab.matlab_bridge import MatlabBridge
from Optical_Grating_Torque_DigitalTwin.control.torque_controller import encode_adc_frame

def run_acceptance():
    r={k:False for k in ('pass_gui','pass_engine_persistent','pass_torque_link','pass_temperature_link','pass_visual_motion','pass_camera_preserved','pass_signal_link','pass_waveform_dynamic','pass_adc_link','pass_serial_link','pass_serial_hardware_loop','pass_controls','pass')}
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    bridge=MatlabBridge(); c=TorqueController(parameter(),bridge)
    try:
        a=c.refresh(); e0=id(bridge._engine); adc0=np.asarray(a['simulation']['adc_code']); sig0=np.asarray(a['simulation']['five_channel_signal']); frame0=c.serial_preview()
        b=c.update(torque=0.5,temperature=60.0,grating_displacement=5e-6); adc1=np.asarray(b['simulation']['adc_code']); sig1=np.asarray(b['simulation']['five_channel_signal']); frame1=c.serial_preview()
        r['pass_engine_persistent']=id(bridge._engine)==e0
        r['pass_torque_link']=abs(float(a['mechanics']['torsion_angle'])-float(b['mechanics']['torsion_angle']))>0
        r['pass_temperature_link']=float(a['mechanics']['torsion_angle'])!=float(b['mechanics']['torsion_angle'])
        mark0=np.asarray(a['assembly']['main_grating']['orientation_mark'].GetBounds(),dtype=float)
        mark1=np.asarray(b['assembly']['main_grating']['orientation_mark'].GetBounds(),dtype=float)
        shaft0=np.asarray(a['assembly']['shaft'].GetBounds(),dtype=float)
        shaft1=np.asarray(b['assembly']['shaft'].GetBounds(),dtype=float)
        r['pass_visual_motion']=bool(np.max(np.abs(mark1-mark0))>1e-5 and np.max(np.abs(shaft1-shaft0))<1e-12)
        r['pass_signal_link']=np.max(np.abs(sig1-sig0))>0
        phase=np.asarray(b['simulation']['phase'],dtype=float).reshape(-1)
        r['pass_waveform_dynamic']=bool(sig1.shape[0] >= 100 and np.ptp(phase)>0 and np.ptp(sig1[:,1])>0)
        r['pass_adc_link']=np.max(np.abs(adc1-adc0))>=1
        r['pass_serial_link']=frame0!=frame1 and len(frame1)==11 and frame1[0]==0xAA and frame1[-2:] == encode_adc_frame(adc1[0,:])[-2:]
        from PyQt5 import QtWidgets
        from Optical_Grating_Torque_DigitalTwin.gui.main_window import MainWindow
        from Optical_Grating_Torque_DigitalTwin.communication.serial_streamer import SerialStreamer
        app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([]); w=MainWindow(TorqueController(parameter(),None)); app.processEvents(); r['pass_gui']=w.vtk.renderer.GetActors().GetNumberOfItems()>0 and w.waveforms.count()==4; r['pass_controls']=w.controls.torque is not None and w.controls.temperature is not None
        streamer=SerialStreamer('loop://',115200,200,adc1); streamer.start(); streamer.wait(150); streamer.stop(); r['pass_serial_hardware_loop']=bool(streamer.frames_sent>0 and streamer.bytes_sent==11*streamer.frames_sent)
        camera=w.vtk.renderer.GetActiveCamera(); camera.SetPosition(0.123,-0.234,0.345); camera.SetFocalPoint(0.001,0.002,0.003); before=np.asarray(camera.GetPosition()); w.vtk.set_assembly(b['assembly']); after=np.asarray(camera.GetPosition()); r['pass_camera_preserved']=bool(np.max(np.abs(after-before))<1e-12)
        w.close(); app.processEvents()
        r['rows']=int(sig1.shape[0]); r['adc_shape']=list(adc1.shape); r['serial_bytes']=len(frame1)
    except Exception as ex:r['error']=f'{type(ex).__name__}: {ex}'
    finally: bridge.close()
    r['pass']=all(r[k] for k in ('pass_gui','pass_engine_persistent','pass_torque_link','pass_temperature_link','pass_visual_motion','pass_camera_preserved','pass_signal_link','pass_waveform_dynamic','pass_adc_link','pass_serial_link','pass_serial_hardware_loop','pass_controls')); return r
if __name__=='__main__':
    out=run_acceptance(); print(json.dumps(out,ensure_ascii=False,indent=2,default=lambda x: bool(x) if hasattr(x,'item') and isinstance(x.item(), bool) else x.item() if hasattr(x,'item') else str(x))); raise SystemExit(0 if out['pass'] else 1)
