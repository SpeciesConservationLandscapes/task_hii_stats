HII STATS TASK
--------------

Task for calculating HII zonal stats. This task calls a function that runs `reduceRegion` with common 
zonal stats (minimum, maximum, mean, standard deviation, and sum / area) over the global aoi and over 
each country. Additional geographies can be easily be summarized using the same function.

## Usage

*All parameters may be specified in the environment as well as the command line.*

```
/app # python task.py --help
usage: task.py [-h] [-d TASKDATE] [--overwrite]

optional arguments:
  -h, --help            show this help message and exit
  -d TASKDATE, --taskdate TASKDATE
  --overwrite           overwrite existing outputs instead of incrementing

```

### License
Copyright (C) 2022 Wildlife Conservation Society
The files in this repository  are part of the task framework for calculating 
Human Impact Index and Species Conservation Landscapes (https://github.com/SpeciesConservationLandscapes) 
and are released under the GPL license:
https://www.gnu.org/licenses/#GPL
See [LICENSE](./LICENSE) for details.
