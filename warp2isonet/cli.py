from pathlib import Path

import click

from warp2isonet.utils import loop_over_tomograms, read_warp_settings


@click.command()
@click.option(
    "--settings",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to a warp_tiltseries.settings file (supplies the processing folder and tomogram dimensions).",
)
@click.option(
    "--isonet-root-dir",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
    help="Output folder for IsoNet2 processing.",
)
@click.option(
    "--binning",
    type=int,
    required=True,
    help="Binning level for reconstructions.",
)
def main(
    settings: Path,
    isonet_root_dir: Path,
    binning: int,
) -> None:
    """Convert a WarpTools processing folder into IsoNet2-ready EVN/ODD reconstructions."""
    processing_folder, dim_px = read_warp_settings(settings)

    isonet_root_dir.mkdir(parents=True, exist_ok=True)
    loop_over_tomograms(
        processing_folder=processing_folder,
        isonet_root_dir=isonet_root_dir,
        binning=binning,
        dim_px=dim_px,
    )


if __name__ == "__main__":
    main()
