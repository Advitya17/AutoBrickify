
git clone https://gitlab.com/dzhong1989/hvac-safety-control.git --quiet

# Loads BD API
mv ./hvac-safety-control/building_depot src/building_depot

# Loads data
mv ./hvac-safety-control/CO2_data data

rm -rf ./hvac-safety-control
