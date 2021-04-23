import os
class Config(object):

    site = "https://oregon-gtfs.com/"
    sourcedir = "K:/Social_Services/Transit/"
    cwd = os.getcwd()
    spatial_ref_file = os.path.join(cwd, 'WGS 1984.prj')

if __name__ == "__main__":
    assert type(Config.sourcedir) == type("")
    assert(os.path.exists(Config.spatial_ref_file))

