import os
import glob


@staticmethod
def write_out(dir: str, fileName: str, ext: str, content: object):
    # w+: Opens a file for both writing and reading. Overwrites the existing file if the file exists.
    # If the file does not exist, creates a new file for reading and writing.
    with open(dir + fileName + ext, mode='w+', encoding='utf-8') as f:
        # print(content, file=f)
        f.write(content)
        print(f'{fileName}.{ext} successfully saved.')
        f.close()
