import os

from html_gateway import HTMLGateway
from bs4 import BeautifulSoup
import json
from datetime import datetime
from glob import glob
import shutil
import zipfile

verbose = False

class GTFSdownloader(object):

    @staticmethod
    def get_table(site):
        """ Scrapes the datatable from the front page of the website """

        raw_data = HTMLGateway.fetch(site)

        # Find the first table in the page.
        soup = BeautifulSoup(raw_data, features="lxml")
        rows = soup.find_all('tr')

        keys = []
        table = []

        for row in rows:
            headers = row.findAll('th')
            if headers:
                for item in headers:
                    try:
                        keys.append(item.get_text().strip())
                    except Exception as e:
                        pass
            else:
                values = {}
                columns = row.findAll('td')
                if len(columns) != len(keys):
                    continue
                for i in range(0,len(keys)):
                    values[keys[i]] = columns[i].get_text().strip()

                table.append(values)

        return table

    @staticmethod
    def download_zip(url, targetdir, updated):
        result = False
        (urlpart,fname) = os.path.split(url)
        local_filename = os.path.join(targetdir, fname)

        overwrite = False
        agencytxt = os.path.join(targetdir, 'agency.txt')
        current = None
        if os.path.exists(agencytxt):
            current_time = os.stat(agencytxt).st_ctime
            current = datetime.fromtimestamp(current_time)

        if not updated or not current or (current < updated):
            print("Time to get a new copy for \"%s\"" % targetdir)
            overwrite = True

        if overwrite or not os.path.exists(local_filename):
            if verbose: print("Downloading \"%s\" to \"%s\"." % (url, targetdir))

            try:
                with HTMLGateway.stream(url) as data:
                    if not os.path.exists(targetdir): os.mkdir(targetdir)
                    with open(local_filename, 'wb') as fp:
                        shutil.copyfileobj(data.raw, fp)
                    result = True
            except Exception as e:
                print("Download failed. %s" % e)
    #    elif verbose:
    #        print("Already have \"%s\", skipping download." % local_filename)

        return result 

    @staticmethod
    def unpack(zippath):
        assert(zippath != '')
        (path,name) = os.path.split(zippath)
        (source,ext) = os.path.splitext(name)
        targetpath = path
        result = False
        try:
            with zipfile.ZipFile(zippath, 'r') as zip_fp:
                zip_fp.extractall(targetpath)
            result = True
        except Exception as e:
            print("Unzip failed for \"%s\", %s" % (zippath, e))
        return result

if __name__ == "__main__":

    from config import Config

    verbose = True

    table = GTFSdownloader.get_table(Config.site)
    j = json.dumps(table, sort_keys=True, indent=4)
    print(j)

    # Check expiration date on data and delete any that are past the "use by" date.

    print("---Download any missing or outdated files---")

    for d in table:
        agency = d['Transit service']
        assert(agency != '')

        updated = None
        updatestr = d['Last Modified']
        if updatestr :
            updated = datetime.strptime(updatestr, "%Y-%b-%d")
 
        expire = None
        expirestr = d['Valid Until']
        if expirestr:
            expire = datetime.strptime(expirestr, "%Y-%b-%d")

        url = d['Download Link']
        targetdir = os.path.join(Config.sourcedir, agency)
        GTFSdownloader.download_zip(url, targetdir, updated)

    print("---Unpacking as needed---")
    for source in glob(Config.sourcedir + '*/*.zip', recursive=False):
        if verbose: print("Unpacking \"%s\"" % source)
        GTFSdownloader.unpack(source)

