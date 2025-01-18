This uses the [prototype branch](https://github.com/anchore/syft/compare/add-elf-note-dependencies) in syft to enumerate static dependencies described as ELF package notes.
The code here is to demo how to craft the notes artifact. To run the demo:

```
make
```

This will:
- create the build environment in a container
- build the application, statically linking in libs
- track the libs referenced and crafts the package notes, embedding into the elf binary
- the final binary is captured as a docker image
- runs syft (using the prototype branch) against the docker image / ELF binary to generate an SBOM
- visualizes the package relationships in the SBOM (saved as a png)

Some items of interest:
- `find_libs.py`: with the `-l` LD_FLAGS used as input, searches the build environment for the libs that these flags reference, and maps these back to debian packages. Outputs `libs.json` to show what was found.
- `make_notes.py`: takes `libs.json` as input and crafts the final package notes (as `notes.json`) to be written into the binary by another process.
- The `Makefile.build` has the command that bakes the notes into the binary:

```
objcopy --add-section .note.package=notes.json --set-section-flags .note.package=noload,readonly $(TARGET) /tmp/$(TARGET)
```
