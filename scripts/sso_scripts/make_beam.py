#!/usr/bin/env python3
import h5py, numpy as np
from math import log, sqrt, pi

def write_gaussian_beam_h5(
    out_path: str,
    fwhm_arcmin: float = 30.0,
    res_arcmin: float | None = None,   # ≈ FWHM/8–10 is good
    size_fwhm: float = 8.0             # total width in units of FWHM
):
    """
    Write a 2D circular Gaussian beam kernel with **unit discrete sum**.
    Use for temperature-preserving convolution on maps in K_CMB.
    """
    # --- geometry ---
    fwhm_deg = fwhm_arcmin / 60.0
    sigma_rad = (fwhm_deg * np.pi/180.0) / sqrt(8.0 * log(2.0))

    if res_arcmin is None:
        res_arcmin = max(fwhm_arcmin / 10.0, 0.05)  # ≥~10 samples/FWHM; clamp to avoid tiny pixels
    res_deg = res_arcmin / 60.0
    res_rad = np.deg2rad(res_deg)

    size_deg = size_fwhm * fwhm_deg
    npix = int(round(size_deg / res_deg))
    if npix % 2 == 0:
        npix += 1  # center pixel

    # --- grid & unnormalized Gaussian (peak = 1) ---
    half = size_deg / 2.0
    x_deg = np.linspace(-half, half, npix)
    x_rad = np.deg2rad(x_deg)
    Xr, Yr = np.meshgrid(x_rad, x_rad, indexing="xy")
    beam = np.exp(-(Xr**2 + Yr**2) / (2.0 * sigma_rad**2)).astype(np.float64)

    # --- normalize to **unit discrete sum** (temperature-preserving) ---
    beam_sum = beam.sum()
    beam /= beam_sum  # now sum(beam) == 1.0

    # Diagnostics (continuous vs discrete estimates)
    omega_theory = 2.0 * pi * sigma_rad**2              # ideal continuous 2πσ²
    omega_discrete = beam_sum * (res_rad**2)            # before renorm; after renorm = res_rad**2

    # --- write HDF5 ---
    with h5py.File(out_path, "w") as f:
        dset = f.create_dataset("beam", data=beam.astype(np.float32),
                                compression="gzip", compression_opts=4)
        dset.attrs["npix"] = int(npix)
        dset.attrs["size"] = float(size_deg)
        dset.attrs["res"] = float(res_deg)
        # Optional 
        dset.attrs["fwhm_arcmin"] = float(fwhm_arcmin)
        dset.attrs["sigma_rad"] = float(sigma_rad)
        dset.attrs["norm"] = "unit_sum"
        dset.attrs["pixel_area_sr"] = float(res_rad**2)
        dset.attrs["omega_theory_sr"] = float(omega_theory)
        dset.attrs["omega_discrete_sr_pre_norm"] = float(omega_discrete)
        dset.attrs["map_units"] = "K_CMB"  # for clarity in your pipeline

    print(f"Wrote {out_path}")
    print(f"  FWHM={fwhm_arcmin:.3f}'  res={res_arcmin:.3f}'  npix={npix}  size={size_deg:.3f} deg")
    print(f"  Beam normalized to unit discrete sum (∑beam = {beam.sum():.6f}).")
    print(f"  Ω_theory=2πσ²={omega_theory:.6e} sr | pixel_area={res_rad**2:.6e} sr")

if __name__ == "__main__":
    # Example: 47″ = 0.7833′
    write_gaussian_beam_h5("data/gauss_beam.h5", fwhm_arcmin=0.7833, res_arcmin=0.08, size_fwhm=8.0)
