#!/usr/bin/env python3

# Python System
import argparse
import sys
import os
import json
from pprint import pprint

# Externl System
# import imagemagick
from wand.image import Image

def sectionImage(path,args,page_number,half=None):

    outdir=""
    if args.export_dir is not None:
        outdir=str(args.export_dir)+"/"

        if not os.path.exists(outdir):
            os.makedirs(outdir)

    with Image(filename=path) as img:
        img.format = 'jpeg'
        img.level(args.black,args.white,args.gamma)
        img.rotate(args.rotate)
        if half=="left" :
            img.crop(0, 0, round(img.size[0]/2), img.size[1])
        if half=="right":
            img.crop(round(img.size[0]/2), 0, img.size[0], img.size[1])

        img.save(filename=outdir+str(page_number).zfill(4)+"_"+path.replace(".tiff", ".jpg"))


def main():
    """ Execute as a CLI and process parameters to rip and convert

    """

    # Usage Example
    # scan2pdf -p "[[1,4],[2,3]]" -r 90 -o -c "15%,90%,1.25" *.tiff

    # Setup CLI arguments
    parser = argparse.ArgumentParser(
                    prog="scan2pdf",
                    description='Scanning post processing utility',
                    epilog='NOTE: Put filenames as last parameter')
    parser.add_argument('-p', '--page-order', help="List of page order offsets to process", type=json.loads, default=[1])
    parser.add_argument('-r', '--rotate', help="Image rotation", type=int, default=None)
    parser.add_argument('-o', '--ocr', help="OCR final output", default=None)
    parser.add_argument('-b', '--black', help="Black level float percentage", type=float, default=0)
    parser.add_argument('-w', '--white', help="White level float percentage", type=float, default=1)
    parser.add_argument('-g', '--gamma', help="Gamma level float percentage", type=float, default=1)
    parser.add_argument('-e', '--export-dir', help="Color level process values", default=None)
    parser.add_argument('filenames', help="", default=None, nargs=argparse.REMAINDER)
    args = parser.parse_args()
    pprint(args)

    scan_sequence=1
    scans_per_page=1
    scan_start_offset=1
    scan_end_offset=0
    for i,valuei in enumerate(args.page_order):
        if isinstance(args.page_order[i], list):
            scan_sequence=len(args.page_order)

            for j,valuej in enumerate(args.page_order[i]):
                scans_per_page=len(args.page_order[i])
                if args.page_order[i][j] > scan_start_offset:
                    scan_start_offset = args.page_order[i][j]
                if args.page_order[i][j] < scan_end_offset:
                    scan_end_offset = args.page_order[i][j]
        else:
            scans_per_page=len(args.page_order)
            if args.page_order[i] > scan_start_offset:
                scan_start_offset = args.page_order[i]
            if args.page_order[i] < scan_end_offset:
                scan_end_offset = args.page_order[i]



    scan_index=0
    page_index=0
    page_end=len(args.filenames)*scans_per_page-1

    threads = []
    while page_index < page_end:

        for i,valuei in enumerate(args.page_order):
            if isinstance(args.page_order[i], list):
                for j,valuej in enumerate(args.page_order[i]):

                    half=None
                    if scans_per_page != 1 :
                        if j :
                            half = "right"
                        else:
                            half = "left"
                    if args.page_order[i][j] > 0:
                        page=page_index+args.page_order[i][j]
                    else:
                        page=page_end-args.page_order[i][j]

                    print(f"{args.filenames[scan_index+i]} : {page} : {half}")

                    sectionImage(args.filenames[scan_index+i],args,page,half)


            else:
                half=None
                if scans_per_page != 1:
                    if i :
                        half = "right"
                    else:
                        half = "left"
                if args.page_order[i] > 0:
                    page=page_index+args.page_order[i]
                else:
                    page=page_end-args.page_order[i]

                print(f"{args.filenames[scan_index]} : {page} : {half}")
                sectionImage(args.filenames[scan_index],args,page,half)

        page_index+=scan_start_offset
        page_end+=scan_end_offset
        #sectionImage(filename,args)

        scan_index += scan_sequence

    print("Passed")
    sys.exit(0)



if __name__ == "__main__":
    main()
