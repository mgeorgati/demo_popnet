import glob, os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_directory = base_dir + "/experiments"
for root, dirs, files in os.walk(out_directory):
    for file in files:
        if file.startswith("percAccu"):
            fileName= os.path.join(root, file)
            print(fileName)
            os.remove(fileName)