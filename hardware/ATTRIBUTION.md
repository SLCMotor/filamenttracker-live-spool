# Printable Hardware Attribution

## Original design

- **Author:** MartinNYHC (Martin Ziegler)
- **Project:** SpoolBuddy enclosure
- **MakerWorld source:** [SpoolBuddy model 2296982](https://makerworld.com/en/models/2296982-spoolbuddy)
- **Official project:** [Bambuddy / SpoolBuddy](https://github.com/maziggy/bambuddy)
- **Official build documentation:** [SpoolBuddy Assembly Guide](https://wiki.bambuddy.cool/spoolbuddy/assembly/)
- **License:** [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)

MakerWorld identifies MartinNYHC as the design creator and the model license as
Creative Commons Attribution (`BY`). The AGPL-3.0 license used by the Bambuddy
software repository does not govern the Live Spool software or replace the CAD
model's Creative Commons license.

## FilamentTracker Live Spool modifications

The STL geometry in this repository is a modified version prepared for the
FilamentTracker Live Spool hardware platform. The 3MF print project packages
that derivative geometry with print-plate and slicer configuration.

Changes from the original enclosure include:

- replaced the original branding with the Live Spool logo
- increased the main enclosure's internal dimensions for wiring and electronics
- raised the touchscreen position for Raspberry Pi 5 active-cooler clearance
- increased clearance for NVMe/SSD HATs and future expansion hardware
- opened the rear section of the display cover for airflow and larger hardware
- refined the enclosure for the FilamentTracker Live Spool component layout

These changes are identified as modifications and are not endorsed by or
affiliated with the original SpoolBuddy project.

## Scope

This attribution and the CC BY 4.0 license apply only to the derivative
printable enclosure files in `hardware/printable/`. FilamentTracker Live Spool's
independently developed software remains under the repository's MIT License.
