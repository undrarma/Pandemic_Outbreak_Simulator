# Cloud Computing Project #
This is the repository for the Cloud Computing project.

## Project First Draft  ##
### Functionality & Scope ###
The goal of our application is to simulate the behavior of a virus outbreak within the population of a given location. It will receive a list of parameters from the user, which it will use for setting up the simulation environment. Parameters to be received are the following:
-    Duration of the following virus stages:
    -   Incubation Stage
    -   Symptomatic Stage
    -   Duration of the infection fight
-	Mortality rate
-	Mean number of transmission events per hour
-	Duration of the simulation

After the user inputs such parameters, simulation will run for the defined period of time, during which a diagram will display the evolution of the virus outbreak. Users will have the opportunity to analyze how the spread of the virus is affected depending on certains parameters he/she defines. The logic behind how the simulation works is as follows: <br/> 
There’s a certain amount of actors (students, workers, elderly, etc…) within a location (housing , office, school, university, medical, recreational and transportation). In order for the virus spread to begin, we will define one of these actors as the “patient zero”. Such actors will have a defined agenda of activities that will be performed daily. These activities may vary (attending to school, work, supermarket, park, etc…).During these activities, the actors will change their location, therefore being exposed to have an interaction with other actors who may be infected. Those interactions will be recorded with anonymous keys (beacons) and eventually, once another actor is flagged as infected, its interactions with others will be retrieved to understand who else could get infected as well. As the simulation continues, the infected actors will go through the different disease stages, and eventually become cured or die.

#### Project Management ####
In order to advance on the project development, the tools that have been chosen to work are:
-	Github
-	Google Docs
-	Google Hangouts
-	Trello

###### Product Architecture
![Product Architecture](img/AWS Architecture.png)

The file 

**Virus Outbreak Simulation - Report.pdf**

contains an explanation about the architecture chosen and a final report regarding the outbreak simulator.