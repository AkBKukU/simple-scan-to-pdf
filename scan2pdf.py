#!/usr/bin/env python3

# Python System
import argparse
import sys
import os
import json
from pprint import pprint
from enum import Enum

# External System
from wand.image import Image
from ocrmypdf import ocr

class PageLayouts(Enum):
    # Binding removed to work with single sheets
    UNBOUND_SADDLE_STITCH =           [[-1,1],[2,-2]]
    UNBOUND_DOUBLE_SIDED_SEQUENTIAL = [[1],[2]]
    # Binding intact
    FLAT_TWOPAGE =                    [[1,2]]
    FLAT_SINGLEPAGE =                 [[1]]
    # Book Edge Scanner
    EDGE_ROTATE =                     [[1],[2.2]]


def sectionImage(path,args,page_number,half=None, shrink=0,rotate=0):

    # Load image file
    img = Image(filename=path)
    # Convert to jpeg for file output
    img.format = 'jpeg'

    # Only process if args are present, used to pass covers through unchanged
    if args is not None:
        # Apply margin crop
        img.crop(
            args.margin_crop[0],
            args.margin_crop[2],
            img.size[0]-args.margin_crop[1],
            img.size[1]-args.margin_crop[3]
            )
        # Apply color level
        img.level(args.black,args.white,args.gamma)
        # Rotate full scan
        img.rotate(args.rotate)
        # Set grayscale
        if args.grayscale:
            img.type = "grayscale"
        # Crop to left side
        if half=="left" :
            img.crop(shrink, 0, round(img.size[0]/2-shrink/2), img.size[1])
        # Crop to right side
        if half=="right":
            img.crop(round(img.size[0]/2+shrink/2), 0, img.size[0], img.size[1])
        # Apply layout rotation
        img.rotate(rotate)
        # If export dir is set, save jpgs
        if args.export_dir is not None:
            outdir=str(args.export_dir)+"/"
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            img.save(filename=outdir+str(page_number).zfill(4)+"_"+path.replace(".tiff", ".jpg"))
    return img

def help_detailed():
    print(
"""
## Process Order

The following is the order that process operations are applied:

1. Margin Crop
2. Color Leveling (Black, White, Gamma)
3. Rotation
4. Grayscale
5. Page Isolation Cropping
6. Page Order Rotation

*Note: Prefix and Postfix covers do not go through any processing by design*

## Page Layouts

This software allows you to define a specific order for pages in scans. It
uses a two dimensional array where the first dimension is the scan file and
the second is the page number offset.

The layout presets provide common page layouts from typical scan methods.

The page order values are offsets relative to the start of a sequence of
scans. These offsets may also be negative to indicate the pages come from
the back of the book instead of the front.

The page order values also have an option decimal component that is
interpreted as an integer representing the number of 90 degree clockwise
rotations to apply to a page.

### Examples
A book scanned open and placed flat will have two pages visible in one
scanned image. Each scanned image is sequential from the last. So you
don't need to relate one scanned image to another. The page layout for this
is `[[1,2]]`. The first page is on the left side, the second page is on the
right.

A book scanned on a book-edge scanner will have scans with a single page
visible. But every other page will be rotated 180 degrees. The page order
with a rotation correction every other page would be `[[1],[2.2]]`.

A saddle stitched document like a manual can be unbound easily if it is
stapled. Each sheet can then be scanned flat to eliminate the gutter uplift.
When viewed from outside, the left side of each sheet contains pages from
the back of the book, the right from the front. Each side of the page also
contains one page from the front and back. Double sided scanning of each
sheet will result in two scan images with related pages. Starting with a scan
of the outer page the page order would be `[[-1,1],[2,-2]]`. The outside scan
containing the first page from the back and then front from left to right.
And following scan containing the second page from the front to the back
from left to right.

## Layout Presets

The default layout with no order or preset provided is simple sequential pages
with no other order changes.

The following presets are available with pre-defined page orders to simplify
usage.

- UNBOUND_SADDLE_STITCH : A saddle stitch book that has been unbound and scanned from the outside in.
- UNBOUND_DOUBLE_SIDED_SEQUENTIAL : The same as no preset, but specifically defined with related scans.
- FLAT_TWOPAGE : A bound book scanned while held open flat against a scan bed.
- FLAT_SINGLEPAGE : The default option for single sequential pages
- EDGE_ROTATE : A bound book scanned on a book-edge scanner that must be rotated every other page.


"""
        )

def main():
    """ Execute as a CLI and process parameters

    """
    # Generate CLI parameter options from enum
    page_layout_options=[]
    for layout in PageLayouts:
        page_layout_options.append(layout.name)

    # Setup CLI arguments
    parser = argparse.ArgumentParser(
                    prog="scan2pdf",
                    description='Scanning post processing utility',
                    epilog='NOTE: Put filenames as last parameter')
    parser.add_argument('-p', '--page-order', help="List of page order offsets to process", type=json.loads, default=[1])
    parser.add_argument('-l', '--layout-preset', help="Use predefined page order preset", choices=page_layout_options, default=None)
    parser.add_argument('-c', '--prefix-cover', help="Add cover image before other images without processing", default=None)
    parser.add_argument('-z', '--postfix-cover', help="Add cover image after other images without processing", default=None)
    parser.add_argument('-H', '--help-detailed', help="More detailed help", action='store_true')
    parser.add_argument('-r', '--rotate', help="Image rotation", type=int, default=0)
    parser.add_argument('-o', '--ocr', help="OCR final output", action='store_true')
    parser.add_argument('-n', '--name', help="Output filename", default="output.pdf")
    parser.add_argument('-b', '--black', help="Black level float percentage", type=float, default=0)
    parser.add_argument('-w', '--white', help="White level float percentage", type=float, default=1)
    parser.add_argument('-g', '--gamma', help="Gamma level float percentage", type=float, default=1)
    parser.add_argument('-x', '--grayscale', help="Set output to grayscale", action='store_true')
    parser.add_argument('-e', '--export-dir', help="Export pages to JPGs in given output directory", default=None)
    parser.add_argument('-s', '--shrink', help="Inner page shrink in pixels for folded binding", type=int, default=0)
    parser.add_argument('-m', '--margin-crop', help="Inset in pixels from edge to crop margins of scan, an array as [left,right,top,bottom]", type=json.loads, default=[0,0,0,0])
    parser.add_argument('-T', '--title', help="Set document title (place multiple words in quotes)", default="")
    parser.add_argument('-J', '--jpeg-quality', help="Adjust  JPEG  quality  level  for JPEG optimization. 100 is best quality and largest output size; 1 is lowest quality and smallest output; 0 uses the default.", type=int, default=0)
    parser.add_argument('-D', '--deskew', help="Attempt deskew in OCR stage to correct rotation of scans", type=bool, default=False)
    parser.add_argument('-O', '--optimize', help="Control how PDF is optimized after processing:0 - do not optimize; 1 - do safe, lossless  optimizations  (de‐fault); 2 - do some lossy optimizations; 3 - do aggressive lossy optimizations (including lossy JBIG2)", type=int, default=0)
    parser.add_argument('filenames', help="", default=None, nargs=argparse.REMAINDER)
    args = parser.parse_args()

    # Print detailed help and exit
    if args.help_detailed:
        help_detailed()
        sys.exit(0)

    # Find layout preset if provided
    if args.layout_preset.upper() in PageLayouts.__members__:
        page_layout = PageLayouts[args.layout_preset.upper()].value
    else:
        page_layout = args.page_order

    # Determine the structure of scans based on page layout
    scan_sequence=1
    scans_per_page=1
    scan_start_offset=1
    scan_end_offset=0
    for i,valuei in enumerate(page_layout):
        # Convert to mult-dim list if not already
        if not isinstance(page_layout[i], list):
            page_layout=[page_layout]

        # Number of scans involved in each layout
        scan_sequence=len(page_layout)

        # Find maximum values for layout
        for j,valuej in enumerate(page_layout[i]):
            scans_per_page=len(page_layout[i])
            if int(page_layout[i][j]) > scan_start_offset:
                scan_start_offset = int(page_layout[i][j])
            if int(page_layout[i][j]) < scan_end_offset:
                scan_end_offset = int(page_layout[i][j])

    # Adjust page_index if front cover is provided
    prefix_offset=0
    if args.prefix_cover is not None:
        prefix_offset=1

    # Adjust page_end if front cover is provided
    postfix_offset=0
    if args.postfix_cover is not None:
        postfix_offset=1

    # Initialize position tracking for processing
    scan_index=0
    page_index=0+prefix_offset
    scan_count=len(args.filenames)
    page_end=len(args.filenames)*scans_per_page+1+prefix_offset

    print(f"scan_sequence : {scan_sequence}")
    print(f"scans_per_page : {scans_per_page}")
    print(f"scan_start_offset : {scan_start_offset}")
    print(f"scan_end_offset : {scan_end_offset}")
    print(f"page_end : {page_end}")

    # Create array to hold all images
    imgs=[None]*(page_end-1+postfix_offset)

    # Add front cover
    if args.prefix_cover is not None:
        imgs[0]=sectionImage(
            args.prefix_cover,
            None,
            0
            )

    # Add rear cover
    if args.postfix_cover is not None:
        imgs[len(imgs)-1]=sectionImage(
            args.postfix_cover,
            None,
            len(imgs)-1
            )

    # Iterate over scans until all pages have been processed
    while page_index < page_end-1:
        # From page index process relates scans for page layout
        for i,valuei in enumerate(page_layout):
            for j,valuej in enumerate(page_layout[i]):

                # Determine if scan is half and what half it is
                half=None
                if scans_per_page != 1 :
                    if j :
                        half = "right"
                    else:
                        half = "left"
                # Determine page index from start or end
                if int(page_layout[i][j]) > 0:
                    page=page_index+int(page_layout[i][j])
                else:
                    page=page_end+int(page_layout[i][j])

                print(f"{args.filenames[scan_index+i]} : {page} : {half}")

                # Process scan and store image
                imgs[page-1]=sectionImage(
                    args.filenames[scan_index+i],
                    args,
                    page,
                    half,
                    int((scan_index/scan_count)*args.shrink),
                    ((page_layout[i][j]-int(page_layout[i][j]))*10)*90
                    )

        # Next process positions
        page_index+=scan_start_offset
        page_end+=scan_end_offset
        scan_index += scan_sequence

    # Store PDF of all images
    with Image() as pdf_out:
        for i,value in enumerate(imgs):
            pdf_out.sequence.append(value)
            imgs[i].destroy()
            imgs[i]=None
        pdf_out.save(filename=args.name)

    # OCR PDF
    if args.ocr:
        ocr(args.name,args.name,
            title=args.title,
            jpg_quality=args.jpeg_quality,
            deskew=args.deskew,
            optimize=args.optimize,
            force_ocr=True)

    print("Passed")
    sys.exit(0)



if __name__ == "__main__":
    main()
