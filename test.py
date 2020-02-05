import os
my_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(my_path, "datafile.json")
print(data_path)
