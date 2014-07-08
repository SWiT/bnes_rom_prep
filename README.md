bnes_rom_prep
=============

A script to prepare ROMs for Beagle SNES.  It compresses any rom files ending in smc using gzip. It resizes and assigns cover images from a folder containing a "SNES Cover Collection". It fetches some information from Wikipedia like the year, genre, and alternate titles.  Finally, it generates the games.xml file for any roms in the Beagle SNES "rom" subfolder.

Instructions:
You will want to change romspath, imagespath, coverspath, and outputxmlfile at the top of bsnes_rom_prep.py to point the proper locations.

python bnes_rom_prep.py
