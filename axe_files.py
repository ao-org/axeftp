"""
    Copyright (C) 2022 Pablo Marquez

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


    this is an utility to download files via ftp

"""

import sys
import time
import os
import argparse
import zipfile

from configparser import ConfigParser
from ftplib import FTP



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest="config_file", help="uses CONFIG_FILE as the server configuration", metavar="CONFIG_FILE")
    parser.add_argument("-u", "--ftpuser", dest="ftpuser", help="ftpuser", metavar="FTPUSER")
    parser.add_argument("-r", "--remote_ftp_host", dest="remote_ftp_host", help="Remote ftp host", metavar="REMOTE_FTP_HOST")
    parser.add_argument("-w" "--remote_ftp_port", dest="remote_ftp_port", help="Remote ftp port", metavar="REMOTE_FTP_PORT")
    parser.add_argument("-p", "--ftppass", dest="ftppass", help="Password", metavar="FTP_PASS")
    parser.add_argument("-f", "--remotefolder", dest="remote_folder", help="Folder", metavar="FTP_FOLDER")
    parser.add_argument("-n", "--dcount", dest="dcount", default=1, help="dcount", metavar="DOWNLOAD_COUNT")
    parser.add_argument("-t", "--local_folder", dest="local_folder", default='./', help="Local folder", metavar="LOCAL_FOLDER")


    options = parser.parse_args()
    config = ConfigParser()

    if not options.config_file:
        if not options.ftpuser:
            sys.exit('Missing user to authenticate')
        if not options.ftppass:
            sys.exit(f'Missing passwd for {options.ftpuser}')
        if not options.remote_ftp_host:
            sys.exit(f'Missing remotehost for {options.remote_ftp_host}')
        if not options.remote_ftp_port:
            sys.exit(f'Missing remote port for {options.remote_ftp_host}')
        if not options.remote_folder:
            sys.exit(f'Missing remote folder for {options.remote_ftp_host}')



    ftp = FTP()
    ftp.connect(options.remote_ftp_host, int( options.remote_ftp_port))
    ftp.login(options.ftpuser,options.ftppass)
  
    # changing directory
    ftp.cwd(options.remote_folder)
  
    names = ftp.nlst()

    latest_time = None
    latest_name = None

    flist = []
    print('Getting last modified time for each backup.')
    for name in names:
        if name.endswith('.zip') :
            ftime = ftp.voidcmd(f'MDTM {name}').split()[1]
            print(name)
            print(f'File: {name} last modified: {ftime}')
            flist.append((name,ftime))

    print(f'Downloading the last {options.dcount} files')
    flist.sort(key=lambda tup: tup[1],reverse=True)  # sorts in place
    c = 0 
    for remote_file,d in flist:
        local_file =  f"{options.local_folder}{d}.zip"
        print(f'Downloading {remote_file}...---->{local_file}')
        ftp.retrbinary(f'RETR {remote_file}',open(local_file, 'wb').write)
        c+=1
        if c > int(options.dcount): break

    c = 0
    for remote_file,d in flist:
        local_file =  f"{options.local_folder}{d}.zip"
        print(f'Inflating {local_file}')
        with zipfile.ZipFile(local_file,"r") as zip_ref:
            zip_ref.extractall()
        c+=1
        if c > int(options.dcount): break


    print('All done...')
    ftp.quit()

