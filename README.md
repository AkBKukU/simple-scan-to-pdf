# Scan2Pdf

This is a simple script that wraps some image processing for scans.

## Dependencies

From pip:

- wand
- ocrmypdf

This heavily relies on ImageMagick and you will likely need to modify the policy file at `/etc/ImageMagick-*/policy.xml` to increase the values of the following lines:

    <policy domain="resource" name="memory" value="4096MiB"/>
    <policy domain="resource" name="disk" value="20GiB"/>


## Common Usage Examples

### ADF Single Pages

This assumes you will have a folder of `tiff` files named sequentially that are already cropped to the content. This would have only one page in each scan.

    scan2pdf.py --name output_file.pdf \
        --title "The Title of the PDF File" \
        --ocr \
        --grayscale \
        *.tiff

### Bound Book on Flatbed Scanner

This assumes you will have a folder of `tiff` files named sequentially that are already cropped to the exact size of the book's pages. There would be two pages visible per scan and the book was rotated 90 degrees to fit on the scanner. Inside the book was only text that would be better off as grayscale and OCR'ed.

The cover scans would be placed in a sub-folder and name accordingly.

    scan2pdf.py --name output_file.pdf \
        --title "The Title of the PDF File" \
        --layout-preset FLAT_TWOPAGE \
        --prefix-cover covers/front.tiff \
        --postfix-cover covers/back.tiff \
        --ocr \
        --grayscale \
        --rotate 90 \
        *.tiff


## Help

        $ ./scan2pdf.py -h
        usage: scan2pdf [-h] [-p PAGE_ORDER]
                        [-l {UNBOUND_SADDLE_STITCH,UNBOUND_DOUBLE_SIDED_SEQUENTIAL,FLAT_TWOPAGE,FLAT_SINGLEPAGE,EDGE_ROTATE}]
                        [-c PREFIX_COVER] [-z POSTFIX_COVER] [-H] [-f] [-r ROTATE]
                        [-t TRIM] [-o] [-n NAME] [-b BLACK] [-w WHITE] [-g GAMMA] [-x]
                        [-e EXPORT_DIR] [-s SHRINK] [-m MARGIN_CROP] [-T TITLE]
                        [-J JPEG_QUALITY] [-D DESKEW] [-O OPTIMIZE]
                        ...

        Scanning post processing utility

        positional arguments:
        filenames

        options:
        -h, --help            show this help message and exit
        -p PAGE_ORDER, --page-order PAGE_ORDER
                                List of page order offsets to process
        -l {UNBOUND_SADDLE_STITCH,UNBOUND_DOUBLE_SIDED_SEQUENTIAL,FLAT_TWOPAGE,FLAT_SINGLEPAGE,EDGE_ROTATE}, --layout-preset {UNBOUND_SADDLE_STITCH,UNBOUND_DOUBLE_SIDED_SEQUENTIAL,FLAT_TWOPAGE,FLAT_SINGLEPAGE,EDGE_ROTATE}
                                Use predefined page order preset
        -c PREFIX_COVER, --prefix-cover PREFIX_COVER
                                Add cover image before other images without processing
        -z POSTFIX_COVER, --postfix-cover POSTFIX_COVER
                                Add cover image after other images without processing
        -H, --help-detailed   More detailed help
        -f, --stack-flip      Process pages in order of stack flipped in single
                                sided ADF
        -r ROTATE, --rotate ROTATE
                                Image rotation
        -t TRIM, --trim TRIM  Automatically trim image with fuzz float percentage
                                based on top left pixel
        -o, --ocr             OCR final output
        -n NAME, --name NAME  Output filename
        -b BLACK, --black BLACK
                                Black level float percentage
        -w WHITE, --white WHITE
                                White level float percentage
        -g GAMMA, --gamma GAMMA
                                Gamma level float percentage
        -x, --grayscale       Set output to grayscale
        -e EXPORT_DIR, --export-dir EXPORT_DIR
                                Export pages to JPGs in given output directory
        -s SHRINK, --shrink SHRINK
                                Inner page shrink in pixels for folded binding
        -m MARGIN_CROP, --margin-crop MARGIN_CROP
                                Inset in pixels from edge to crop margins of scan, an
                                array as [left,right,top,bottom]
        -T TITLE, --title TITLE
                                Set document title (place multiple words in quotes)
        -J JPEG_QUALITY, --jpeg-quality JPEG_QUALITY
                                Adjust JPEG quality level for JPEG optimization. 100
                                is best quality and largest output size; 1 is lowest
                                quality and smallest output; 0 uses the default.
        -D DESKEW, --deskew DESKEW
                                Attempt deskew in OCR stage to correct rotation of
                                scans
        -O OPTIMIZE, --optimize OPTIMIZE
                                Control how PDF is optimized after processing:0 - do
                                not optimize; 1 - do safe, lossless optimizations
                                (de‐fault); 2 - do some lossy optimizations; 3 - do
                                aggressive lossy optimizations (including lossy JBIG2)

        NOTE: Put filenames as last parameter


## Process Order

The following is the order that process operations are applied:

1. Margin Crop
2. Trim
3. Color Leveling (Black, White, Gamma)
4. Rotation
5. Grayscale
6. Page Isolation Cropping
7. Page Order Rotation

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
