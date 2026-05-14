# MASA-DOC-005: Vicuña Module — Storage and Cargo Operations Manual

## Module Overview and Cargo Function

The Vicuña module serves as the primary storage and cargo bay for Kuntur Station, designed to accommodate incoming supply vessels, experimental payloads, and long-term storage of critical mission consumables. Unlike other modules such as Cóndor or Jaguar, Vicuña operates without permanent workstations or crew cabins, instead providing a flexible environment optimized for cargo handling and inventory management. The module supports a crew capacity of two personnel during active operations, typically Specialist Kai Nakamura and Specialist Fátima Al-Hassan, who are responsible for overseeing docking procedures, cargo transfers, and inventory updates in accordance with MASA-OPS-005 (Cargo Transfer and Inventory Update).

Vicuña's role extends beyond simple storage; it functions as the station's logistical hub, facilitating the distribution of supplies to other modules while maintaining environmental conditions suitable for both crew operations and sensitive cargo. The module's systems—including ventilation, heating, lighting, cooling, and filtration—are calibrated to sustain a stable environment for extended periods, even during undocked phases when the module operates in a quiescent state. This stability is critical, as Vicuña often houses perishable scientific samples, replacement parts for life-support systems, and other temperature-sensitive materials.

## Docking Port Specifications and Procedures

The Vicuña module features a single external docking port, compliant with MASA's standardized docking interface, which supports both automated and manual docking operations. The port is equipped with redundant sealing mechanisms to ensure pressure integrity during mating and demating sequences, a critical feature given the module's role in receiving external cargo vessels. Docking operations are governed by MASA-OPS-003 (Docking and Undocking Procedure), which mandates a series of pre-docking checks, including verification of pressure equalization, structural alignment, and communication link establishment between the station and the incoming vessel.

During docking, the Vicuña module's pressure must remain within the normal operational range of 99.0 kPa to 103.0 kPa to prevent stress on the docking seals. Any deviation below 95.0 kPa triggers a low-severity alert, prompting the crew to verify seal integrity and check for minor leaks. Should pressure drop further to 90.0 kPa, a medium-severity alert is issued, requiring immediate activation of the module's backup pressurization system. A critical condition is declared if pressure falls below 85.0 kPa, at which point MASA-SEC-001 (Rapid Decompression Response) is initiated, mandating immediate evacuation of the module and isolation of the docking port to prevent station-wide depressurization.

The docking port's structural integrity is continuously monitored for anomalies, with any deviation from expected parameters triggering MASA-SEC-008 (Structural Integrity Alert). This protocol ensures that any potential breaches or misalignments are addressed before they compromise the module's ability to maintain pressure or secure cargo.

## Cargo Bay Layout and Capacity

The Vicuña module's cargo bay is divided into three primary zones: the forward staging area, the central storage racks, and the aft equipment lockers. The forward staging area is designed for temporary storage of newly arrived cargo, allowing for immediate access during unpacking and distribution. This zone is equipped with adjustable restraint systems to secure payloads of varying sizes, ensuring stability during station maneuvers or microgravity operations.

The central storage racks occupy the majority of the module's volume, providing standardized shelving units that can be reconfigured to accommodate different cargo types. Each rack is labeled with a unique identifier, cross-referenced in the Inventory Management System (IMS), which tracks the location, quantity, and status of all stored items. The aft equipment lockers are reserved for high-value or sensitive equipment, such as scientific instruments or replacement life-support components, which require additional environmental controls or security measures.

Vicuña's total cargo capacity is designed to support up to six months of consumables for the station's full crew complement, including food, water, oxygen, and spare parts. The module's layout is optimized for efficient cargo transfer, with clear pathways and designated work areas to minimize the risk of damage to stored items during handling. The absence of permanent workstations or cabins allows for maximum utilization of the module's internal volume, though it also means that crew members must rely on portable equipment for any extended operations within Vicuña.

## Telemetry Specifications and Operational Ranges

### Temperature Monitoring and Control

Vicuña maintains a normal operating temperature range of 10.0°C to 35.0°C, which accommodates both crew comfort and the storage requirements of most cargo types. Temperatures exceeding 35.0°C but remaining below 45.0°C are classified as low-severity deviations, often attributable to transient heat loads from adjacent modules or temporary increases in crew activity. If temperatures rise to 55.0°C, a medium-severity alert is triggered, requiring the crew to inspect the module's cooling system and verify that ventilation is functioning correctly. A critical alert is issued at temperatures above 65.0°C, at which point MASA-SEC-003 (Fire and Thermal Runaway Suppression) is activated, mandating immediate evacuation and activation of the module's fire suppression systems.

### Pressure Management

Pressure within Vicuña is maintained between 99.0 kPa and 103.0 kPa under normal conditions. A drop below 95.0 kPa triggers a low-severity alert, prompting the crew to check for minor leaks or seal degradation. Further reductions to 90.0 kPa escalate the alert to medium severity, requiring activation of backup pressurization systems. Critical conditions are declared at pressures below 85.0 kPa, initiating MASA-SEC-001 (Rapid Decompression Response) to isolate the module and prevent station-wide depressurization.

### Oxygen Levels and Atmospheric Composition

Oxygen levels in Vicuña are maintained between 19.5% and 23.5% under normal conditions. A drop below 18.0% triggers a low-severity alert, while levels below 16.0% escalate to medium severity, requiring immediate corrective action. Critical conditions are declared at oxygen levels below 14.0%, activating MASA-SEC-002 (Oxygen Depletion Response) and mandating evacuation of the module. The module's filtration system is designed to maintain oxygen levels within the normal range, but crew intervention is required if deviations persist.

### Radiation Monitoring

Vicuña's radiation monitoring system ensures that exposure levels remain below 0.5 mSv/hour under normal conditions. A low-severity alert is triggered at 1.0 mSv/hour, prompting the crew to verify shielding integrity and check for external sources of radiation. Medium-severity alerts are issued at 2.0 mSv/hour, while high-severity alerts occur at 5.0 mSv/hour. Critical conditions are declared at radiation levels above 5.0 mSv/hour, activating MASA-SEC-004 (Radiation Lockdown Protocol) and requiring station-wide protective measures.

### Humidity Control

Humidity in Vicuña is maintained between 40% and 60% under normal conditions. Deviations into the 30%-39% or 61%-70% ranges trigger low-severity alerts, while medium-severity alerts are issued for humidity levels between 20%-29% or 71%-80%. High-severity alerts occur at humidity levels between 15%-19% or 81%-90%, with critical conditions declared at levels below 15% or above 90%. These thresholds are designed to prevent condensation on sensitive equipment or excessive dryness that could compromise stored materials.

### Power Management

Vicuña's power consumption is monitored as a percentage of rated capacity, with normal operations limited to 80% of capacity. A low-severity alert is triggered at 88% capacity, while medium-severity alerts occur at 93% capacity. High-severity alerts are issued at 97% capacity, with critical conditions declared above 97% capacity. These thresholds ensure that the module's power systems operate within safe limits, preventing overheating or system failures.

## Inventory Management System

The Inventory Management System (IMS) is the central database for tracking all cargo and supplies stored within Vicuña. The IMS is updated in real time during cargo transfer operations, with each item assigned a unique identifier, location, and status. The system is integrated with the station's broader logistics network, allowing crew members to query inventory levels, locate specific items, and generate reports for ground control.

Inventory updates are performed in accordance with MASA-OPS-005 (Cargo Transfer and Inventory Update), which mandates that all cargo transfers be logged immediately upon completion. The IMS also supports automated alerts for low stock levels, expired items, or misplaced cargo, ensuring that critical supplies are always available when needed. The system is backed up daily to prevent data loss, with redundant copies stored in both Vicuña and the Cóndor command module.

## Assigned Crew for Cargo Operations

Primary responsibility for cargo operations in Vicuña falls to Specialist Kai Nakamura and Specialist Fátima Al-Hassan, both of whom are assigned to the Quetzal module but spend significant time in Vicuña during active cargo operations. Their duties include overseeing docking procedures, managing cargo transfers, updating the Inventory Management System, and performing routine inspections of stored materials.

During off-shift hours, monitoring of Vicuña's systems reverts to the Cóndor command center under the supervision of Commander Santiago Reyes. The crew follows MASA-OPS-006 (Crew Shift Handoff) to ensure seamless transitions between shifts, with detailed logs of all cargo operations and system statuses provided during each handoff. This ensures that any anomalies or pending tasks are promptly addressed, maintaining the module's operational readiness at all times.

In the event of an emergency, such as a critical pressure drop or fire, the entire crew is trained to respond in accordance with the relevant protocols, ensuring that Vicuña's role as the station's logistical hub is never compromised. The module's design and the crew's training ensure that cargo operations proceed smoothly, supporting the station's broader mission objectives.