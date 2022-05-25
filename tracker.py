#!/usr/bin/env python

import re
import json
import argparse
import requests
import pefile

def download(url):
    r = requests.get(url)
    assert(r.status_code == 200)
    return r.content

def file_info(pe):
    return {k.decode("utf8"):v.decode("utf8") for k,v in pe.FileInfo[0][0].StringTable[0].entries.items()}

RE_MANIFEST = re.compile("<manifest.*?</manifest>", flags=re.DOTALL)

class SysmonBin():

    def __init__(self, data: bytes):
        self._pe = pefile.PE(data=data)
        self._file_info = None
        self._manifests = None
    
    @property
    def PE(self) -> pefile.PE:
        return self._pe

    @property
    def file_info(self):
        if self._file_info is None:
            self._file_info = file_info(self.PE)
        return self._file_info

    @property
    def manifests(self):
        if self._manifests is None:
            xml_entry = None
            for entry in self.PE.DIRECTORY_ENTRY_RESOURCE.entries:
                if str(entry.name) == "XML":
                    xml_entry = entry
                    break
            
            if xml_entry is not None:
                sub_entry = xml_entry.directory.entries[0].directory.entries[0]
                struct = sub_entry.data.struct
                data = self.PE.get_data(struct.OffsetToData, length=struct.Size)
                self._manifests = RE_MANIFEST.findall(data.decode("utf16"))
            else:
                self._manifests = []

        return self._manifests



if __name__ == "__main__":

    file_info_path = "file-info.json"
    manifest_path = "manifest.xml"
    sysmon_path = "Sysmon.exe"
    sysmon_url = "https://live.sysinternals.com/Sysmon.exe"

    parser = argparse.ArgumentParser()
    
    parser.add_argument("--url", type=str, help="Overrides default URL")
    parser.add_argument("--binary", type=str, help="Use binary specified instead of remote file")
    parser.add_argument("-d", "--dump", action="store_true", help="Dump binary")
    parser.add_argument("-u", "--update", action="store_true", help="Update manifest XML file and file-info.json")
    parser.add_argument("-pv", "--product-version", action="store_true", help="Return ProductVersion information from file-info.json")

    args = parser.parse_args()

    if args.update:
        # initialize pe data
        if args.binary is not None:
            with open(args.binary, "rb") as fd:
                pe_data = fd.read()
        elif args.url is not None:
            pe_data = download(args.url)
        else:
            pe_data = download(sysmon_url)
        
        s = SysmonBin(pe_data)

        with open(file_info_path, "w") as fd:
            json.dump(s.file_info, fd, indent="  ")

        if len(s.manifests) > 0:
            with open(manifest_path, "w") as fd:
                fd.write(s.manifests[0])

        if args.dump:
            with open(sysmon_path, "wb") as fd:
                fd.write(pe_data)
        
    if args.product_version:
        fi = json.load(open(file_info_path))
        print(fi["ProductVersion"])
