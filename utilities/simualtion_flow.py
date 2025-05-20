import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyArrowPatch
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D

def create_ems_simulation_flow_diagram():
    """
    Creates a visual representation of the EMS system simulation flow
    """
    plt.figure(figsize=(14, 10))
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Define node positions for better layout
    pos = {
        "Setup Data": (0, 8),
        "Hospital Data": (2, 8),
        "Patient Data": (2, 7),
        "EMS Base Data": (2, 9),
        
        "Train Model": (4, 8),
        "Random Forest": (6, 8),
        "Model Evaluation": (8, 8),
        
        "Run Simulation": (0, 4),
        "Patient Input": (2, 4),
        "Find EMS Base": (4, 4),
        "Calculate Travel Time": (6, 4),
        "Hospital Selection": (8, 4),
        "Response Time": (10, 4),
        
        "Visualization": (6, 1),
        "HTML Map": (8, 1),
        "Route Display": (10, 1),
    }
    
    # Add nodes
    data_nodes = ["Hospital Data", "Patient Data", "EMS Base Data"]
    model_nodes = ["Train Model", "Random Forest", "Model Evaluation"]
    simulation_nodes = ["Run Simulation", "Patient Input", "Find EMS Base", "Calculate Travel Time", 
                        "Hospital Selection", "Response Time"]
    visualization_nodes = ["Visualization", "HTML Map", "Route Display"]
    
    all_nodes = ["Setup Data"] + data_nodes + model_nodes + simulation_nodes + visualization_nodes
    
    G.add_nodes_from(all_nodes)
    
    # Add edges
    edges = [
        ("Setup Data", "Hospital Data"),
        ("Setup Data", "Patient Data"),
        ("Setup Data", "EMS Base Data"),
        
        ("Hospital Data", "Train Model"),
        ("Patient Data", "Train Model"),
        ("Train Model", "Random Forest"),
        ("Random Forest", "Model Evaluation"),
        
        ("Run Simulation", "Patient Input"),
        ("Patient Input", "Find EMS Base"),
        ("EMS Base Data", "Find EMS Base"),
        ("Find EMS Base", "Calculate Travel Time"),
        ("Calculate Travel Time", "Hospital Selection"),
        ("Hospital Data", "Hospital Selection"),
        ("Random Forest", "Hospital Selection"),
        ("Hospital Selection", "Response Time"),
        
        ("Response Time", "Visualization"),
        ("Visualization", "HTML Map"),
        ("HTML Map", "Route Display"),
    ]
    
    G.add_edges_from(edges)
    
    # Node colors by category
    node_colors = []
    for node in G.nodes():
        if node == "Setup Data":
            node_colors.append("lightblue")
        elif node in data_nodes:
            node_colors.append("lightgreen")
        elif node in model_nodes:
            node_colors.append("orange")
        elif node in simulation_nodes:
            node_colors.append("lightcoral")
        elif node in visualization_nodes:
            node_colors.append("violet")
    
    # Draw the graph
    nx.draw_networkx(
        G, pos,
        node_color=node_colors,
        node_size=3000,
        font_size=10,
        font_weight='bold',
        arrowsize=20,
        width=2,
        edge_color='gray',
        with_labels=True,
    )
    
    # Add a legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=15, label='Initial Setup'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgreen', markersize=15, label='Data Sources'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=15, label='ML Model'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', markersize=15, label='Simulation Steps'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='violet', markersize=15, label='Visualization'),
    ]
    
    plt.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
    
    # Add title and description
    plt.title("EMS Route Optimization and Hospital Selection System Simulation Flow", fontsize=16)
    
    description = (
        "This diagram illustrates the flow of the EMS simulation system:\n"
        "1. Setup: Initialize hospital, patient, and EMS base data\n"
        "2. Training: Create and evaluate the Random Forest model for hospital selection\n"
        "3. Simulation: Process patient input, find nearest EMS, calculate routes using OpenRouteService API\n"
        "4. Visualization: Generate interactive HTML maps showing the complete emergency route"
    )
    
    plt.figtext(0.5, -0.1, description, ha="center", fontsize=12, bbox={"facecolor":"white", "alpha":0.5, "pad":5})
    
    plt.tight_layout()
    plt.savefig("D:\\Documents\\Python\\EMS\\utilities\\simulation_flow_diagram.png", bbox_inches="tight", dpi=300)
    plt.close()
    
    print("Simulation flow diagram created and saved to D:\\Documents\\Python\\EMS\\utilities\\simulation_flow_diagram.png")

# Detailed flow description as multi-line string
simulation_flow_description = """
# EMS Route Optimization and Hospital Selection System: Simulation Flow

## 1. Data Setup Phase
- **Hospital Data**: Initialized from known locations in Marikina with fallback to OpenStreetMap data
- **Patient Data**: Generated with various medical conditions and severity levels
- **EMS Base Data**: Multiple ambulance bases across Marikina with geographic coordinates

## 2. Machine Learning Model Training
- **Dataset Creation**: Combines patient and hospital data with calculated distances
- **Random Forest Model**: Trained to predict the optimal hospital based on:
  - Patient location (latitude/longitude)
  - Medical condition and severity
  - Travel distances and times
- **Model Evaluation**: Tested for accuracy and cross-validated

## 3. Simulation Execution
- **Patient Input**: User provides location, severity, and condition
- **EMS Base Selection**: Finds the closest available ambulance
- **Route Calculation**: Uses OpenRouteService API to calculate:
  - EMS base to patient route
  - Patient to hospital route
- **Hospital Selection**: Uses the ML model to recommend the most appropriate hospital
- **Response Time Calculation**: Breaks down the full emergency response timeline
  - Dispatch time (2 min)
  - Travel to patient time (variable)
  - On-scene care time (10 min)
  - Transport to hospital time (variable)
  - Hospital handover time (5 min)

## 4. Visualization
- **Map Generation**: Creates an interactive HTML map using Folium
- **Route Display**: Shows the full emergency route with:
  - EMS base marker (red)
  - Patient location marker (blue)
  - Hospital marker (green)
  - Route lines with time information
- **Information Panel**: Displays all timing and emergency details

## 5. Data Flow Between Components
- temp_route_data.json: Transfers route information between prediction and visualization
- marikina_hospitals.csv: Stores hospital location and level data
- hospital_prediction_model.pkl: Saved machine learning model for hospital predictions
"""

if __name__ == "__main__":
    # Create the visual diagram
    create_ems_simulation_flow_diagram()
    
    # Save the detailed text description
    with open("D:\\Documents\\Python\\EMS\\utilities\\simulation_flow_description.md", "w") as f:
        f.write(simulation_flow_description)
    
    print("Simulation flow description saved to D:\\Documents\\Python\\EMS\\utilities\\simulation_flow_description.md")