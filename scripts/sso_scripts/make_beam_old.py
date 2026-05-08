#!/usr/bin/env python3
import h5py, numpy as np
from math import log, sqrt, pi

def write_gaussian_beam_h5(
    out_path: str,
    fwhm_arcmin: float = 30.0,   # beam FWHM
    res_arcmin: float | None = None,  # pixel size
    size_fwhm: float = 8.0       # map width in units of FWHM (total width)
):
    """
    Create a Gaussian beam map and save it as an HDF5 file.
    
    Parameters
    ----------
    out_path : str
        Path to the output HDF5 file containing the beam.

    fwhm_arcmin : float
        Full Width at Half Maximum (FWHM) of the Gaussian beam in arcminutes.
        This sets the intrinsic width of the beam profile.

    res_arcmin : float or None
        Pixel resolution of the beam map in arcminutes per pixel. This controls
        how finely the Gaussian is sampled in the 2D beam image. Should be small
        compared to the FWHM (≈ FWHM/5 or FWHM/10 is typical). If None, a default
        value of ~FWHM/25 is chosen.

    size_fwhm : float
        Size of the beam map (side length) expressed in multiples of the FWHM.
        Determines how much of the beam wings are included in the map.
        Typical choices are 6 to 10 x FWHM to capture enough of the beam's solid angle.

    Notes
    -----
    - These parameters only describe the internal beam map used by SimSSO for
      interpolation, not the resolution of the final science map.
    - The function writes an HDF5 file with dataset 'beam' and attributes:
      'size' (deg), 'res' (deg/pix), and 'npix' (int).
    
    Create HDF5 beam with:
       - dataset 'beam' (n x n)
       - attrs: size (deg), res (deg/pix), npix (int)
    """
    fwhm_deg = fwhm_arcmin / 60.0
    sigma_rad = (fwhm_deg * np.pi/180.0) / sqrt(8.0 * log(2.0))

    if res_arcmin is None:
        res_arcmin = max( fwhm_arcmin / 25.0, 0.1 )  # sensible default & avoid tiny pixels
    res_deg = res_arcmin / 60.0

    size_deg = size_fwhm * fwhm_deg            # total width in degrees
    npix = int(round(size_deg / res_deg))
    if npix % 2 == 0:
        npix += 1                               # prefer odd so center pixel exists

    # Grid in degrees (for metadata) + radians (for Gaussian calc)
    half = size_deg / 2.0
    x_deg = np.linspace(-half, half, npix)
    x_rad = np.deg2rad(x_deg)
    Xr, Yr = np.meshgrid(x_rad, x_rad, indexing="xy")

    # Circular Gaussian, unnormalized: integral ≈ 2πσ² when map is wide enough
    beam = np.exp(-(Xr**2 + Yr**2) / (2.0 * sigma_rad**2)).astype(np.float32)

    # Write HDF5
    with h5py.File(out_path, "w") as f:
        dset = f.create_dataset("beam", data=beam, compression="gzip", compression_opts=4)
        dset.attrs["size"] = float(size_deg)         # degrees (total width)
        dset.attrs["res"]  = float(res_deg)          # degrees per pixel
        dset.attrs["npix"] = int(npix)

    # Report effective solid angle estimate (for sanity check)
    omega_est = beam.sum() * (np.deg2rad(res_deg)**2)
    print(f"Wrote {out_path}")
    print(f"  FWHM = {fwhm_arcmin:.3f} arcmin, res = {res_arcmin:.3f} arcmin, npix = {npix}, size = {size_deg:.3f} deg")
    print(f"  Ω_beam (sum*res^2) ≈ {omega_est:.6e} sr  |  2πσ² = {2*pi*sigma_rad**2:.6e} sr")

if __name__ == "__main__":
    # Example: 47" = 0.78' FWHM, res = 0.1*fwhm, map width = 8×FWHM
    write_gaussian_beam_h5("data/gauss_beam.h5", fwhm_arcmin=0.78, res_arcmin=0.1, size_fwhm=8.0)
