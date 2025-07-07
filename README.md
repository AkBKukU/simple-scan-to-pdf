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
