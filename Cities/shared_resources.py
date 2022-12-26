import os,subprocess
from pexpect import popen_spawn
from datetime import datetime
import socket,logging,sys
import shutil, random, math


class AutoGitHandler:
    def __init__(self,github_username,github_password):   
        self.username=github_username
        self.password=github_password
        self.instances=list()
        self.results=list()
        self.root_folder=None
        

    def configure(self,**args):
        # solution file should be saved as dataset_solution-cost_datetime
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
        
        if args.get('root','None.f')!='None.f':
            self.root_folder=args.get('root')
        else:
            raise ValueError("Path to root are setted to None.f\nPlease set root path")

        print('===== Instances =====')
        for in_index,instance in enumerate(self.instances):
            print(f'Instance {in_index+1}:{instance}')
        print('\n\n\n')

    def git_pull(self):
        logger=logging.getLogger("Pull Repository Data")
        logger.setLevel(logging.INFO)
        formatter=logging.Formatter('%(asctime)s\t%(message)s')
        sh=logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        returned_value=subprocess.call(f'cd {self.root_folder}',shell=True)
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
        logger=logging.getLogger(name=f'AuthGitHandler Uploader')
        logger.setLevel(logging.INFO)
        formatter=logging.Formatter(f'%(asctime)s \t %(message)s')
        sh=logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        logger.info(f'Username:{self.username}')
        logger.info(f'Password:{self.password}')

        returned_value=subprocess.call(f"cd {self.root_folder}",shell=True)
        logger.info(f'Current folder:{self.root_folder}')

        for cmd in [
            f"git add .",
            f"git commit -m update_results_{socket.gethostname()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
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
        logger.info(f"Returned value:{returned_value}",end='\n\n')

class CityProblem:
    rcounter=1
    path_to_results=""

    @staticmethod
    def set_save_folder(folder_name):
        CityProblem.path_to_results=folder_name

    def __init__(self):
        self.cities=list()
        with open(os.path.join('','datasets','cities.txt'),'r') as RF:
            for line in RF:
                x,y=tuple([float(coord) for coord in line.split()])
                self.cities.append((x,y))
        self.travel_plans=dict()

    def travel_plan(self):
        random_10_cities=[self.cities[random.randint(0,len(self.cities)-1)] for _ in range(10)]
        self.travel_plans[f'rnd_city_{CityProblem.rcounter}']=random_10_cities
        CityProblem.rcounter+=1
    
    def generate10_routes(self):
        for _ in range(10):
            self.travel_plan()
    
    def compute_cost(self,solution):
        distance=0
        for i in range(len(solution)-1):
            x,y=solution[i]
            x2,y2=solution[i+1]
            distance+=math.sqrt(math.pow(x-x2,2)+math.pow(y-y2,2))
        return distance
        
    def save_solutions(self):
        for name,traveL_route in self.travel_plans.items():
            with open(os.path.join(CityProblem.path_to_results,f'{name}_{self.compute_cost(traveL_route)}_{datetime.now().strftime("%Y%m%d%H%M%S")}.sol'),'w') as WF:
                for i,(x,y) in enumerate(traveL_route):
                    WF.write(f'City {i+1}:({x},{y})\n')
                WF.write(f'Driving cost:{self.compute_cost(traveL_route)}\n')

    def save_datasets(self):
        for name,travel_route in self.travel_plans.items():
            with open(os.path.join('','datasets',f'{name}.in'),'w') as WF:
                for (x,y) in travel_route:
                    WF.write(f'{x} {y}\n')

if __name__=='__main__':
    CityProblem.set_save_folder(os.path.join('','solutions'))
    problem=CityProblem()
    problem.generate10_routes()
    problem.save_solutions()
    problem.save_datasets()
    
    # handler=AutoGitHandler("vasnastos","basilis99")
