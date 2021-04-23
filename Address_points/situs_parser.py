# situs_parser.poly_to_point
# 
# This is code that I wrote when I was trying to pull
# together address data from different sources
#
# I needed to convert a situs_address field in taxlots_accounts into separate fields
#
# 2021-04-22 bwilson
# 
import re

re_housenum = re.compile(r'(\d[\d\-\s]*)([ABCD]?)\s+(.*)')
re_predirection = re.compile(r'^\s*(SE|NE|NW|SW|N|E|S|W)\s+(.*)$') # put longer strings first
# Seaside's "AVENUE S|W|N|E" confuses the postdirection handler so it's a special case
re_special_streets = re.compile(r'^(.*)\s*(AVENUE\s+[EWSN])\s*')
# There is one entry with "Ave." so I handle it and drop it.
re_streettype = re.compile(r'(.*)\s+(LP|LOOP|LN|LANE|RD|DR|AVE|PL|WAY|CT|ST|BLVD|CIRCLE|CIR|TER)\.?$', re.IGNORECASE)
#str = "MAIN ST NW"
re_postdirection = re.compile(r'(.*)\s+(SE|NE|NW|SW|N|E|S|W)$') # put longer strings first
# There is ONE property that uses a $ separator instead of #
re_unit = re.compile(r'(.*)\s+[\$#](.*)')

def split_situs(situs):
    """ Situs address in, separate fields out, in a tuple. """
    rval = False
    house_num = ''
    house_suffix = ''
    pre_direction = ''
    street = ''
    street_type = ''
    unit_num = ''
    post_direction = ''

    mo = re_housenum.search(situs)
    if mo:
        house_num = mo.group(1).replace(' ', '').strip('-')
        house_suffix = mo.group(2)
        situs = mo.group(3)
        rval = True

    mo = re_unit.search(situs)
    if mo:
        situs = mo.group(1)
        unit_num = mo.group(2).replace(' ', '')
        rval = True

    mo = re_special_streets.search(situs)
    if mo:
        situs = mo.group(1)
        street = mo.group(2)
        rval = True

    mo = re_postdirection.search(situs)
    if mo:
        situs = mo.group(1)
        post_direction = mo.group(2)
        rval = True

    mo = re_predirection.search(situs)
    if mo:
        pre_direction = mo.group(1)
        situs = mo.group(2)
        rval = True

    mo = re_streettype.search(situs)
    if mo:
        street = mo.group(1)
        street_type = mo.group(2)
        rval = True
    else:
        if not street: 
            street = situs
            if street: rval = True

    # Special case handler for "E ST", "W ST", etc.
    if pre_direction and not street:
        street = pre_direction
        pre_direction = ''

    # Special case: replace "Highway" with "Hwy", fixing multiple spaces and case.
    street = re.sub(r'Highway\s+', 'Hwy ', street, flags=re.IGNORECASE)

    return (rval, house_num, house_suffix, pre_direction, street, street_type, post_direction, unit_num)


def situs_to_fields(row):
    """ This is called from a Pandas dataframe "apply". 
    It takes situs from a row as a dictionary 
    and produces separate columns for each field, street, housenum and so on. """

    situs = row['SITUS_ADDR']
    if situs:
        (rval, house_num, house_suffix, predirection, street, street_type, postdirection, unit) = split_situs(situs)
        if rval:
            row['HOUSE_NUM'] = house_num
            row['HOUSE_SUFFIX'] = house_suffix
            row['PRE_DIRECTION'] = predirection
            row['STREET_NAME'] = street
            row['STREET_TYPE'] = street_type
            row['POST_DIRECTION'] = postdirection
            row['UNIT_NUM'] = unit
    return row

def combine_fields_to_situs(row):
    """ This is called from a Pandas dataframe "apply".
    It takes a row as a dictionary in and returns a situs address. """

    # Complicated way to get rid of ".0" at the end of the output string
    try:
        housenum = "%d" % int(row['HOUSE_NUM'])
    except:
        housenum = "%s" % row['HOUSE_NUM']
    row['HOUSE_NUM'] = housenum

    situs = ' '.join(filter(None, [
                            row['HOUSE_NUM'], row['HOUSE_SUFFIX'], row['PRE_DIRECTION'], 
                            row['STREET_NAME'], row['STREET_TYPE'], row['POST_DIRECTION'], 
                            row['UNIT_TYPE'], str(row['UNIT_NUM'])
    ]))
    row['SITUS_ADDR'] = situs
    return row

def test_split_situs():
    cases = [
        'SADDLE MOUNTAIN STATE PARK',
        'Port',
        'WH Pier 2',
        'Alt Hwy 101',
        '120-124-126 N Hemlock St N', # I wonder how this will turn out.
        '100 Highway    53',
        '100 Alt Highway 101 Business #123',
        'PALLISADES CONDOMINUM #123',
        '101 A E MAIN ST #123',
        '101 A E MAIN ST E #123',
        '101A MAIN ST #123',
        '101 - 102 MAIN ST #123',
        '101 - 102 MAIN ST $123',
        '101 A MAIN ST #123',
        'AVENUE E #123',
        '3621 S Hemlock (Sea Colony Condos) St #7',
    ]
    for case in cases:
        a = split_situs(case)
        print(case, ' ::', a)

if __name__ == "__main__":
    test_split_situs()



