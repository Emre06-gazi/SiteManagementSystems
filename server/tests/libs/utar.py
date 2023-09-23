# import module
import tarfile

# declare filename
filename = "tutorial.tar"


def reset(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


# open file in write mode
file_obj = tarfile.open(filename, "w", format=tarfile.GNU_FORMAT, bufsize=512)

# Add other files to tar file

file_obj.add("testDevice") # , filter=reset

# close file
file_obj.close()
