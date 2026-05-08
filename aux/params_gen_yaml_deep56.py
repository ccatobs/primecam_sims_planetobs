import argparse
import yaml
import subprocess

# Set up argument parser
parser = argparse.ArgumentParser(description="Generate YAML configuration file for Horizontal Scans",
        epilog="The schedule out-filename is based on patch name and first day of schedule")
parser.add_argument("start", help="Start time of Schedule config file")
parser.add_argument("stop", help="Stop time of Schedule config file")
parser.add_argument("patch_name", help="Name of the patch; Format: FieldName_eELR_MM_DD")
parser.add_argument("--params_yaml", default="params.yaml", help="Output YAML file name")

# Parse the command line arguments
args = parser.parse_args()

start_time = args.start
mm_dd = start_time.split(" ")[0][-5:].replace("-","_")
patch_name = args.patch_name.upper() + f"_{mm_dd}"
el_direction = (patch_name).split("_")[1]
#print(patch_name, el_direction)

patch_args = None #Format: "azmin, azmax, el"
if el_direction=="E50S":
    patch_args="283,309,50"
elif el_direction=="E50R":
    patch_args="50,76,50"

elif el_direction=="E60S":
    patch_args="292,335,60"
elif el_direction=="E60R":
    patch_args="24,67,60"
else:
    raise RuntimeError("Incorrect el_direction format. Required example: e50R")

out_yaml = f"schedule_{patch_name}.txt"

#patch = HorizontalPatch(name,HORIZONTAL, weight, azmin, azmax, el, scantime)

#"--boresight-offset-az-deg", "0.6",
#"--boresight-offset-el-deg", "1.7",

#For Deep56 Horizontal scans format
# Construct the list of configuration items
config_items = \
["--site-lat", "-22.9855235",
"--site-lon", "-67.7403087",
"--site-alt", "5610",
"--site-name", "Cerro-Chajnantor",
"--telescope", "FYST",
"--patch-coord", "C",
"--start", args.start,
"--stop", args.stop,
"--patch", f"{patch_name},HORIZONTAL,1,{patch_args},30",
"--el-min-deg", "30",
"--el-max-deg", "70",
"--sun-avoidance-angle-deg", "35",
"--ces-max-time-s", "1800",
"--fp-radius-deg", "0.0",
"--gap-s", "0.0",
"--gap-small-s" , "0.0",
"--lock-az-range",
"--no-partial-scans",
"--out", f"./gen_schedules/{out_yaml}",]

# Write the configuration to a YAML file
with open(args.params_yaml, 'w') as yaml_file:
    yaml.dump(config_items, yaml_file, default_flow_style=False)

print(f"Config for writing schedule to: {out_yaml}")

# After writing the YAML file, call/run another python script
subprocess.run(["python", "make_schedule_files.py"])
