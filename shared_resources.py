import os,subprocess
from pexpect import popen_spawn
from datetime import datetime
import socket,logging,sys
import shutil


class AutoGitHandler:
    def __init__(self,github_username,github_password):  
        self.filepath=None  
        self.username=github_username
        self.password=github_password
        self.instances=list()
        self.results=list()
        

    def configure(self,**args):
        if args.get('instances','None.f')!='None.f':
            self.filepath=args.get('instances')
            self.instances=os.listdir(self.filepath)
            for instance in self.instances:
                instance_name=instance.removesuffix('xml')
                self.results[instance_name]=dict(name="None.f",objective_infeasibilities=sys.maxsize,objective_value=sys.maxsize)
        else:
            raise ValueError("Path to instances are set to:None.f\nPlease provide path to instances")

        if args.get('results','None.f')!='None.f':
            for solution_file in os.listdir(args['results']):
                sname,infeasibilities,objective_value=tuple(solution_file.split('-'))
                if infeasibilities<self.results[sname]['objective_infeasibilities']:
                    self.results[sname]['name']=os.path.join(args.get('results'),solution_file)
                    self.results[sname]['objective_infeasibilities']=infeasibilities
                    self.results[sname]['objective_values']=objective_value
                
                elif infeasibilities==self.results[sname]['objective_infeasibilities']:
                    if self.results[sname]['objective_value']<objective_value:
                        self.results[sname]['name']=os.path.join(args.get('results'),solution_file)
                        self.results[sname]['objective_infeasibilities']=infeasibilities
                        self.results[sname]['objective_values']=objective_value
        else:
            raise ValueError("Path to solutions are setted to None.f\nPlease set path to solutions!!")
        
        print('===== Instances =====')
        for in_index,instance in enumerate(self.instances):
            print(f'Instance {in_index+1}:{instance}')
        print('\n\n\n')
    
    def save_best(self):
        pass

    def git_pull(self):
        logger=logging.getLogger("Puller")
        logger.setLevel(logging.INFO)
        formatter=logging.Formatter('%(asctime)s\t%(message)s')
        sh=logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        returned_value=subprocess.call(f'cd {self.filepath}',shell=True)
        cmd='git pull'
        child_process=popen_spawn.PopenSpawn(cmd)
        child_process.expect(self.username)
        child_process.sendline(self.username)
        child_process.expect(self.password)
        child_process.sendline(self.password)
        logger.info(f'Command:{cmd}')
        logger.info(f'Successful Authentication:{self.username},{self.password}')
        logger.info(f'Returned value:{returned_value}')

    def git_upload(self):    
        logger=logging.getLogger(name=f'Uploader_Logger')
        logger.setLevel(logging.INFO)
        formatter=logging.Formatter(f'%(asctime)s \t %(message)s')
        sh=logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        logger.info(f'Username:{self.username}')
        logger.info(f'Password:{self.password}')

        returned_value=subprocess.call(f"cd {self.filepath}",shell=True)

        for cmd in [
            f"git add .",
            f"git commit -m update_results_{socket}"
        ]:
            logger.info(f'Command execute:{cmd}')
            subprocess.call(cmd,shell=True)
        
        cmd="git push"
        child_process=popen_spawn.PopenSpawn(cmd)
        child_process.expect(self.username)
        child_process.sendline(self.username)
        child_process.expect(self.password)
        child_process.sendline(self.password)
        logger.info(f"Successful Authontication:{self.username},{self.password}")
        logger.info(f"Returned value:{returned_value}")

        logger.info("========== Uploaded finished ==========")
        logger.info(f'Datetime:{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        logger.info(f'Files changes:')

