import os,subprocess
from pexpect import popen_spawn
import socket,logging


class UpLoader:
    def __init__(self,get_path_to_files):
        self.filepath=get_path_to_files
        self.files=list()    
        
    def git_upload(self):    
        logger=logging.getLogger(name=f'Uploader_Logger')
        logger.setLevel(logging.INFO)
        formatter=logging.Formatter(f'%(asctime)s \t %(message)s')
        sh=logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        github_username="vasnastos"
        github_password="basilis99"
        logger.info(github_username)
        logger.info(github_password)

        returned_value=subprocess.call(f"cd {self.filepath}",shell=True)

        for cmd in [
            f"git add .",
            f"git commit -m update_results_{socket}"
        ]:
            logger.info(f'Command execute:{cmd}')
            subprocess.call(cmd,shell=True)
        
        cmd="git push"
        child_process=popen_spawn.PopenSpawn(cmd)
        child_process.expect(github_username)
        child_process.sendline(github_username)
        child_process.expect(github_password)
        child_process.sendline(github_password)
        logger.info(f"Successful Authontication:{github_username},{github_password}")
        logger.info(f"Returned value:{returned_value}")

        logger.info("End of procedure")

    


