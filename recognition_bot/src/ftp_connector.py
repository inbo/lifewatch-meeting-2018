
import os
import pysftp


class Connector:
    def download_file(self, filename, local_path_prefix):
        """download a file to local drive"""
        raise NotImplementedError

    def list_files(self, name_match):
        """list the files within a given subfolder or relative path"""
        raise NotImplementedError


class FTPConnector(Connector):
    """General FTP handling class
    """

    _ftp_connection = None

    def __init__(self, ftp_url=None, ftp_username=None,
                 ftp_pwd=None, subfolder='Documents'):
        """Initialize a Connector to a FTP drive
        Initialize a Connection to an FTP drive or a specific subfolder of the
        FTP drive under consideration
        :param ftp_url: url of the FTP
        :param ftp_username: username of the FTP
        :param ftp_pwd: password of the FTP username
        :param subfolder: optional subfolder listing to set working directory (
        or None)
        """
        self._ftp_url = ftp_url
        self._ftp_username = ftp_username
        self._ftp_pwd = ftp_pwd

        self._connect_to_ftp(self._ftp_url, self._ftp_username,
                             self._ftp_pwd, subfolder)

    def _connect_to_ftp(self, url, login, pwd, subfolder=None):
        """Private method to connect to the FTP drive
        """
        self._ftp = pysftp.Connection(url,  username=login, password=pwd)
        if subfolder:
            self._ftp.cwd(subfolder)

    def __del__(self):
        self._ftp.close()

    def download_file(self, filename, local_path_prefix="../photos"):
        """Download a single file
        Download a file with a given filename from FTP
        :param filename:
        :type filename: string
        """
        local_path = os.path.join(local_path_prefix, filename)
        self._ftp.get(filename, localpath=local_path, preserve_mtime=True)

    def list_files(self, name_match=".jpg"):
        """list the files within the current working directory
        Returns an iterator that allows you to iterate over all files in the
        current working directory, optionally only those with a specific name match
        :param name_match: string that should be contained in the file name
        :return: yields the file names
        """
        for fname in self._ftp.listdir():
            if name_match in fname:
                yield fname
    
    def delete_file(self, filename):
        """delete file in current dir
        
        Arguments:
            filename str -- filename of file to remove
        """
        self._ftp.remove(filename)
