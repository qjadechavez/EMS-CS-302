import pandas as pd
from datetime import datetime

# Define EMS units with updated Marikina Rescue 161 base location
EMS_UNITS = [
    {'ems_id': 1, 'type': 'Ambulance', 'base_latitude': 14.6628689, 'base_longitude': 121.1214235},
    {'ems_id': 2, 'type': 'Ambulance', 'base_latitude': 14.6628689, 'base_longitude': 121.1214235},
    {'ems_id': 3, 'type': 'Ambulance', 'base_latitude': 14.6628689, 'base_longitude': 121.1214235},
    {'ems_id': 4, 'type': 'Ambulance', 'base_latitude': 14.6628689, 'base_longitude': 121.1214235},
    {'ems_id': 5, 'type': 'Ambulance', 'base_latitude': 14.6628689, 'base_longitude': 121.1214235},
    {'ems_id': 6, 'type': 'Ambulance', 'base_latitude': 14.6628689, 'base_longitude': 121.1214235},
    {'ems_id': 7, 'type': 'Rescue', 'base_latitude': 14.6628689, 'base_longitude': 121.1214235},
    {'ems_id': 8, 'type': 'Rescue', 'base_latitude': 14.6628689, 'base_longitude': 121.1214235}
]
START_TIME = '2025-05-13 08:00:00'

# Generate EMS data
ems = [{'ems_id': unit['ems_id'], 'type': unit['type'], 'base_latitude': unit['base_latitude'], 
        'base_longitude': unit['base_longitude'], 'status': 'Available', 'last_available_time': START_TIME} 
       for unit in EMS_UNITS]

# Save to CSV
ems_df = pd.DataFrame(ems)
ems_df.to_csv('marikina_ems.csv', index=False)
print("EMS Dataset (Marikina Rescue 161):")
print(ems_df.to_string(index=False))