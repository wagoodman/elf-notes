#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gd.h>
#include <gdfontg.h>  // Added for giant font
#include <zlib.h>

#define CHUNK 16384

// Function to compress a file using zlib
int compress_file(const char *source, const char *dest) {
    FILE *source_file = fopen(source, "rb");
    FILE *dest_file = fopen(dest, "wb");

    if (!source_file || !dest_file) {
        printf("Error opening files\n");
        return -1;
    }

    unsigned char in[CHUNK];
    unsigned char out[CHUNK];
    z_stream strm;

    strm.zalloc = Z_NULL;
    strm.zfree = Z_NULL;
    strm.opaque = Z_NULL;

    if (deflateInit(&strm, Z_DEFAULT_COMPRESSION) != Z_OK) {
        return -1;
    }

    int ret;
    do {
        strm.avail_in = fread(in, 1, CHUNK, source_file);
        if (ferror(source_file)) {
            deflateEnd(&strm);
            return -1;
        }

        if (strm.avail_in == 0)
            break;

        strm.next_in = in;
        do {
            strm.avail_out = CHUNK;
            strm.next_out = out;

            ret = deflate(&strm, Z_NO_FLUSH);

            unsigned have = CHUNK - strm.avail_out;
            if (fwrite(out, 1, have, dest_file) != have || ferror(dest_file)) {
                deflateEnd(&strm);
                return -1;
            }
        } while (strm.avail_out == 0);
    } while (ret != Z_STREAM_END);

    deflateEnd(&strm);
    fclose(source_file);
    fclose(dest_file);
    return 0;
}

int main(void) {  // Changed signature to void since we don't use args
    // Create a new image
    gdImagePtr im;
    FILE *output_file;
    int width = 400;
    int height = 300;

    im = gdImageCreate(width, height);

    // Set up colors
    int background = gdImageColorAllocate(im, 255, 255, 255);  // white
    int text_color = gdImageColorAllocate(im, 0, 0, 0);        // black
    int red = gdImageColorAllocate(im, 255, 0, 0);
    int blue = gdImageColorAllocate(im, 0, 0, 255);

    // Draw some shapes
    gdImageFilledRectangle(im, 50, 50, 350, 250, blue);
    gdImageFilledEllipse(im, 200, 150, 100, 100, red);

    // Fill the background of the text area
    gdImageFilledRectangle(im, 155, 135, 245, 165, background);

    // Write text
    char *text = "Hello, GD!";
    gdImageString(im, gdFontGetGiant(), 160, 140, (unsigned char*)text, text_color);

    // Save the image
    output_file = fopen("/output/output.png", "wb");
    if (output_file == NULL) {
        fprintf(stderr, "Error creating output file\n");
        return 1;
    }

    gdImagePng(im, output_file);
    fclose(output_file);
    gdImageDestroy(im);

    // Compress the generated image
    printf("Compressing image...\n");
    if (compress_file("/output/output.png", "/output/output.png.gz") == 0) {
        printf("Successfully created and compressed image!\n");
    } else {
        printf("Error during compression\n");
        return 1;
    }

    return 0;
}
