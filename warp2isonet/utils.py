from pathlib import Path
import mrcfile
import starfile
import pandas as pd
from warpylib import TiltSeries
import torch

import gc

import os

def parse_tomos(processing_folder: Path):
    """Return a list of TiltSeries objects from a processing_path.
    
    Inputs:
        processing_folder (Path): folder with WarpTools processing results.
    
    Returns:
        tomo_list ([]): list containing TiltSeries objects for all tomograms in folder.
    """
    
    tomo_list = []
    
    for tomo in processing_folder.glob('*.xml'):
        ts = TiltSeries(tomo)
        
        tomo_list.append(ts)
        
    return tomo_list
        
def make_noCTF_EVNODD(ts: TiltSeries,
                      binning: int,
                      isonet_root_dir: Path,
                      dim_px = (4092,5760,3000)):
    """Make EVN/ODD tomogram without any CTF modulation.
    
    Inputs:
        ts (TiltSeries): warpylib TiltSeries to work on.
        binning (int): binning level to reconstruct at.
        isonet_root_dir (Path): output path for all IsoNet2 processing.
        dim_px (tuple(int,int,int)): xyz extent of tomogram in unbinned pixels.
        
    Returns:
        tomo_values ({}): dict with all relevant values for IsoNet2 star file.
    """

    # prepare output folders
    tomo_dir = isonet_root_dir / "tomo"
    
    if not os.path.isdir(tomo_dir):
        os.mkdir(tomo_dir)
                
    # reset CTF information in the memory to get tomogram without any correction
    y_offset = ts.level_angle_y

    defocus_um  = ts.ctf.get_copy().defocus
    t_max = ts.max_tilt + y_offset
    t_min = ts.min_tilt + y_offset
    
    # set global CTF variables to disable CTF
    ts.ctf.amplitude = 1
    ts.ctf.cc = 0
    ts.ctf.cs = 0
    ts.ctf.defocus = 0
    ts.ctf.defocus_delta = 0
    
    ts.grid_ctf_defocus.values = torch.zeros(ts.grid_ctf_defocus.flat_values.shape)
    ts.grid_ctf_defocus_delta.values = torch.zeros(ts.grid_ctf_defocus_delta.flat_values.shape)
    
    # generate output pixel sizes and tomogram dimensions
    orig_angpix = ts.ctf.pixel_size
    out_angpix = orig_angpix * binning
    
    dim_a = torch.tensor([dim_px[0] * orig_angpix,
                                                 dim_px[1] * orig_angpix,
                                                 dim_px[2] * orig_angpix],
                                                 dtype = torch.float32)
    
    ts.volume_dimensions_physical = dim_a
    
    # reconstruct with EVN/ODD
    evn_path = tomo_dir /  f'{ts.name[:-4]}_even.mrc'
    odd_path = tomo_dir /  f'{ts.name[:-4]}_odd.mrc'
    
    _, ts_evn, ts_odd = ts.load_images(original_pixel_size = orig_angpix, 
                                       desired_pixel_size = out_angpix,
                                       load_half_averages = True)
    
    tomo_evn = ts.reconstruct_full(tilt_data = ts_evn,
                                   pixel_size =  out_angpix,
                                   volume_dimensions_physical = dim_a)
    
    mrcfile.write(evn_path,
                  data = tomo_evn.numpy(),
                  overwrite = True,
                  voxel_size = out_angpix)
    
    tomo_odd = ts.reconstruct_full(tilt_data = ts_odd,
                                   pixel_size =  out_angpix,
                                   volume_dimensions_physical = dim_a)
    
    mrcfile.write(odd_path,
                  data = tomo_odd.numpy(),
                  overwrite = True,
                  voxel_size = out_angpix)
    
    
    # save values to starfile
    tomo_values = {'rlnTomoName': f'{ts.name[:-4]}',
                   'rlnTomoReconstructedTomogramHalf1': evn_path,
                   'rlnTomoReconstructedTomogramHalf2': odd_path,
                   'rlnPixelSize': out_angpix,
                   'rlnDefocus': int(defocus_um * 10000),
                   'rlnTiltMin': round(t_min),
                   'rlnTiltMax': round(t_max),}
    
    ts.save_meta(tomo_dir / f'{ts.name[:-4]}.xml')
    
    del ts_evn, ts_odd, tomo_evn, tomo_odd
    gc.collect()
    
    return tomo_values

def loop_over_tomograms(processing_folder: Path,
                        isonet_root_dir: Path,
                        binning: int,
                        dim_px: (int,int,int)):
    """Convert WarpTools processing folder for IsoNet2 processing.
    
    Inputs:
        processing_folder (Path): Folder with WarpTools tomogram processing results.
        isonet_root_dir (Path): Folder for IsoNet2 processing.
        binning (int): Binning level for reconstructions.
        dim_px (tuple(int,int,int)): Final tomogram dimensions, in unbinned pixels.

    Returns:
        EVN/ODD reconstructions without CTF modulation for all tomograms.
        tomograms.star file for IsoNet2 processing with all relevant metadata values.
    """
    
    tomo_list = parse_tomos(processing_folder)
    
    output_star_list = []
    
    for tomo in tomo_list:
        particle_star = make_noCTF_EVNODD(tomo, 
                          binning, 
                          isonet_root_dir)
        
        output_star_list.append(particle_star)
    
    output_star = pd.DataFrame().from_records(output_star_list)
    
    output_star['rlnIndex'] = output_star.index + 1
    output_star['rlnVoltage'] = 300
    output_star['rlnSphericalAberration'] = 2.7
    output_star['rlnAmplitudeContrast'] = 0.07
    output_star['rlnDeconvTomoName'] = "None"
    output_star['rlnMaskBoundary'] = "None"
    output_star['rlnMaskName'] = "None"
    output_star['rlnBoxFile'] = "None"
    output_star['rlnCorrectedTomoName'] = "None"
    output_star['rlnDenoisedTomoName'] = "None"
    output_star['rlnNumberSubtomo'] = round(6000 / len(output_star.index))

    starfile.write(output_star, 
                   isonet_root_dir / f'isonet2_tomos_bin_{binning}.star')
    