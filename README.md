# primecam_sims_planetobs

PrimeCam / FYST planet-observation simulations using TOAST. The main workflow
generates detector timestreams for Solar System Object (SSO) observations,
writes TOAST HDF5 files, optionally makes filter-and-bin maps, and provides
helpers for FITS plotting and SPT3G conversion. Currently, we have only tested 
with observations of Jupiter.

These jobs are memory intensive. Use the Slurm scripts on a cluster for normal
production runs.

For queries, please contact:

Author(s): Ankur Dev (adev@uni-bonn.de)

## Workflow

1. Prepare or update the SSO beam file (optional step, beam file included).
2. Run the timestream simulation with `ramses_mockdata_sim.slurm`.
3. Optionally make maps with `ramses_fbmap.slurm`.
4. Inspect FITS map products with `scripts/plot_scripts/plot_fits_map.py`.
5. Convert TOAST HDF5 output to SPT3G with `scripts/helper_scripts/toast_h5_g3.py`.

## SSO Signal
The SSO simulation script used here was based on 
[sotodlib implementation](https://github.com/simonsobs/sotodlib/blob/v0.6.3/sotodlib/toast/ops/sim_sso.py)

SSO simulation is handled by `scripts/sso_scripts/sim_sso.py` and is called from
`sim_data_primecam_mpi.py`. The current pipeline simulates Jupiter using the
beam file at:

```bash
scripts/sso_scripts/data/gauss_beam.h5
```

The SSO name must be recognized by PyEphem. The simulation writes the SSO signal
into the detector timestreams along with atmosphere and detector noise.

## Make the Beam File

The default Gaussian beam file can be regenerated with:

```bash
cd scripts/sso_scripts
python make_beam.py
cd ../..
```

This writes:

```bash
scripts/sso_scripts/data/gauss_beam.h5
```

The script currently uses a 0.7833 arcmin FWHM Gaussian beam, matching the
default 280 GHz beam setting used by the simulation.

## Run Timestream Simulations

The recommended entry point is the Slurm array script:

```bash
sbatch ramses_mockdata_sim.slurm
```

Before launching, edit the Slurm header and job settings in
`ramses_mockdata_sim.slurm` as needed:

- `#SBATCH --array=...` selects which schedule files to run from
  `input_files/schedules/*.txt`.
- `#SBATCH --ntasks-per-node`, `#SBATCH --cpus-per-task`, `#SBATCH --nodes`,
  `#SBATCH --mem`, and `#SBATCH --time` control resources.
- `ndets=...` selects the detector count.

Logs are written to:

```bash
logs_sims/
```

Simulation output is written under:

```bash
ccat_datacenter_mock/mockdata/planet_ATMdata_d<NDETS>/
```

For example, a 100-detector Jupiter run writes HDF5 observations below a
directory like:

```bash
ccat_datacenter_mock/mockdata/planet_ATMdata_d100/sim_PCAM280_h5_Jupiter_d100/
```

For a small manual run, use:

```bash
export OMP_NUM_THREADS=2
mpirun -np 4 python sim_data_primecam_mpi.py \
    --sch schedule_Jupiter_0_5deg.txt \
    --dets 100
```

Only pass the schedule file name to `--sch`; schedule files are read from
`input_files/schedules/`.

## Make Filter-and-Bin Maps

Use the mapmaking Slurm script after timestream HDF5 output exists:

```bash
sbatch ramses_fbmap.slurm
```

Before launching, edit section 4 of `ramses_fbmap.slurm`:

- `INDIR` is the input TOD directory inside `ccat_datacenter_mock/mockdata/`.
- `OUTDIR` is the output map directory inside `ccat_datacenter_mock/fb_maps/`.
- `GRP_SIZE` is the MPI group size.
- `MAP_PREFIX` controls the output FITS file prefix.

The Slurm script runs `write_toast_maps.py` and writes products such as:

```bash
ccat_datacenter_mock/fb_maps/<OUTDIR>/<MAP_PREFIX>_map.fits
ccat_datacenter_mock/fb_maps/<OUTDIR>/<MAP_PREFIX>_hits.fits
ccat_datacenter_mock/fb_maps/<OUTDIR>/<MAP_PREFIX>_invcov.fits
```

## Plot FITS Maps

Use the plotting helper to make a PNG from a FITS map:

```bash
python scripts/plot_scripts/plot_fits_map.py \
    ccat_datacenter_mock/fb_maps/<OUTDIR>/<MAP_PREFIX>_map.fits
```

By default, the PNG is written next to the FITS file. Useful options:

```bash
python scripts/plot_scripts/plot_fits_map.py MAP.fits --mk-units
python scripts/plot_scripts/plot_fits_map.py MAP.fits --save quicklook.png
python scripts/plot_scripts/plot_fits_map.py MAP.fits --vmin -1 --vmax 1
python scripts/plot_scripts/plot_fits_map.py MAP.fits --no-wcs
```

Run help for the full option list:

```bash
python scripts/plot_scripts/plot_fits_map.py -h
```

## Convert TOAST HDF5 to SPT3G

Convert one TOAST HDF5 observation directory at a time:

```bash
python scripts/helper_scripts/toast_h5_g3.py \
    ccat_datacenter_mock/mockdata/planet_ATMdata_d100/sim_PCAM280_h5_Jupiter_d100/
```

The converter creates a sibling directory with `h5` replaced by `g3`, for
example:

```bash
sim_PCAM280_g3_Jupiter_d100/
```

The converter stops if the target G3 directory already exists.

## Useful Checks

Show command-line help:

```bash
python sim_data_primecam_mpi.py -h
python write_toast_maps.py -h
python scripts/helper_scripts/toast_h5_g3.py -h
```
