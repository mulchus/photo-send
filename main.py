from subprocess import Popen, PIPE


def main():
    archive = Popen(['zip', '-r', '-', '.', '-i', './photo/*'], stdout=PIPE, stderr=PIPE)
    stdout, stderr = archive.communicate()
    print(len(stdout))
    print(stderr.decode('utf-8'))
    with open('photo.zip', 'wb') as file:
        file.write(stdout)
    
    # s = subprocess.check_output(["echo", "Hello World!"], shell=True)
    # print("s = " + str(s.decode()))
    

if __name__ == "__main__":
    main()
