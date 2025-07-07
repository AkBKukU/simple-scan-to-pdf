# Scan2Pdf

This is a simple script that wraps some image processing for scans.

## Dependencies

From pip:

- wand
- ocrmypdf

## Help

    $ ./scan2pdf.py -h
    usage: scan2pdf [-h] [-p PAGE_ORDER] [-l {stapled-flat}] [-r ROTATE] [-o]
                    [-n NAME] [-b BLACK] [-w WHITE] [-g GAMMA] [-e EXPORT_DIR]
                    [-s SHRINK] [-T TITLE] [-J JPEG_QUALITY] [-D DESKEW]
                    [-O OPTIMIZE]
                    ...

    Scanning post processing utility

    positional arguments:
      filenames

    options:
      -h, --help            show this help message and exit
      -p, --page-order PAGE_ORDER
                            List of page order offsets to process
      -l, --layout-preset {stapled-flat}
                            Use predefined page order preset
      -r, --rotate ROTATE   Image rotation
      -o, --ocr             OCR final output
      -n, --name NAME       Output filename
      -b, --black BLACK     Black level float percentage
      -w, --white WHITE     White level float percentage
      -g, --gamma GAMMA     Gamma level float percentage
      -e, --export-dir EXPORT_DIR
                            Export pages to JPGs in given output directory
      -s, --shrink SHRINK   Inner page shrink in pixels for folded binding
      -T, --title TITLE     Set document title (place multiple words in quotes)
      -J, --jpeg-quality JPEG_QUALITY
                            Adjust JPEG quality level for JPEG optimization. 100
                            is best quality and largest output size; 1 is lowest
                            quality and smallest output; 0 uses the default.
      -D, --deskew DESKEW   Attempt deskew in OCR stage to correct rotation of
                            scans
      -O, --optimize OPTIMIZE
                            Control how PDF is optimized after processing:0 - do
                            not optimize; 1 - do safe, lossless optimizations
                            (de‐fault); 2 - do some lossy optimizations; 3 - do
                            aggressive lossy optimizations (including lossy JBIG2)

    NOTE: Put filenames as last parameter

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
