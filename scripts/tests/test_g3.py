import numpy as np
from spt3g import core as c3g
from toast.spt3g.spt3g_utils import decompress_timestream  # ← TOAST helper

exit(0)
g3_file = 'ccat_datacenter_mock/data_testmpi/planet_WNdata_d100/sim_PCAM280_g3_Jupiter_d100/Jupiter-0-0/frames-0000.g3'
det = None
y_all = []
exit(0)

for fr in c3g.G3File(g3_file):
    if fr.type == c3g.G3FrameType.Scan:
        tsmap = fr["signal"]
        if det is None:
            det = next(iter(tsmap.keys()))
        # per-frame metadata
        gain   = float(fr[f"compress_signal_{det}_gain"])
        offset = float(fr[f"compress_signal_{det}_offset"])
        units  = c3g.G3TimestreamUnits(fr[f"compress_signal_{det}_units"])

        # TOAST’s exact reconstruction (includes unit scaling)
        y = decompress_timestream(tsmap[det], gain, offset, units)  # → np.float64
        y_all.append(y)

y = np.concatenate(y_all)
fs = 488.0
t  = np.arange(len(y)) / fs

import matplotlib.pyplot as plt
plt.figure(figsize=(10,4))
plt.plot(t, y, lw=0.8, label=str(det))
plt.xlabel("Time [s]"); plt.ylabel("Signal [K]")
plt.legend(); plt.tight_layout(); 
plt.save('test_calib_g3.png')
