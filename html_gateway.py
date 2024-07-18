import sys
import os
import requests
import shutil

class HTMLGateway:
    
    @staticmethod
    def fetch(url):
        # Okay, I understand that I am not using good certs. Thanks for the warning.
        requests.packages.urllib3.disable_warnings()

        try:
            res = requests.get(url, timeout=30)
        except requests.Timeout:
            raise HTMLGatewayError("Timeout error '%s'" % url)
        except requests.RequestException:
            raise HTMLGatewayError("Request Exception '%s' : %s" % (url, requests.RequestException))
        except Exception as e:
            raise HTMLGatewayError("Timeout error '%s' : %s" % url, e)

        if res.status_code != 200:
            raise HTMLGatewayError("Website '%s' returned status code %s" % (url, res.status_code))

        return res.text

    @staticmethod
    def stream(url):
        # Okay, I understand that I am not using good certs. Thanks for the warning.
        requests.packages.urllib3.disable_warnings()
        data = requests.get(url, stream=True, verify=False)
        data.raise_for_status()
        return data

class HTMLGatewayError(Exception):
    pass

if __name__ == "__main__":
    # unit tests

    # Attempt to download the GTFS home page
    bad_url  = "https://co.clatsop.or.us/this_should_fail.html"
    good_url = "https://oregon-gtfs.com/"
    zip_url = "https://oregon-gtfs.com/gtfs_data/benton-or-us/benton-or-us.zip"

    with HTMLGateway.stream(zip_url) as data:
        assert(data.status_code == 200)

    try:
        data = HTMLGateway.fetch(bad_url)
        sys.exit("Test failed, download of bad url.")
    except HTMLGatewayError as e:
        pass

    data = HTMLGateway.fetch(good_url)
    assert(len(data)!=0)

    