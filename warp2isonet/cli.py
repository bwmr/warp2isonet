from pathlib import Path

import click

from warp2isonet.utils import loop_over_tomograms


@click.command()
@click.option(
    "--processing-folder",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Folder with WarpTools tomogram processing results (contains .xml files).",
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
@click.option(
    "--dim-px",
    type=(int, int, int),
    default=(4092, 5760, 3000),
    show_default=True,
    help="Final tomogram dimensions in unbinned pixels (X Y Z).",
)
def main(
    processing_folder: Path,
    isonet_root_dir: Path,
    binning: int,
    dim_px: tuple,
) -> None:
    """Convert a WarpTools processing folder into IsoNet2-ready EVN/ODD reconstructions."""
    isonet_root_dir.mkdir(parents=True, exist_ok=True)
    loop_over_tomograms(
        processing_folder=processing_folder,
        isonet_root_dir=isonet_root_dir,
        binning=binning,
        dim_px=dim_px,
    )


if __name__ == "__main__":
    main()
