# MASA-DOC-008: Thermal and Fire Safety Protocols

## Protocol Overview

Thermal management and fire safety represent the most time-critical emergency domains aboard Kuntur Station. The closed environment at 408 km altitude, combined with the high energy density of life-support and propulsion systems, demands a layered response framework that begins with continuous telemetry monitoring and culminates in automated suppression and evacuation. This document consolidates all thermal and fire-related protocols, thresholds, and procedural responses into a single operational reference for flight controllers, engineers, and crew.

The primary protocol governing thermal emergencies is MASA-SEC-003 (Fire and Thermal Runaway Suppression), which activates at critical severity whenever a fire sensor returns a positive reading or when the temperature rise rate exceeds 2.0 °C per minute. This rate-of-change threshold was selected because it indicates an uncontrolled exothermic reaction—such as a lithium-ion battery failure or a short-circuit in high-power distribution lines—rather than a gradual thermal drift that might be managed through passive cooling adjustments. The 2.0 °C/minute figure is derived from ground-based thermal runaway tests conducted on identical hardware, where sustained rates above this value consistently led to catastrophic failure within a short time. Therefore, any detection of this rate triggers an immediate, module-wide critical response.

While MASA-SEC-003 is the only protocol with a dedicated thermal trigger, its activation intersects with other critical protocols. For instance, a fire in the Jaguar module could compromise oxygen generation, potentially triggering MASA-SEC-002 (Oxygen Depletion Response) if oxygen levels drop below 14.0%. Similarly, a thermal event in the Cóndor command center could disrupt station-wide communications, escalating to MASA-SEC-007 (Communication Blackout Protocol) if redundancy systems fail. Thus, thermal safety is not an isolated concern but a cross-cutting risk that must be managed in concert with atmospheric control, power distribution, and data integrity.

## MASA-SEC-003: Fire and Thermal Runaway Suppression

MASA-SEC-003 (Fire and Thermal Runaway Suppression) is the sole protocol dedicated to thermal emergencies and is triggered under two conditions: a confirmed positive reading from any of the station’s distributed fire sensors, or a temperature rise rate exceeding 2.0 °C per minute within any module. The 2.0 °C/minute threshold is not arbitrary; it represents the point at which passive cooling measures—such as increasing radiator flow or reducing equipment load—can no longer arrest the temperature climb. Beyond this rate, thermal inertia ensures that the module will reach critical material failure temperatures within minutes, necessitating immediate suppression and evacuation.

Upon activation, the protocol enforces a five-step response sequence that must be executed in under a short time to prevent cascading failures. First, the fire suppression system in the affected module is activated automatically, releasing a gaseous mixture of nitrogen and argon to displace oxygen and starve the fire. Second, ventilation to the module is cut to prevent oxygen replenishment and smoke propagation. Third, all crew members within the module must evacuate immediately via predefined routes. Fourth, a critical alert is transmitted to both the Cóndor command center and MASA Mission Control in Lima, triggering station-wide audio alarms and visual strobes. Fifth, the module is sealed via automated hatch closure to contain the event.

The protocol’s scope is module-only, meaning that while the response is critical, it does not automatically trigger station-wide lockdowns such as those seen in MASA-SEC-004 (Radiation Lockdown Protocol). However, if the fire occurs in a central module like Cóndor or Jaguar, the Commander or Engineer may escalate to MASA-SEC-020 (Emergency Station Evacuation) if structural integrity is compromised or if multiple modules are at risk.

Crew responsibilities under MASA-SEC-003 are clearly delineated by shift and role. During the day shift, Systems Engineer Pavel Kozlov serves as the primary responder for any thermal event in the Jaguar module, while Commander Santiago Reyes oversees station-wide coordination from Cóndor. During the night shift, responsibility shifts to Medical Officer Lucía Mendoza in Tucán, who is trained to initiate suppression in any module while awaiting backup from the on-call engineer. All crew members undergo quarterly drills under MASA-OPS-015 (Emergency Drill) to ensure familiarity with suppression equipment and evacuation paths.

## Module-Specific Temperature Critical Thresholds

While MASA-SEC-003 is triggered by rate of change, each module also has a static critical temperature threshold that, if reached, indicates imminent structural or system failure. These thresholds are not triggers for MASA-SEC-003 but serve as secondary indicators that a thermal event is already in progress and that suppression may be too late to prevent damage.

The Cóndor module, housing the command center and primary life-support systems, has a critical threshold of 55.0 °C. This value is based on the thermal tolerance of the station’s central processing units and communication arrays, which begin to exhibit data corruption and hardware degradation above 50.0 °C. The additional 5.0 °C margin accounts for thermal lag in sensor readings and the time required for crew response.

The Quetzal laboratory module, where most scientific experiments are conducted, has a critical threshold of 60.0 °C. This reflects the presence of volatile chemical storage and sensitive instrumentation that can be permanently damaged by sustained exposure above 55.0 °C. The threshold is set conservatively to protect irreplaceable research equipment and prevent the release of hazardous materials.

The Jaguar module, responsible for power distribution and oxygen generation, has the lowest critical threshold at 50.0 °C—10.0 °C lower than Quetzal. The operational implications of a thermal event in Jaguar are the most severe on the station: it could disrupt power to the entire station, potentially triggering MASA-SEC-006 (Power Grid Critical Failure). The lower threshold also accounts for the proximity of high-voltage distribution lines, which can arc and ignite surrounding materials if temperatures exceed design limits.

The Colibrí communications module, used for navigation and long-range antenna operations, has the highest critical threshold at 65.0 °C. This reflects its simpler systems and the fact that it is often unoccupied during non-communication periods. However, during active orbital adjustment maneuvers under MASA-OPS-007, the threshold is effectively reduced to 55.0 °C due to the increased thermal load from navigation computers and the need to protect sensitive antenna calibration equipment.

The Vicuña storage and cargo module, which houses the external docking port and serves as the primary cargo bay, has a critical threshold of 65.0 °C—matching Colibrí as the highest on the station. This reflects its lower equipment density and the fact that it is often used for storage of temperature-tolerant materials. However, the threshold must be considered in conjunction with the thermal sensitivity of any active cargo, particularly biological samples or fuel cells being stored for transfer.

The Tucán medical module, where Medical Officer Lucía Mendoza conducts examinations and stores pharmaceuticals, has the most stringent threshold at 52.0 °C—just 2.0 °C above Jaguar. This reflects the temperature sensitivity of medical supplies, particularly vaccines and biological samples, which can degrade rapidly above 45.0 °C. The threshold is set to ensure that even a slow thermal rise is caught before critical medical assets are compromised.

## Fire Suppression System Locations

Fire suppression systems are strategically placed in each module to ensure rapid response to any ignition source. Each system consists of a pressurized canister containing a nitrogen-argon gas mixture, designed to displace oxygen without introducing toxic byproducts or residue that could damage sensitive equipment.

In the Cóndor module, two suppression canisters are located in the overhead service bay above the command console, with a third positioned near the primary life-support rack. This redundancy ensures that a fire in either the command or life-support section can be addressed without requiring crew to traverse the module during an emergency.

The Quetzal module houses three suppression canisters: one in the central experiment bay, one near the chemical storage locker, and one adjacent to the high-power laser optics bench. The placement reflects the higher risk of ignition in areas with volatile materials and high-energy equipment.

Jaguar contains four suppression canisters—the highest density on the station—due to its role in power distribution. Canisters are positioned at each of the four main bus tie points, ensuring that an electrical fire can be suppressed before it propagates through the power grid. Additionally, a manual override panel is located at the module’s entrance, allowing crew to trigger suppression even if the automated system fails.

Colibrí’s suppression system is simpler, with two canisters: one in the docking adapter and one in the cargo transfer vestibule. This reflects the module’s intermittent occupancy and lower equipment density. However, during docking operations, an additional portable suppression unit is staged in the vestibule as part of MASA-OPS-003 (Docking and Undocking Procedure).

Vicuña and Tucán each have two suppression canisters. In Vicuña, they are located in the galley and the sleep quarters, addressing the two highest-risk areas for accidental ignition. In Tucán, one canister is positioned near the medical storage refrigerator, and the other is in the examination bay, protecting both equipment and crew during medical procedures.

## Evacuation Routes per Module

Evacuation routes are designed to provide at least two egress paths from any point in a module, ensuring redundancy in case one path is blocked by fire or debris. Routes are marked with photoluminescent striping and backed by audio cues from the station’s emergency alert system.

In Cóndor, the primary evacuation route leads directly to the central hub, while the secondary route exits through the aft maintenance tunnel into Jaguar. This dual-path design ensures that crew can escape even if the main hatch is compromised.

Quetzal’s evacuation routes are similarly redundant. The primary path exits through the forward hatch into the central hub, while the secondary path leads through the experiment airlock into the external truss—though this route is only used if the forward hatch is inaccessible, as it requires donning emergency oxygen masks.

Jaguar’s evacuation is complicated by its central location. The primary route exits into the hub, while the secondary route leads into Cóndor via the maintenance tunnel. Crew are trained to use the tunnel only if the hub is blocked, as it requires navigating a narrow passage with limited visibility.

Colibrí’s evacuation routes depend on docking status. When undocked, the primary route exits into the hub, and the secondary route leads into Vicuña. During docking, the primary route remains the same, but the secondary route is temporarily rerouted through the docking adapter to the visiting vehicle if it is pressurized and safe.

Vicuña and Tucán share a common evacuation strategy. Both modules have primary routes leading directly into the hub, with secondary routes connecting Vicuña to Colibrí and Tucán to Jaguar. This cross-module redundancy ensures that crew can always reach a safe haven even if the hub is compromised.

## Post-Fire Assessment Procedures

Once a fire has been suppressed and the module evacuated, a structured assessment protocol begins to determine the extent of damage and the feasibility of reoccupying the space. This process is governed by MASA-OPS-010 (Life Support Maintenance) and involves both automated telemetry analysis and manual inspection.

The first step is atmospheric sampling. Remote sensors measure oxygen, CO₂, and particulate levels to confirm that the suppression gas has dispersed and that the air is safe to breathe. Oxygen levels must return to at least 19.5% before crew can re-enter, and CO₂ must be below 1.0% to prevent respiratory distress.

The second step is thermal imaging. Infrared cameras mounted in adjacent modules scan the affected area to identify hot spots that could reignite. Any surface temperature above 40.0 °C is considered a potential reignition risk and must be cooled before further assessment.

The third step is structural integrity verification. Crew use ultrasonic sensors to check for warping or weakening in bulkheads and hatches. Particular attention is paid to hatch seals, as a compromised seal could lead to a secondary emergency under MASA-SEC-017 (Airlock Seal Failure Protocol).

The fourth step is equipment functionality testing. Life-support systems, power distribution nodes, and communication arrays are powered up in stages to ensure no latent damage exists. This phase is conducted under the supervision of the Engineer, with backup power available in case of cascading failures.

The final step is documentation and reporting. All findings are logged in the station’s maintenance system, and a detailed report is transmitted to MASA Mission Control. If damage exceeds predefined thresholds—such as loss of a significant portion of a module’s life-support capacity—the station may initiate MASA-SEC-020 (Emergency Station Evacuation) until repairs can be effected.

Throughout the assessment, crew adhere to strict safety protocols. No single crew member enters the affected module alone, and all personnel wear emergency oxygen masks until atmospheric readings are confirmed safe. The process is overseen by the Commander, with the Medical Officer standing by to treat any smoke inhalation or heat exposure injuries.

In summary, thermal and fire safety aboard Kuntur Station is a multi-layered discipline that integrates automated suppression, crew training, and structured recovery procedures. By adhering to the protocols and thresholds outlined in this document, MASA ensures that thermal emergencies are contained rapidly and that the station remains a safe environment for scientific research and human habitation.