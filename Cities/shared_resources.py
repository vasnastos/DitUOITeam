import os,subprocess
from datetime import datetime
import platform
import socket,logging
import shutil, random, math
from tabulate import tabulate
import shutil,yaml,time,cpuinfo


class AutoGitHandler:
    def __init__(self):   
        self.username=None
        self.instances=list()
        self.results=list()
        self.split_token=None
        self.objective_position=None
        self.root_folder=None
        self.user_email=None
        self.best_solutions=None
        self.target_folders=list()

        self.logger=logging.getLogger("Solution Validator")
        self.logger.setLevel(logging.INFO)
        formatter=logging.Formatter('%(asctime)s %(message)s')
        sh=logging.StreamHandler()
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)
    
    def add_target_folder(self,target_folder):
        self.target_folders.append(target_folder)

    def configure(self,**args):
        if args.get("username",None):
            self.username=args.get("username")
        else:
            raise ValueError("User name does not setted\nPlease provide a username")

        if args.get('instances','None.f')!='None.f':
            self.filepath=args.get('instances')
            self.instances=os.listdir(self.filepath)
        else:
            raise ValueError("Path to instances are set to:None.f\nPlease provide path to instances")

        if args.get('results','None.f')!='None.f':
            self.results=args.get('results')
        else:
            raise ValueError("Path to solutions are setted to None.f\nPlease set path to solutions!!")
        
        if args.get('root','None.f')!='None.f':
            self.root_folder=args.get('root')
        else:
            raise ValueError("Path to root are setted to None.f\nPlease set root path")


        if args.get('split_token','None')!='None':
            self.split_token=args.get('split_token')
        else:
            raise ValueError("Split token are setted to None\nPlease provide a split token")
        
        if args.get('objective_position',None):
            self.objective_position=args.get('objective_position')
        
        if args.get('email',None):
            self.user_email=args.get('email')
        else:
            raise ValueError("User email not configure\nPlease set the user email")

        if args.get("best_solutions",None):
            self.best_solutions=args.get("best_solutions")

        print('===== Instances =====')
        for in_index,instance in enumerate(self.instances):
            print(f'Instance {in_index+1}:{instance}')
        print('\n\n')

        print(tabulate([
            ["Username",self.username],
            ["User Email",self.user_email],
            ["Instances",len(self.instances)],
            ["solutions",self.results],
            ["Root",self.root_folder],
            ["Split_token",self.split_token],
            ["Objective_position",self.objective_position],
            ["Best solutions",self.best_solutions]
        ],headers=["Configuration item","Value"],tablefmt='fancy_grid'),end='\n')

    def configure_via_file(self,path_to_configurations):
        RF=open(path_to_configurations,'r')
        configurations=yaml.load(RF,Loader=yaml.FullLoader)
        RF.close()

        excluded=False
        for config_key in ['username','root','instances','results','split_token','objective_position','email']:
            if config_key not in list(configurations.keys()):
                self.logger.info(f"Configurations key missed:{config_key}")
                excluded=True

        if excluded:
            raise "Configuration file does not filled correctly"

        self.username=configurations['username']
        self.root_folder=configurations['root']
        self.instances=configurations['instances']
        self.results=configurations['results']
        self.split_token=configurations['split_token']
        self.objective_position=configurations['objective_position']
        self.user_email=configurations['email']

        if 'target' in list(configurations.keys()):
            self.target_folders=configurations['target']


    def git_best(self):
        best_solutions=dict()
        for instance in self.instances:
            solution=[solution_filename for solution_filename in os.listdir(self.best_solutions) if solution_filename.startswith(instance.removesuffix(".xml"))]
            if len(solution)==0:
                best_solutions[instance.removesuffix(".xml")]=None
            else:
                best_solutions[instance.removesuffix(".xml")]=float(solution.split(self.split_token)[self.objective_position])

        previous_best_solution=best_solutions.copy()
        best_solution_change={instance:False for instance in self.instances}
        for solution_filename in os.listdir(self.results):
            instance=[instance.removesuffix(".xml") for instance in self.instances if solution_filename.startswith(instance)]
            solution_data=solution_filename.split(self.split_token)
            if best_solutions[instance]:
                best_objective_value=float(best_solutions[instance].split()[self.objective_position])
                if float(solution_data[self.objective_position])<best_objective_value:
                    self.logger.info(f"Instance:{instance} Previous best solution:{best_objective_value} New best solution:{float(solution_data[self.objective_position])}  Best solution file:{solution_filename}")
                    best_solution_change[instance]=True
                    best_solutions[instance]=solution_filename
            else:
                self.logger.info(f"Instance:{instance} New best solution:{float(solution_data[self.objective_position])}  Best solution file:{solution_filename}")
                best_solution_change[instance]=True
                best_solutions[instance]=solution_filename

        self.logger.info(f"New best solutions found:{sum(list(best_solution_change.values()))}")

        for instance,solution_change in best_solution_change.items():
            if solution_change:
                os.remove(os.path.join(self.results,previous_best_solution[instance]))
                shutil.copy2(os.path.join(self.results,best_solutions[instance]),self.best_solutions)

        with open(os.path.join('','reports',f'{socket.gethostname()}_{platform.processor()}.out'),'a') as WF:
            WF.write(f"========== New Report:{datetime.now().strftime('%Y%m%d%H%M%S')} ==========")
            WF.write(
                str(tabulate(
                    [
                        [instance,solution_changed if not solution_changed else ", ".join([previous_best_solution[instance],best_solutions[instance]])]
                        for instance,solution_changed in best_solution_change.items()
                    ],headers=["Instance","New Solution"],tablefmt='textfile'
                ))
            )


    def git_authentication(self):
        if self.username==None or self.user_email:
            raise ValueError("Username not setted\n Set username")
        
        for cmd in [
            f"git config --global user.name {self.username}",
            f"git config --global user.email {self.user_email}"
        ]:
            returned_value=subprocess.call(cmd)
            self.logger.info(f"Command executed:{cmd}\tExecuted:{bool(returned_value)}")
        
        print("====== Authentication complete =======")
        self.logger.info(f"Authentication settings:{self.username},{self.user_email}")


    def git_pull(self):
        logger=logging.getLogger("Repository Puller")
        logger.setLevel(logging.INFO)
        formatter=logging.Formatter('%(asctime)s\t%(message)s')
        sh=logging.StreamHandler()
        sh.setFormatter(formatter)
        logger.addHandler(sh)

        returned_value=subprocess.call(f'cd {self.root_folder}',shell=True)
        cmd='git pull'
        subprocess.call(cmd,shell=True)
        logger.info(f'Command:{cmd}')
        logger.info(f'Returned value:{returned_value}')

    def git_push(self):    
        for cmd in [
            f"git add {' '.join(self.target_folders)}",
            f"git commit -m solutions_{socket.gethostname()}_{cpuinfo.get_cpu_info()['brand_raw'].replace(' ','_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            "git push"
        ]:
            self.logger.info(f'Command execute:{cmd}')
            subprocess.call(cmd,shell=True)

        self.logger.info("========== Uploaded finished ==========",end='\n\n')


def solve():
    from city import Problem
    Problem.set_save_folder(os.path.join(os.getcwd(),'solutions'))
    cityProblem=Problem()
    cityProblem.load_routes()
    
    for instance,solution in cityProblem.routes.items():
        for _ in range(3):
            new_solution=solution.copy()
            random.shuffle(new_solution)
            cityProblem.add_solution(instance,new_solution)
    cityProblem.save_solutions()


if __name__=='__main__':
    handler=AutoGitHandler()
    handler.configure(username="vasnastos",instances=os.path.join(os.getcwd(),'datasets'),results=os.path.join(os.getcwd(),'solutions'),root=os.getcwd(),split_token="_",objective_position=2,email="nastosvasileios99@gmail.com")
    handler.add_target_folder(os.path.join('','solutions'))
    handler.git_pull()

    solve()
    handler.git_push()