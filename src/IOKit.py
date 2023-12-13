import os
import glob
import json

from src.PlayerKit import Player

getDir = lambda dir: dir if dir else "root"


def writeOut(dir: str = "", fileName: str = "", ext: str = "", content: object = None):
    # w+: Opens a file for both writing and reading. Overwrites the existing file if the file exists.
    # If the file does not exist, creates a new file for reading and writing.
    if isinstance(content[0], Player):
        content = [x.__dict__ for x in content] # serialize Player objects
        with open(os.path.join(dir, (fileName + ext)), mode='w+', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
            print(f'{fileName}{ext} successfully saved to {getDir(dir)}')
            f.close()
    else:
        with open(os.path.join(dir, (fileName + ext)), mode='w+', encoding='utf-8') as f:
            # print(content, file=f)
            f.write(content)
            # print(f'{fileName}{ext} successfully saved to {getDir(dir)}')
            f.close()


def renameFile(dir: str, fExt: str, downloadedFile: str, newFileName: str):
    # get all the .csv files in the download directory
    files = glob.glob(dir + "*" + fExt)
    for f in files:
        fName = f.rsplit("/", 1)[1]
        if fName.__eq__(downloadedFile):
            # remove old files
            for removable in files:
                if removable.__contains__(newFileName):
                    os.remove(removable)
                    break
            newDownloadPath = dir + newFileName + ".csv"
            os.rename(f, newDownloadPath)
            # locCSVs.append(newDownloadPath)
            # print(f"successfully downloaded {newFileName} to {getDir(dir)}")
            return
        

def readIn(dir: str = "", fileName: str = "", ext: str = "") -> any:
    with open(os.path.join(dir, (fileName + ext)), mode='r', encoding='utf-8') as f:
        content = f.read()
        f.close()
        print(f'{fileName}{ext} successfully read from {getDir(dir)}')
        return content
