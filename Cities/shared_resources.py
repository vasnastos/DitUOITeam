import os,subprocess
from datetime import datetime
import platform
import socket,logging
import shutil, random, math
from tabulate import tabulate
import shutil


class AutoGitHandler:
    def __init__(self,github_username,github_password):   
        self.username=github_username
        self.password=github_password
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
            f"git add {self.results}",
            f"git commit -m update_results_{socket.gethostname()}_{platform.processor()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            "git push"
        ]:
            self.logger.info(f'Command execute:{cmd}')
            subprocess.call(cmd,shell=True)

        self.logger.info("========== Uploaded finished ==========",end='\n\n')

class CityProblem:
    path_to_results=""
    path_to_datasets=os.path.join('','datasets')

    @staticmethod
    def set_save_folder(folder_name):
        CityProblem.path_to_results=folder_name

    def __init__(self):
        self.routes=dict()
    
    def create_routes(self):
        with open(os.path.join('','cities.txt'),'r') as RF:
            for line in RF:
                x,y=tuple([float(coord) for coord in line.split()])
                self.cities.append((x,y))
        self.routes=self.travel_plan(10)
        self.save_datasets()
        self.save_solutions()
    
    def load_routes(self):
        for dataset_name in os.listdir(CityProblem.path_to_datasets):
            with open(os.path.join(CityProblem.path_to_datasets,dataset_name),'r') as RF:
                route=list()
                for line in RF:
                    route.append(tuple([float(x) for x in line.split()]))
                self.routes[dataset_name.removesuffix('.in')]=route

    def travel_plan(self,number_of_routes):
        return {f'rnd_city_{index}':[self.cities[random.randint(0,len(self.cities)-1)] for _ in range(10)] for index in range(number_of_routes)}
    
    
    def compute_cost(self,solution):
        distance=0
        for i in range(len(solution)-1):
            x,y=solution[i]
            x2,y2=solution[i+1]
            distance+=math.sqrt(math.pow(x-x2,2)+math.pow(y-y2,2))
        return distance
        
    def save_solutions(self):
        for name,travel_route in self.routes.items():
            with open(os.path.join(CityProblem.path_to_results,f'{name}_{self.compute_cost(travel_route)}_{datetime.now().strftime("%Y%m%d%H%M%S")}.sol'),'w') as WF:
                for i,(x,y) in enumerate(travel_route):
                    WF.write(f'City {i+1}:({x},{y})\n')
                WF.write(f'Driving cost:{self.compute_cost(travel_route)}\n')

    def save_datasets(self):
        for name,travel_route in self.routes.items():
            with open(os.path.join('','datasets',f'{name}.in'),'w') as WF:
                for (x,y) in travel_route:
                    WF.write(f'{x} {y}\n')
    
    def shuffle_routes(self):
        for _,route in self.routes.items():
            random.shuffle(route)
        self.save_solutions()


if __name__=='__main__':
    # CityProblem.set_save_folder(os.path.join('','solutions'))
    # problem=CityProblem()
    # problem.generate10_routes()
    # problem.save_solutions()
    # problem.save_datasets()
    
    handler=AutoGitHandler("vasnastos","basilis99")
    handler.configure(instances=os.path.join(os.getcwd(),'datasets'),results=os.path.join(os.getcwd(),'solutions'),root=os.getcwd(),split_token="_",objective_position=2,email="nastosvasileios99@gmail.com")
    handler.git_pull()