import os
import glob


@staticmethod
def write_out(dir: str, fileName: str, ext: str, content: str):
    # remove file at current directory
    files = glob.glob(dir + "/*.html")
    for removable in files:
        if removable.__contains__(fileName+ext):
            os.remove(removable)

    # write out new contents
    with open(dir+fileName+ext, 'w', encoding='utf-8') as f:
        print(content, file=f)
        f.close()