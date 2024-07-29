# PDFlib

*2024-07-29 bwilson I turned this off because it's not working with profiles,
and I did not want my password stored in plaintext.

It's pretty low priority anyway.*

Check for missing PDFlib files
to avoid having broken links in webmaps.


## Backstory:

Cartographers generate taxmaps as PDF files as a matter of public record.
We make them available via hyperlinks from maps. That means from time to time
there is a link that points nowhere.

## How it works

1. Build a list of needed files from taxlots GIS layer
2. See if the referenced taxmap files exist
3. List any that are missing

## Deployment

### Profile

For Linux I switched to using profiles insteand of a plaintext password. To do this, 
I had to install packages at the system level.
Then I used the "keyring" app (part of python3-keyring) to create my profile called "delta".
I copied the existing .arcgisprofile file from my Desktop to avoid messing about with having
to also run the arcgis API module.

```bash
sudo apt install python3-dbus # was already installed
sudo apt install python3-keyring
keyring set cc-testmaps delta
```

### Script

Copy check_pdflib.* from the source folder to the user bin folder and then
set it to run as from crontab each morning. Cron will 
automatically email output to me.

The automounter is not working right now, so the file server is
mounted at /media/GIS from /etc/fstab.  That's defined in the same
environment under PDFLIB.