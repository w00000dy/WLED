Import('env')
import os
import shutil
import gzip

OUTPUT_DIR = "build_output{}".format(os.path.sep)
VARIANT = env["PIOENV"]
FIRMWARE = env.subst("$BUILD_DIR/${PROGNAME}.bin")

def _get_cpp_define_value(env, define):
    define_list = [item[-1] for item in env["CPPDEFINES"] if item[0] == define]

    if define_list:
        return define_list[0]

    return None

def _create_dirs(dirs=["firmware", "map"]):
    # check if output directories exist and create if necessary
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    for d in dirs:
        if not os.path.isdir("{}{}".format(OUTPUT_DIR, d)):
            os.mkdir("{}{}".format(OUTPUT_DIR, d))

def bin_rename_copy(source, target, env):
    _create_dirs()
    
    # create string with location and file names based on variant
    map_file = "{}map{}{}.map".format(OUTPUT_DIR, os.path.sep, VARIANT)
    bin_file = "{}firmware{}{}.bin".format(OUTPUT_DIR, os.path.sep, VARIANT)

    release_name = _get_cpp_define_value(env, "WLED_RELEASE_NAME")

    if release_name:
        _create_dirs(["release"])
        version = _get_cpp_define_value(env, "WLED_VERSION")
        release_file = "{}release{}WLED_{}_{}.bin".format(OUTPUT_DIR, os.path.sep, version, release_name)
        shutil.copy(FIRMWARE, release_file)

    # check if new target files exist and remove if necessary
    for f in [map_file, bin_file]:
        if os.path.isfile(f):
            os.remove(f)

    # copy firmware.bin to firmware/<variant>.bin
    shutil.copy(FIRMWARE, bin_file)

    # copy firmware.map to map/<variant>.map
    if os.path.isfile("firmware.map"):
        shutil.move("firmware.map", map_file)

def bin_gzip(source, target, env):
    _create_dirs()

    # create string with location and file names based on variant
    bin_file = "{}firmware{}{}.bin".format(OUTPUT_DIR, os.path.sep, VARIANT)
    gzip_file = bin_file + ".gz"

    # check if new target files exist and remove if necessary
    if os.path.isfile(gzip_file): os.remove(gzip_file)

    # write gzip firmware file
    with open(bin_file,"rb") as fp:
        with gzip.open(gzip_file, "wb", compresslevel = 9) as f:
            shutil.copyfileobj(fp, f)

# Always run regardless of whether the firmware has actually been regenerated or not after a “build”
env.AddPostAction(FIRMWARE, [bin_rename_copy, bin_gzip])