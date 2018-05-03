#!/usr/bin/env python
import datetime
import os
import shutil
import argparse
from sys import argv, exit
try:
    import exifread
    exif_read = True
except:
    print "Please install exifread for better performance."
    exif_read = False

def timestamp2datetime(timestamp, convert_to_local=False):
    ''' Converts UNIX timestamp to a datetime object. '''
    if isinstance(timestamp, (int, long, float)):
        dt = datetime.datetime.utcfromtimestamp(timestamp)
        if convert_to_local:
            dt = dt + datetime.timedelta(hours=8)
        return dt
    return timestamp


def datetime2timestamp(dt, convert_to_utc=False):
    ''' Converts a datetime object to UNIX timestamp in milliseconds. '''
    if isinstance(dt, datetime.datetime):
        if convert_to_utc:
            dt = dt + datetime.timedelta(hours=-8)
        timestamp = total_seconds(dt - EPOCH)
        return long(timestamp)
    return dt


def _sort_file(filename, dir_format):
    crt_date = timestamp2datetime(os.path.getctime(filename))
    print "Found image %s created at %s ..." % (filename, crt_date.strftime("%Y-%m-%d"))
    dirname = os.path.dirname(filename)
    move_to = os.path.join(dirname, crt_date.strftime(dir_format))
    if not os.path.exists(move_to):
        os.mkdir(move_to)

    dest_file = os.path.join(move_to, os.path.basename(filename))

    if not os.path.exists(dest_file):
        shutil.move(filename, dest_file)

def _save_file(filename, dest, dir_format):
    # _show(filename)
    basename = os.path.basename(filename)
    if not exif_read:
        crt_date = timestamp2datetime(os.path.getctime(filename))
    else:
        try:
            with open(filename, 'rb') as f:
            # Return Exif tags
                tags = exifread.process_file(f)
                crt_date = datetime.datetime.strptime(str(tags["EXIF DateTimeOriginal"]), '%Y:%m:%d %H:%M:%S')
        except KeyError:
            print "No exif info for file " , basename, ', not a photo file.'
            return

    subdir = crt_date.strftime(dir_format)

    if os.path.exists(os.path.join(dest, subdir, basename)):
        print "File %s existed, skipped." % basename
        return False

    try:
        if not os.path.exists(os.path.join(dest, subdir)):
            os.mkdir(os.path.join(dest, subdir))

        shutil.copy(filename, os.path.join(dest, subdir, basename))

        return True
    except:
        print "Import file '%s' failed." % basename
        return False

def sort_photos(src_dir, dir_format="%Y-%m"):
    src_dir = os.path.abspath(src_dir)
    print "Search photos on", src_dir, '...'
    count = 0
    for (root, dir, files) in os.walk(src_dir):
        if root != src_dir:
            break
        for file in files:
            if ".jpg" in file.lower():
                _sort_file(os.path.join(root, file), dir_format)
                count += 1
    print "Done, %d files sorted." % count

def _show(filename, **options):
    # override me, as necessary
    # Open windows Image Preview to preview image
    import subprocess
    subprocess.Popen('rundll32.exe shimgvw.dll,ImageView_Fullscreen '+filename)

def import_photos(src, dest, dir_format="%Y-%m"):
    count = 0
    for (root, dir, files) in os.walk(src):
        for file in files:
            if ".jpg" in file.lower():
                if _save_file(os.path.join(root, file), dest, dir_format):
                    count += 1

                if count > 0 and count % 50 == 0:
                    print "%d files imported." % count
    print "Done, %d files imported." % count

if __name__ == "__main__":
    prog_name = os.path.basename(argv[0])
    USAGE = "Usage: %s sort <target directory> \n" \
            "       %s import <source directory> <target directory> -- import all files from source to target diectory." % (prog_name, prog_name)
    if len(argv) < 2 or '-h' in argv[1]:
        exit(USAGE)

    action = argv[1]

    if action == "sort":
        if len(argv) < 3:
            exit(USAGE)
        src_dir = argv[2]
        sort_photos(src_dir)
    elif action == "import":
        if len(argv) < 4:
            exit(USAGE)

        src_dir = argv[2]
        dest_dir = argv[3]
        import_photos(src_dir, dest_dir)
    else:
        print "Unknown action '%s'!" % argv[1]
        exit(USAGE)



