# FilamentTracker Live Spool Hardware

This directory contains the build documentation and printable enclosure for a
FilamentTracker Live Spool appliance. Start with the bill of materials, follow
the wiring and assembly guides, and calibrate the completed scale before use.

## Hardware documentation

1. [Bill of Materials](docs/01_Bill_of_Materials.pdf)
2. [Wiring Diagram](docs/02_Wiring_Diagram.png)
3. [Assembly Guide](docs/03_Assembly_Guide.png)
4. [Print Plates](docs/04_Print_Plates.png)
5. [Calibration Guide](docs/05_Calibration_Guide.pdf)

The wiring, assembly, and print-plate guides are high-resolution images so they
can be viewed directly on GitHub or saved for reference at the workbench.

## Printable files

- [FilamentTracker_Live_Spool.3mf](printable/FilamentTracker_Live_Spool.3mf) —
  recommended multi-plate print project with slicer settings and part placement
- [FilamentTracker_Live_Spool_STL.zip](printable/FilamentTracker_Live_Spool_STL.zip) —
  STL package for OrcaSlicer, PrusaSlicer, Cura, and other slicers
- [FilamentTracker_Live_Spool.stl](printable/FilamentTracker_Live_Spool.stl) —
  unpacked STL supplied for convenient direct import

PETG is recommended for the finished appliance. Review the print-plate guide
and confirm the selected printer, material, and support settings before slicing.

## Build sequence

1. Obtain the components and fasteners in the bill of materials.
2. Print the enclosure from the recommended 3MF project or import the STL.
3. Assemble the enclosure without powering the Raspberry Pi.
4. Wire the PN532, scale ADC, and load cell using the wiring guide.
5. Check every supply voltage and connection before applying power.
6. Install Live Spool using the repository's main installation instructions.
7. Complete tare and calibration using the calibration guide.

Load-cell wire colors and breakout-board voltage requirements are not
universal. Verify the markings and datasheets for the exact parts being used.

## Attribution and licensing

The Live Spool software, wiring documentation, and original project
documentation are licensed separately from the printable enclosure.

The printable enclosure is a modified derivative of the SpoolBuddy enclosure
by MartinNYHC and is distributed under the Creative Commons Attribution 4.0
International license. See [Attribution](ATTRIBUTION.md) and the
[printable-file license notice](printable/LICENSE.md).
