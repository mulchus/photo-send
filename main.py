import os
import subprocess

from subprocess import Popen, PIPE


def main():
    # process = Popen(['zip', 'photo.zip', '-r', 'photo'], stdout=PIPE, stderr=PIPE, shell=True)
    process = Popen(['7z', 'a', 'photo.zip', './photo/*'], stdout=PIPE, stderr=PIPE, shell=True)
    # process = Popen(["echo", "Hello World!"], stdout=PIPE, stderr=PIPE, shell=True)
    stdout, stderr = process.communicate()
    print(stdout)
    print()
    print(stderr.decode('cp866'))

    # s = subprocess.check_output(["echo", "Hello World!"], shell=True)
    # print("s = " + str(s.decode()))




if __name__ == "__main__":
    main()
