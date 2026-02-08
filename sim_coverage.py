"""
DISASTER RELIEF DRONE SIMULATION - NETWORK COVERAGE MAP
This file handles the 2D coverage map showing drone ranges, user connections, and service areas.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

from config_params import *

# INITIALIZATION
print("\n" + "="*60)
print("NETWORK COVERAGE MAP SIMULATION")
print("="*60)
print(f"Simulation Duration: {SIM_TIME} seconds (extended)")
print(f"Number of Drones: {NUM_DRONES}")
print(f"Coverage Radius: {COVERAGE_RADIUS}m")
print(f"Search Radius: {SEARCH_RADIUS}m")
print("="*60 + "\n")

current_time = 0
operator = OperatorNotification()
tower = Tower(TOWER_POSITION)
drones = initialize_drones()
users = initialize_users()
clusters_formed = {}
next_cluster_id = 0

# VISUALIZATION SETUP
fig, ax_coverage = plt.subplots(figsize=(14, 12))

ax_coverage.set_xlim(0, AREA_SIZE)
ax_coverage.set_ylim(0, AREA_SIZE)
ax_coverage.set_xlabel("X (m)", fontsize=14)
ax_coverage.set_ylabel("Y (m)", fontsize=14)
ax_coverage.set_title("Drone Coverage & Service Map", fontsize=18, fontweight='bold')
ax_coverage.set_aspect('equal')
ax_coverage.grid(True, alpha=0.3, linestyle='--')

# Status text
status_text = fig.text(0.5, 0.02, "", ha='center', fontsize=12,
                      bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))

# ANIMATION UPDATE FUNCTION
def animate(frame):
    global current_time, next_cluster_id
    current_time = frame
    
    # Run simulation step
    G, next_cluster_id = update_simulation(drones, users, tower, current_time, 
                                           clusters_formed, next_cluster_id, operator)
    
    alive_drones = [d for d in drones if d.alive]
    
    # Clear and redraw coverage map
    ax_coverage.clear()
    ax_coverage.set_xlim(0, AREA_SIZE)
    ax_coverage.set_ylim(0, AREA_SIZE)
    ax_coverage.set_xlabel("X (m)", fontsize=14)
    ax_coverage.set_ylabel("Y (m)", fontsize=14)
    ax_coverage.set_title("Drone Coverage & Service Map", fontsize=18, fontweight='bold')
    ax_coverage.set_aspect('equal')
    ax_coverage.grid(True, alpha=0.3, linestyle='--')
    
    # Draw 5G tower range (background)
    tower_range = Circle((TOWER_POSITION[0], TOWER_POSITION[1]), MAX_5G_RANGE,
                         fill=True, facecolor='purple', alpha=0.05,
                         edgecolor='purple', linewidth=2.5, 
                         linestyle='--', label='Tower Range')
    ax_coverage.add_patch(tower_range)
    
    # Draw coverage circles for each drone
    for d in alive_drones:
        if d.mode == "CLUSTER":
            color = 'blue'
            fill_alpha = 0.18
            edge_alpha = 0.6
            edge_width = 2
        else:
            color = 'red'
            fill_alpha = 0.12
            edge_alpha = 0.4
            edge_width = 1.8
            
        # Coverage circle
        circle = Circle((d.pos[0], d.pos[1]), COVERAGE_RADIUS, 
                       fill=True, facecolor=color, alpha=fill_alpha,
                       edgecolor=color, linewidth=edge_width, linestyle='-')
        ax_coverage.add_patch(circle)
        
        # Search radius (lighter, dashed)
        search_circle = Circle((d.pos[0], d.pos[1]), SEARCH_RADIUS, 
                              fill=False, edgecolor=color, linewidth=1.2, 
                              linestyle=':', alpha=0.35)
        ax_coverage.add_patch(search_circle)
    
    # Draw connection lines from users to drones
    for u in users:
        if u.served and u.connected_drone is not None:
            drone = drones[u.connected_drone]
            
            # Color by number of hops
            if u.hops_to_tower == 1:
                line_color = 'darkgreen'
                line_alpha = 0.5
                line_width = 1.5
            elif u.hops_to_tower == 2:
                line_color = 'green'
                line_alpha = 0.4
                line_width = 1.2
            else:
                line_color = 'yellowgreen'
                line_alpha = 0.3
                line_width = 1
            
            ax_coverage.plot([u.pos[0], drone.pos[0]], 
                           [u.pos[1], drone.pos[1]], 
                           color=line_color, alpha=line_alpha, 
                           linewidth=line_width, linestyle='-')
    
    # Categorize users
    undetected = [u for u in users if not u.detected]
    detected = [u for u in users if u.detected and not u.served]
    served = [u for u in users if u.served]
    
    # Draw users with size based on group size
    if undetected:
        sizes = [30 + u.group_size * 4 for u in undetected]
        ax_coverage.scatter([u.pos[0] for u in undetected], 
                          [u.pos[1] for u in undetected],
                          c='gray', s=sizes, alpha=0.7, 
                          edgecolors='black', linewidths=0.8, 
                          label=f'Undetected ({len(undetected)})')
    
    if detected:
        sizes = [40 + u.group_size * 4 for u in detected]
        ax_coverage.scatter([u.pos[0] for u in detected], 
                          [u.pos[1] for u in detected],
                          c='orange', s=sizes, marker='*', 
                          edgecolors='black', linewidths=0.8, 
                          label=f'Detected ({len(detected)})')
    
    if served:
        sizes = [50 + u.group_size * 4 for u in served]
        ax_coverage.scatter([u.pos[0] for u in served], 
                          [u.pos[1] for u in served],
                          c='green', s=sizes, marker='s', 
                          edgecolors='black', linewidths=0.8, 
                          label=f'Served ({len(served)})')
    
    # Draw drones with mode-based colors
    drone_colors = []
    drone_labels_map = {'SEARCH': 0, 'CLUSTER': 0, 'RELAY': 0}
    
    for d in alive_drones:
        if d.mode == "CLUSTER":
            drone_colors.append('blue')
            drone_labels_map['CLUSTER'] += 1
        elif d.mode == "RELAY":
            drone_colors.append('cyan')
            drone_labels_map['RELAY'] += 1
        else:
            drone_colors.append('red')
            drone_labels_map['SEARCH'] += 1
    
    if alive_drones:
        ax_coverage.scatter([d.pos[0] for d in alive_drones], 
                          [d.pos[1] for d in alive_drones],
                          c=drone_colors, s=200, marker='^', 
                          edgecolors='black', linewidths=2, zorder=5)
        
        # Add drone labels with battery percentage
        for d in alive_drones:
            battery_pct = (d.battery / BATTERY_INIT) * 100
            label_color = 'green' if battery_pct > 50 else ('orange' if battery_pct > 25 else 'red')
            
            ax_coverage.text(d.pos[0], d.pos[1]+25, 
                           f'D{d.id}\n{battery_pct:.0f}%', 
                           ha='center', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.4', 
                                   facecolor='white', 
                                   alpha=0.85, 
                                   edgecolor=label_color,
                                   linewidth=1.5))
    
    # Draw 5G Tower
    ax_coverage.scatter([TOWER_POSITION[0]], [TOWER_POSITION[1]], 
                       c='purple', s=500, marker='s', 
                       edgecolors='black', linewidths=3, 
                       label='5G Tower', zorder=10)
    ax_coverage.text(TOWER_POSITION[0], TOWER_POSITION[1]-30, 
                    '5G TOWER', ha='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='purple', 
                            alpha=0.3, edgecolor='purple', linewidth=2))
    
    # Create custom legend
    from matplotlib.lines import Line2D
    legend_elements = []
    
    # Add user status
    if undetected:
        legend_elements.append(Line2D([0], [0], marker='o', color='w', 
                                     markerfacecolor='gray', markersize=10,
                                     label=f'Undetected ({len(undetected)})'))
    if detected:
        legend_elements.append(Line2D([0], [0], marker='*', color='w', 
                                     markerfacecolor='orange', markersize=12,
                                     label=f'Detected ({len(detected)})'))
    if served:
        legend_elements.append(Line2D([0], [0], marker='s', color='w', 
                                     markerfacecolor='green', markersize=10,
                                     label=f'Served ({len(served)})'))
    
    # Add drone modes
    if drone_labels_map['SEARCH'] > 0:
        legend_elements.append(Line2D([0], [0], marker='^', color='w', 
                                     markerfacecolor='red', markersize=12,
                                     label=f'SEARCH ({drone_labels_map["SEARCH"]})'))
    if drone_labels_map['CLUSTER'] > 0:
        legend_elements.append(Line2D([0], [0], marker='^', color='w', 
                                     markerfacecolor='blue', markersize=12,
                                     label=f'CLUSTER ({drone_labels_map["CLUSTER"]})'))
    if drone_labels_map['RELAY'] > 0:
        legend_elements.append(Line2D([0], [0], marker='^', color='w', 
                                     markerfacecolor='cyan', markersize=12,
                                     label=f'RELAY ({drone_labels_map["RELAY"]})'))
    
    # Add tower
    legend_elements.append(Line2D([0], [0], marker='s', color='w', 
                                 markerfacecolor='purple', markersize=12,
                                 label='5G Tower'))
    
    ax_coverage.legend(handles=legend_elements, loc='upper right', 
                      fontsize=10, framealpha=0.95, edgecolor='black')
    
    # Update status bar
    alive_count = len(alive_drones)
    detected_people = sum(u.group_size for u in users if u.detected)
    served_people = sum(u.group_size for u in users if u.served)
    total_people = sum(u.group_size for u in users)
    total_throughput = sum(u.throughput for u in users)
    avg_battery = np.mean([d.battery for d in alive_drones]) if alive_drones else 0
    avg_throughput = total_throughput / len(served) if served else 0
    
    status_text.set_text(
        f"Time: {frame}s / {SIM_TIME}s  |  "
        f"Drones Active: {alive_count}/{NUM_DRONES}  |  "
        f"Avg Battery: {avg_battery:.0f}J ({100*avg_battery/BATTERY_INIT:.1f}%)  |  "
        f"Detection: {detected_people}/{total_people} ({100*detected_people/max(1,total_people):.1f}%)  |  "
        f"Service: {served_people}/{total_people} ({100*served_people/max(1,total_people):.1f}%)  |  "
        f"Total Throughput: {total_throughput:.1f} Mbps  |  "
        f"Avg per User: {avg_throughput:.1f} Mbps  |  "
        f"Clusters: {len(clusters_formed)}"
    )
    
    return ax_coverage,

# RUN ANIMATION
print("Starting coverage map visualization...")
print("- Shows drone coverage areas and service connections")
print("- Larger markers = larger groups of people")
print("- Lines connect served users to their serving drone")
print("- Colors indicate service status and drone modes")
print("="*60 + "\n")

ani = FuncAnimation(fig, animate, frames=range(0, SIM_TIME, DT),
                    interval=50, blit=False)

plt.tight_layout()
plt.show()

# FINAL STATISTICS
print("\n" + "="*60)
print("SIMULATION COMPLETE - COVERAGE MAP")
print("="*60)

final_detected = sum(u.group_size for u in users if u.detected)
final_served = sum(u.group_size for u in users if u.served)
total_people = sum(u.group_size for u in users)

print(f"\nFinal Statistics:")
print(f"  • Duration: {SIM_TIME}s")
print(f"  • Drones Survived: {sum(d.alive for d in drones)}/{NUM_DRONES}")
print(f"  • Average Battery Remaining: {np.mean([d.battery for d in drones if d.alive]):.0f}J")
print(f"  • Battery Utilization: {100*(1 - np.mean([d.battery/BATTERY_INIT for d in drones if d.alive])):.1f}%")
print(f"  • People Detected: {final_detected}/{total_people} ({100*final_detected/total_people:.1f}%)")
print(f"  • People Served: {final_served}/{total_people} ({100*final_served/total_people:.1f}%)")
print(f"  • Final Coverage Rate: {100*final_served/total_people:.1f}%")
print(f"  • Clusters Formed: {len(clusters_formed)}")
print(f"  • Total Alerts Sent: {len(operator.notifications)}")

# Network performance metrics
served_users = [u for u in users if u.served]
if served_users:
    avg_throughput = np.mean([u.throughput for u in served_users])
    avg_hops = np.mean([u.hops_to_tower for u in served_users])
    print(f"\nNetwork Performance:")
    print(f"  • Average Throughput: {avg_throughput:.2f} Mbps")
    print(f"  • Average Hops to Tower: {avg_hops:.2f}")
    print(f"  • Total Network Throughput: {sum(u.throughput for u in served_users):.1f} Mbps")

print("\nDetection Timeline (first 10 alerts):")
for i, notif in enumerate(operator.notifications[:10]):
    if 'group_size' in notif:
        print(f"  {i+1}. t={notif['time']:3d}s - Drone {notif['drone_id']} detected "
              f"{notif['group_size']} person(s)")

print("\n" + "="*60)
