# Using IFC to Determine Where Healthy Materials Should Be a Prioritiy for Improved IEQ in a Building

## Flooring VOC Emissions and Space Concentrations

#### Use case description

This script solves the task of determining the Volatile Organic Compounds (VOCs) concentration for each space in a building model based on: the off-gassing from the materials in the room, their surface area, and the estimated air change rate of the space. This makes it possible to identify problematic spaces and improvement potentials. The concentration of VOCs in a room should be limited to ensure a healthy and good indoor air quality. Thus, this tool will contribute to assessing and improving the indoor environmental quality (IEQ), helping to create better spaces for occupants, early in the design process.

##### Why is this valuable?

The value in this tool is that it provides any constituent in the building design process with an easy tool to perform analysis on the off-gassing of materials in a building based on the building's IFC file. This means that as long as there is in IFC file with spaces and quantities assigned and information on off-gassing for specific materials, concentration analysis can be conducted from the early design stages to generate improved iterations.

##### Who can this tool be used by?

- Project managers in the building industry trying to make cost effective decisions while maintaining building health

- Architects focused on designing material and health conscious spaces

- Engineers involved in performing building simulations and other analyses

- Anyone working in the built environment space who is interested in improving decision making for material selection

##### What does the script do?

The script runs a loop through all unique spaces in an IFC file to retrieve data for each space in a building including space name, floor- and ceiling areas, volumes, and the floor covering in a space. The current script calculates only VOC off-gassing from the floor covering, but would (if expanded) be calculated for all walls, floors, ceilings, and furnitures in the space. The script, therefore, additionally runs a loop that goes through all spaces to determine the bounding wall elements and their materials. The information is not yet further utilized, but is made available if necessary. 

Disciplinary expertise in indoor air quality (IAQ) and ventilation is required to perform an analysis and assessment of VOC concentrations in the spaces based on the information extracted from the IFC. A list with off-gassing rates for particular flooring materials has been created and is utilized in calculations for VOC concentrations in the spaces.

The emission rate for all flooring in a room is then determined by multiplying the space area and the specific emission rate corresponding to the floor covering in the space. In this particular script, an assumed ventilation rate was used along with the extracted space volume to determine the air change rate in the space requiring expert knowledge of necessary ventilation rates for the spaces and the influence of the air exchange rate. Once the space emission rate and air change rate are determined, the VOC concentration in a space can be estimated and is printed. Plots and a 'Top 10' list are generated to easily compare VOC 'hotspots' in the building.

No other use cases are needed to be done before starting the script, and no other use cases are waiting for this script to be complete.

###### IFC Input data:

Necessary for the final VOC calculation with this script

- Room identifier = space_Name

- Room type = space_LongName

- Room area = space_area

- Room volume = space_volume

- Flooring type = floor_covering

Input used but not applied for final VOC calculation 

- Wall material = matrix_wall_material

- Wall area = matrix_wall_area

- Ceiling area = space_ceiling_area

###### External Input data:

- Specific Emission Rate (SER) of materials

- Ventilation rate

###### IFC Concepts used

- Property- and quantity sets: Retrieves space volume, floor area, ceiling area and floor covering given from the quantity sets Qto_SpaceBaseQuantities, Qto_WallBaseQuantities, and property set Pset_SpaceCoveringRequirements. The property set Pset_SpaceThermalLoad defined the with the property AirExchangeRate could for future development of the script be used to define the air change rate of the space. 

- IfcMaterial + IfcMaterialConstituentSet: Used to determine the material of the walls of the spaces. The constituentset is further broken down in order to ascribe one material to the given wall. 

- IfcRelSpaceBoundary: An attribute type for the space which is found by utilizing the BoundedBy attribute. This makes it possible to identify the bounding walls of a space.

- Element types: Used in order to filter for the wanted space boundary (IfcWall) and retrieve data for the wanted elements such as spaces.

##### What needs advacement for this tool to be widely and easily used?

Many iterations and improvements could be made to this tool so that more materials in a building can be evaluated. This is first going to require more extensive off-gas testing of materials so that there is a database of input for these calculations. Further advancements may also be to include off-gassing from walls, ceilings and furniture to the calculations, and the ability to substitute materials in the calculation in order to assess material changes in the room. To further improve the calculations, proper modelling must also be done to include e.g. furniture and needed quantities assigned to all spaces in order to retrieve the surface areas.
