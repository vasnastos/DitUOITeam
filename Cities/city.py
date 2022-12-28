import os,random,math
from datetime import datetime

class Problem:
    path_to_results=""
    path_to_datasets=os.path.join('','datasets')

    @staticmethod
    def set_save_folder(folder_name):
        Problem.path_to_results=folder_name

    def __init__(self):
        self.routes=dict()
    
    def create_routes(self,number_of_routes):
        with open(os.path.join('','cities.txt'),'r') as RF:
            for line in RF:
                x,y=tuple([float(coord) for coord in line.split()])
                self.cities.append((x,y))
        self.routes={f'rnd_city_{index}':[self.cities[random.randint(0,len(self.cities)-1)] for _ in range(10)] for index in range(number_of_routes)}
        self.solutions={f'rnd_city_{index}':list()  for index in range(number_of_routes)}
        self.save_datasets()
        self.save_solutions()
    
    def load_routes(self):
        self.solutions={}
        for dataset_name in os.listdir(Problem.path_to_datasets):
            with open(os.path.join(Problem.path_to_datasets,dataset_name),'r') as RF:
                self.routes[dataset_name.removesuffix('.in')]=[tuple([float(x) for x in line.split()]) for line in RF]
                self.solutions[dataset_name.removesuffix('.in')]=list()

    def compute_cost(self,solution):
        distance=0
        for i in range(len(solution)-1):
            x,y=solution[i]
            x2,y2=solution[i+1]
            distance+=math.sqrt(math.pow(x-x2,2)+math.pow(y-y2,2))
        return distance

    def add_solution(self,instance,solution):
        self.solutions[instance].append(solution)

    def save_solutions(self):
        for name,solutions in self.solutions.items():
            for solution in solutions:
                with open(os.path.join(Problem.path_to_results,f'{name}_{self.compute_cost(solution)}_{datetime.now().strftime("%Y%m%d%H%M%S")}.sol'),'w') as WF:
                    for i,(x,y) in enumerate(solution):
                        WF.write(f'City {i+1}:({x},{y})\n')
                    WF.write(f'Driving cost:{self.compute_cost(solution)}\n')

    def save_datasets(self):
        for name,travel_route in self.routes.items():
            with open(os.path.join('','datasets',f'{name}.in'),'w') as WF:
                for (x,y) in travel_route:
                    WF.write(f'{x} {y}\n')