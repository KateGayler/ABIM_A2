# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 14:53:25 2023

@author: nadja
"""
#Import libraries
from pathlib import Path
import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.element
import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd

#Import model
modelname = "LLYN - ARK_Qto"

try:
    dir_path = Path(__file__).parent
    model_url = Path.joinpath(dir_path, 'model', modelname).with_suffix('.ifc')
    model = ifcopenshell.open(model_url)
except OSError:
    try:
        import bpy
        model_url = Path.joinpath(Path(bpy.context.space_data.text.filepath).parent, 'model', modelname).with_suffix('.ifc')
        model = ifcopenshell.open(model_url)
    except OSError:
        print(f"ERROR: please check your model folder : {model_url} does not exist")
        
        
########################## Format check #################################

#Checks the IFC format of the file - Should be IFC4
format = model.schema
if format == "IFC4":
    print(f"\n The file format is {format} and is okay")
else:
    print(f"\n The file is {format} and not IFC4. The model should therefore be updated to IFC4.")



########################## Space data ##########################
#Store all spaces
spaces = model.by_type("IfcSpace")

#Number of spaces
spaces_in_model = len(spaces)
print(f"\n There are {spaces_in_model} spaces in the model. ")

##Creates a loop, that loops through all the rooms and retrieves the data
#Empty variables are made to append data to
floor_covering = []
space_volume=[]
space_area=[]
space_ceiling_area=[]
space_LongName=[]
space_Name=[]
i = 0

#Retrieves the needed property+quantity of a space. If the needed property sets are not available,
# 0 is appended
#Retrieves: Space volume, area, ceiling area and floor covering
for space in spaces:
    psets_space = ifcopenshell.util.element.get_psets(space,psets_only=False)
    space_LongName.append(space.LongName)
    space_Name.append(space.Name)
    if "Qto_SpaceBaseQuantities" in psets_space and "NetVolume" in psets_space["Qto_SpaceBaseQuantities"]:
        space_volume.append(psets_space["Qto_SpaceBaseQuantities"]["NetVolume"])
        space_area.append(psets_space["Qto_SpaceBaseQuantities"]["NetFloorArea"])
        space_ceiling_area.append(psets_space["Qto_SpaceBaseQuantities"]["NetCeilingArea"])
        i = i+1
    else: 
        space_volume.append(0)
        space_area.append(0)
        space_ceiling_area.append(0)
    if "Pset_SpaceCoveringRequirements" in psets_space:
        floor_covering.append(psets_space["Pset_SpaceCoveringRequirements"]["FloorCovering"])
    else: 
        floor_covering.append("0")

#Overview of the number of rooms with quantaties
if i == spaces_in_model:
    print("All spaces in the model contain the necessary quantities.\n")
else: 
    print(f"\n {i} spaces contain quantities out of {spaces_in_model} spaces. You may want to add quantities to the remaining spaces.\n")

#Merges the space number together with the longname of the space
space_description = [x + ' ' + y for x, y in zip(space_Name, space_LongName)]

########################## Wall data ##################################  
#Empty variables
wall_space_total = []
matrix_wall_area = []
matrix_wall_material=[]

#Creates a loop that goes through all the spaces, identifies the boundering elements
#And for the ones that are wall, find the wall material and wall area
#The wall material and area is stored in a matrix, so each wall of a room can be 
#identified with the corresponding material, since not all walls of a room has the same material
for space in spaces:
    near = space.BoundedBy
    wall_space_area = []
    wall_material = []
    for objects in near:
        if (objects.RelatedBuildingElement != None):
            if (objects.RelatedBuildingElement.is_a('IfcWall')):
                material = ifcopenshell.util.element.get_material(objects.RelatedBuildingElement)
                if material.is_a("IfcMaterial"):
                    wall_material.append(material.Name)
                if material.is_a("IfcMaterialConstituentSet"):
                    Constituent=material.MaterialConstituents[-1]   #Assumes that the material closest to the room is defined last
                    Constituent_material = Constituent.Material
                    wall_material.append(Constituent_material.Name)
                psets_wall = ifcopenshell.util.element.get_psets(objects.RelatedBuildingElement)
                if "Qto_WallBaseQuantities" in psets_wall:
                    wall_space_area.append(psets_wall["Qto_WallBaseQuantities"]["NetSideArea"])
    matrix_wall_material.append(wall_material)
    matrix_wall_area.append(wall_space_area)
    wall_space_total.append(np.sum(wall_space_area))


############################### Calculation of VOC concentration #############################
 
#Define SER values (off-gassing values) for known materials
materials = {"Epoxy":25,"Beton":5,"Vinyl":30,"Fliser":0,"Gummi":15}     #ug/h/m2

#Function that search for partial matches between dictionary key and searchword
def partial_match(search_word, keys):
    for key in keys:
        if key in search_word:
            return key
    return None

#Makes a list of SER values corresponding to each floor covering in each space
floor_SER = [materials[partial_match(word, materials.keys())] if partial_match(word, materials.keys()) is not None else 0 for word in floor_covering]

#Calculates the emission rate. The space area equals the floor covering area
emission_rate_floor = np.multiply(floor_SER,space_area)       #ug/h

#Defining the ventilation rate to be 0,7 l/s*m2 (since unknown in model) and calculates air change rate of the space
ventilation_rate = [0.7 for _ in range(len(space_area))]    #l/s*m2
air_change = np.divide((np.multiply(ventilation_rate,space_area)*(10**(-3))*3600),space_volume)     #h^-1

#Calculation of VOC concentration and relating VOC concentration to room in a dictionary
VOC_concentration = np.around(np.divide(emission_rate_floor,np.multiply(air_change,space_volume)),3)             #ug/m3
zip_dict = dict(zip(space_description,VOC_concentration))


########################### Data visualisation #################################

#Create a dataframe for easier management of all of the data
data = {"Space number":space_Name,"Space type":space_LongName,"Floor area":space_area,
        "Room volume":space_volume,"Floor covering":floor_covering,"VOC concentration":VOC_concentration}

df = pd.DataFrame(data)

print(f"The VOC for each room is now calculated. The data for each room can be found in the dataframe df. \n \n {df}")

#Plot of the concentrations in the rooms
indices = np.where(~np.isnan(VOC_concentration))[0]     #Gets all the indices where there are calculated VOC concentration

plt.bar(np.array(space_description)[indices], np.array(VOC_concentration)[indices], color ='maroon', width = 0.4)    

plt.xticks(rotation=90)
plt.title("VOC concentration pr. room")
plt.xlabel("Room name")
plt.ylabel("VOC concentration [ug/m3]")

print("The VOC concentration is plotted as bar plots in the 'plots' tab.")

#Finds the 'Top 10 worst rooms' in the building
indices10 = np.argsort(np.array(VOC_concentration)[indices])[-10:]
top10_VOC = [np.array(VOC_concentration)[indices][i] for i in indices10]
top10_spaces = [np.array(space_description)[indices][i] for i in indices10]

print(f"\n The 10 worst spaces in the model are:{top10_spaces}, with the given values:\n")

for top10_spaces, top10_VOC in zip(top10_spaces, top10_VOC):
    print(f"{top10_spaces:<15}{top10_VOC}")
