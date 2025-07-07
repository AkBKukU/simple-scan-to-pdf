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
from ocrmypdf import ocr

def sectionImage(path,args,page_number,half=None, shrink=0):

    outdir=""
    if args.export_dir is not None:
        outdir=str(args.export_dir)+"/"

        if not os.path.exists(outdir):
            os.makedirs(outdir)

    img = Image(filename=path)
    img.format = 'jpeg'
    img.level(args.black,args.white,args.gamma)
    img.rotate(args.rotate)
    if half=="left" :
        img.crop(shrink, 0, round(img.size[0]/2-shrink/2), img.size[1])
    if half=="right":
        img.crop(round(img.size[0]/2+shrink/2), 0, img.size[0], img.size[1])
    img.save(filename=outdir+str(page_number).zfill(4)+"_"+path.replace(".tiff", ".jpg"))
    return img


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
    parser.add_argument('-l', '--layout-preset', help="Use predefined page order preset", choices={"stapled-flat"}, default=None)
    parser.add_argument('-r', '--rotate', help="Image rotation", type=int, default=None)
    parser.add_argument('-o', '--ocr', help="OCR final output", default=None)
    parser.add_argument('-b', '--black', help="Black level float percentage", type=float, default=0)
    parser.add_argument('-w', '--white', help="White level float percentage", type=float, default=1)
    parser.add_argument('-g', '--gamma', help="Gamma level float percentage", type=float, default=1)
    parser.add_argument('-e', '--export-dir', help="Color level process values", default=None)
    parser.add_argument('-s', '--shrink', help="Inner page shrink in pixels for folded binding", type=int, default=0)
    parser.add_argument('-T', '--title', help="Set document title (place multiple words in quotes)", default="")
    parser.add_argument('-J', '--jpeg-quality', help="Adjust  JPEG  quality  level  for JPEG optimization. 100 is best quality and largest output size; 1 is lowest quality and smallest output; 0 uses the default.", type=int, default=0)
    parser.add_argument('-D', '--deskew', help="Attempt deskew in OCR stage to correct rotation of scans", type=bool, default=False)
    parser.add_argument('-O', '--optimize', help="Control how PDF is optimized after processing:0 - do not optimize; 1 - do safe, lossless  optimizations  (de‐fault); 2 - do some lossy optimizations; 3 - do aggressive lossy optimizations (including lossy JBIG2)", type=int, default=0)
    parser.add_argument('filenames', help="", default=None, nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.layout_preset == "stapled-flat":
        page_layout = [[-1,1],[2,-2]]
    else:
        page_layout = args.page_order

    scan_sequence=1
    scans_per_page=1
    scan_start_offset=1
    scan_end_offset=0
    for i,valuei in enumerate(page_layout):
        if isinstance(page_layout[i], list):
            scan_sequence=len(page_layout)

            for j,valuej in enumerate(page_layout[i]):
                scans_per_page=len(page_layout[i])
                if page_layout[i][j] > scan_start_offset:
                    scan_start_offset = page_layout[i][j]
                if page_layout[i][j] < scan_end_offset:
                    scan_end_offset = page_layout[i][j]
        else:
            scans_per_page=len(page_layout)
            if page_layout[i] > scan_start_offset:
                scan_start_offset = page_layout[i]
            if page_layout[i] < scan_end_offset:
                scan_end_offset = page_layout[i]


    scan_index=0
    page_index=0
    scan_count=len(args.filenames)
    page_end=len(args.filenames)*scans_per_page+1

    print(f"scan_sequence : {scan_sequence}")
    print(f"scans_per_page : {scans_per_page}")
    print(f"scan_start_offset : {scan_start_offset}")
    print(f"scan_end_offset : {scan_end_offset}")
    print(f"page_end : {page_end}")

    imgs=[None]*(page_end-1)

    while page_index < page_end-1:


        for i,valuei in enumerate(page_layout):
            if isinstance(page_layout[i], list):
                for j,valuej in enumerate(page_layout[i]):

                    half=None
                    if scans_per_page != 1 :
                        if j :
                            half = "right"
                        else:
                            half = "left"
                    if page_layout[i][j] > 0:
                        page=page_index+page_layout[i][j]
                    else:
                        page=page_end+page_layout[i][j]

                    print(f"{args.filenames[scan_index+i]} : {page} : {half}")

                    imgs[page-1]=sectionImage(args.filenames[scan_index+i],args,page,half,int((scan_index/scan_count)*args.shrink))


            else:
                half=None
                if scans_per_page != 1:
                    if i :
                        half = "right"
                    else:
                        half = "left"
                if page_layout[i] > 0:
                    page=page_index+page_layout[i]
                else:
                    page=page_end+page_layout[i]

                print(f"{args.filenames[scan_index]} : {page} : {half}")
                imgs[page-1]=sectionImage(args.filenames[scan_index],args,page,half,int((scan_index/scan_count)*args.shrink))

        page_index+=scan_start_offset
        page_end+=scan_end_offset
        sectionImage(filename,args)

        scan_index += scan_sequence
    with Image() as pdf_out:
        for i,value in enumerate(imgs):
            pdf_out.sequence.append(value)
            imgs[i].destroy()
            imgs[i]=None
        pdf_out.save(filename='series.pdf')
    ocr('series.pdf',"ocr.pdf",
        title=args.title,
        jpg_quality=args.jpeg_quality,
        deskew=args.deskew,
        optimize=args.optimize)

    print("Passed")
    sys.exit(0)



if __name__ == "__main__":
    main()
