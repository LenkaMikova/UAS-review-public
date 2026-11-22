# Full OpenSkyLab / ASPRS metadata matrix (not the printed OR)

Printed Online Resource 16 is the 25-item paper checklist (Layer 1) in _online-resources.qmd.
This file keeps Tables 1–10 as the Layer 2 dataset schema.

**Paper L1 keys (keep in OR 16):** spatial_extent, temporal_extent, start_utc / end_utc, platform_model, sensor_type, sensor_model, bands, nominal_agl, gnss_mode, flight_pattern, overlap_forward, overlap_side, gsd_nominal, panel_reflectance, drift_protocol, distortion_model, software, gcp_survey_method, checkpoint_count, reported_rmse_horizontal, dataset_id, licence, known_issues, weather_source, product_type.

::: {#or-metadata}

**Table 1. Dataset Identification and Publication Metadata**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `dataset_id` | OpenSkyLab | **Core (C)** | String (DOI / URL) | `10.5281/zenodo.10123456` | Persistent Identifier (PID) assigned to the published dataset for citation and FAIR data discovery. |
| `title` | OpenSkyLab | **Core (C)** | String | `UAV Multispectral and Thermal Soil Moisture Dataset - Marquardt 2026` | Concise, descriptive title of the dataset for cataloging and scientific indexing. |
| `abstract` | OpenSkyLab | **Core (C)** | Text | `High-resolution UAV multispectral, thermal LWIR, and ground-truth soil moisture measurements collected over agricultural fields...` | Detailed summary describing measured variables, site location, experimental objectives, sensors, and data limitations. |
| `version` | OpenSkyLab | **Core (C)** | String (SemVer) | `1.0.0` \| `1.1.0` \| `2.0.0` | Semantic versioning number tracking data revisions, re-calibrations, and re-processing iterations. |
| `creators` | OpenSkyLab | **Core (C)** | Array of JSON | `[{"name": "Jan Novák", "orcid": "0000-0002-1825-0097", "affiliation": "Czech Technical University in Prague"}]` | List of authors and data curators including full names, ORCID identifiers, and institutional affiliations. |
| `contact` | OpenSkyLab | **Core (C)** | String (E-mail) | `jan.novak@fsv.cvut.cz` | Official contact e-mail address of the corresponding author or data steward. |
| `publication_date` | OpenSkyLab | **Core (C)** | String (ISO 8601) | `2026-06-15` | Official publication date of the dataset in a data repository. |
| `licence` | OpenSkyLab | **Core (C)** | String (SPDX) | `CC-BY-4.0` \| `CC0-1.0` \| `MIT` \| `ODC-By-1.0` | Legal licensing framework dictating data re-use rights and attribution requirements. |
| `access_conditions` | OpenSkyLab | **Core (C)** | Text | `Open Access` \| `Embargoed until 2027-01-01` \| `Restricted to research partners` | Terms of access, embargo periods, or specific conditions for data usage. |
| `spatial_extent` | OpenSkyLab | **Core (C)** | Array (EPSG:4326) | `[12.8451, 49.5123, 12.8590, 49.5210]` | Geographic Bounding Box (West, South, East, North) in decimal degrees. |
| `temporal_extent` | OpenSkyLab | **Core (C)** | String (ISO 8601) | `2026-06-12T08:30:00Z/2026-06-12T14:15:00Z` | Start and end timestamp of data acquisition in UTC. |
| `missions` | OpenSkyLab | **Core (C)** | Array of Strings | `["MARQUARDT-20260612-MS", "MARQUARDT-20260612-TIR"]` | List of unique flight mission identifiers (`mission_id`) included in the dataset. |
| `profile` | OpenSkyLab | **Core (C)** | Categorical | `core` \| `quantitative` \| `full` | Metadata completeness level declared according to the OpenSkyLab profile schema. |
| `sensitivity` | OpenSkyLab | **Core (C)** | Text | `Non-sensitive` \| `Contains GDPR-compliant pilot logs` \| `Protected fauna area` | Declaration of sensitive content (personal data, privacy, protected species, restricted zones). |
| `keywords` | OpenSkyLab | **Full (F)** | Array of Strings | `["soil moisture", "UAV", "multispectral", "precision agriculture", "ASPRS 2024"]` | Controlled vocabulary and free-text keywords for domain-specific indexing and searchability. |
| `topic_category` | OpenSkyLab | **Full (F)** | Categorical | `farming` \| `environment` \| `imageryBaseMapsEarthCover` \| `geoscientificInformation` | ISO 19115 topic category for international spatial metadata catalogs. |
| `related_publications` | OpenSkyLab | **Full (F)** | Array of DOIs/URLs | `["10.1016/j.agwat.2026.108123"]` | Cross-references to peer-reviewed articles or technical reports utilizing this dataset. |
| `known_issues` | OpenSkyLab | **Full (F)** | Text | `Minor cloud shadows on Eastern flight transect at 10:14 UTC` \| `Camera 3 thermal drift uncompensated` | Explicit documentation of data artifacts, sensor anomalies, uncorrected atmospheric effects, or alignment errors. |
| `care_statement` | OpenSkyLab | **Full (F)** | Text | `Data collected with formal consent from Marquardt Agricultural Cooperative` | Statement confirming adherence to CARE principles regarding Indigenous data governance and local community rights. |
| `funding` | OpenSkyLab | **Optional (O)** | Text | `Czech Science Foundation (GACR), Grant No. 24-12345S` | Funding agency, grant identifier, and project title supporting data acquisition. |

**Table 2. Flight Mission Identification and Operation Protocols**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `mission_id` | OpenSkyLab | **Core (C)** | String | `MARQUARDT-20260612-01` | Unique alphanumeric identifier assigned to a single UAV flight campaign. |
| `start_utc` / `end_utc` | OpenSkyLab | **Core (C)** | String (ISO 8601) | `2026-06-12T09:15:22Z` / `2026-06-12T09:42:10Z` | Precise UTC timestamps marking the start and end of image acquisition. |
| `site_name` | OpenSkyLab | **Core (C)** | String | `Marquardt Research Cluster - Plot B` | Geographic or agricultural plot name designating the study area. |
| `site_centroid` | OpenSkyLab | **Core (C)** | Array (WGS84) | `[52.421102, 12.961055]` | WGS84 coordinates (Latitude, Longitude) of the study area centroid. |
| `operator` | OpenSkyLab | **Core (C)** | String | `OpenSkyLab Pilot Team / Op-ID: CZE-OP-123456789` | Flight operator name, institution, or official pilot registration identifier. |
| `sensor_ids` | OpenSkyLab | **Core (C)** | Array of Strings | `["SENS_MICASENSE_P01", "SENS_FLIR_TAU2_02"]` | List of sensor IDs deployed on the UAV payload during the mission. |
| `nominal_agl` | OpenSkyLab / ASPRS | **Core (C)** | Float (m AGL) | `50.0` \| `80.0` \| `100.0` | Planned flying altitude Above Ground Level (AGL), governing Ground Sample Distance (GSD) and optical footprint. |
| `gnss_mode` | OpenSkyLab / ASPRS | **Core (C)** | Categorical | `single` \| `DGNSS` \| `RTK` \| `PPK` | Onboard positioning mode dictating direct georeferencing quality. |
| `flight_pattern` | OpenSkyLab | **Quantitative (Q)** | Categorical | `single_grid` \| `double_grid` \| `linear` \| `circular` \| `manual` | Flight line geometry executed over the site. |
| `nominal_ground_speed` | OpenSkyLab | **Quantitative (Q)** | Float (m/s) | `4.5` \| `6.0` \| `8.0` | Planned aircraft ground speed influencing motion blur and exposure frequency. |
| `overlap_forward` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Float (%) | `80.0` \| `85.0` | Longitudinal image overlap along the flight path (crucial for SfM keypoint matching). |
| `overlap_side` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Float (%) | `75.0` \| `80.0` | Lateral overlap between adjacent flight transects (sidelap). |
| `gsd_nominal` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Float (cm/px) | `1.2` \| `2.5` \| `4.0` | Theoretical spatial resolution calculated from altitude, focal length, and sensor pixel size. |
| `gimbal_pitch_nominal` | OpenSkyLab | **Quantitative (Q)** | Float (degrees) | `-90.0` (nadir) \| `-60.0` (oblique) | Planned camera pitch angle (-90° indicates vertical nadir orientation). |
| `time_sync_method` | OpenSkyLab | **Quantitative (Q)** | Categorical | `hardware_trigger_event` \| `software_timestamp` \| `none` | Synchronization mechanism between camera exposure events and GNSS/IMU logs. |
| `gnss_correction_source` | OpenSkyLab | **Quantitative (Q)** | Text | `CZEPOS NTRIP VRS` \| `Local Base Station Topcon GR-5` \| `EGNOS` | Source of differential corrections used for RTK/PPK processing. |
| `n_images` | OpenSkyLab | **Quantitative (Q)** | Integer | `342` \| `1250` | Total count of raw images captured per band during the mission. |
| `purpose` | OpenSkyLab | **Full (F)** | Text | `Validation of UAV-based soil moisture retrieval algorithms` | Research objective or operational goal of the flight mission. |
| `authorisation` | OpenSkyLab | **Full (F)** | Text | `EASA Specific Category / LUC Authorisation No. CZ-LUC-004` | Regulatory flight permit, EASA category (`Open` \| `Specific` \| `Certified`), and permit number. |
| `trigger_mode` | OpenSkyLab | **Full (F)** | Categorical | `distance` \| `time` \| `manual` | Exposure trigger criterion executed by the flight controller. |
| `sop_reference` | OpenSkyLab | **Full (F)** | Text / URL | `OpenSkyLab SOP v2.1 ([suspicious link removed])` | Reference to Standard Operating Procedures or institutional protocols. |
| `planning_software` | OpenSkyLab | **Full (F)** | String | `DJI Pilot 2 v5.1` \| `UGCS v4.12` \| `Mission Planner v1.3.8` | Mission planning software name and software version. |
| `terrain_following` | OpenSkyLab | **Full (F)** | Boolean + Text | `true (using SRTM 30m DEM)` | Indicates if adaptive terrain-following flight was executed, along with DEM source. |
| `time_sync_offset` | OpenSkyLab | **Full (F)** | Float (s) | `0.002` \| `-0.015` | Residual time offset between exposure signal and GNSS/IMU log timestamp. |
| `antenna_camera_offset` | OpenSkyLab / ASPRS | **Full (F)** | Array (m) | `[0.05, -0.02, 0.18]` | Lever arm offset vector (\\(X, Y, Z\\)) between GNSS phase center and camera projection center. |
| `gcp_count` | OpenSkyLab / ASPRS | **Full (F)** | Integer | `0` \| `8` \| `15` \| `24` | Total number of Ground Control Points (GCPs) surveyed and used in block adjustment. |
| `gcp_survey_method` | OpenSkyLab / ASPRS | **Full (F)** | Text | `RTK-GNSS in CZEPOS network (RMSE_H < 1.0 cm, RMSE_V < 1.5 cm)` | Geodetic surveying technique used for GCP acquisition and reported survey accuracy. |
| `checkpoint_count` | OpenSkyLab / ASPRS | **Full (F)** | Integer | `0` \| `12` \| `30` \| `42` | Number of independent Checkpoints withheld from block adjustment for accuracy testing. |
| `flight_log_ref` | OpenSkyLab | **Full (F)** | File / URL | `logs/20260612_FLY342.DAT` | File reference to raw telemetry flight logs (`.DAT`, `.LOG`, or `.BIN`). |
| `notes` | OpenSkyLab | **Optional (O)** | Text | `Wind gusts up to 7 m/s at 10:20 UTC; flight altitude held stable` | Field observations, weather anomalies, or unexpected telemetry events during flight. |

**Table 3. Platform and Sensor Payload Specifications**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `platform_model` | OpenSkyLab / ASPRS | **Core (C)** | String | `DJI Matrice 300 RTK` \| `DJI Mavic 3 Enterprise` \| `SenseFly eBee X` | Manufacturer and model name of the UAV aircraft platform. |
| `sensor_id` | OpenSkyLab | **Core (C)** | String | `SENS_MICASENSE_REDEDGE_P` | Unique identifier assigned to the sensor payload within the dataset. |
| `sensor_model` | OpenSkyLab / ASPRS | **Core (C)** | String | `MicaSense RedEdge-P` \| `FLIR Tau 2 640` \| `Headwall Nano-Hyperspec` | Manufacturer and model name of the imaging sensor. |
| `sensor_type` | OpenSkyLab | **Core (C)** | Categorical | `RGB` \| `multispectral` \| `thermal_LWIR` \| `hyperspectral` \| `lidar` | Physical classification of the remote sensing payload. |
| `image_size` | OpenSkyLab | **Core (C)** | String (px x px) | `1456 x 1088` \| `2048 x 1536` \| `640 x 512` | Sensor array dimensions in pixels (Width × Height). |
| `bands` | OpenSkyLab | **Core (C)** | Array / Integer | `["Blue", "Green", "Red", "RedEdge", "NIR"]` \| `5` | Number and nomenclature of registered spectral bands. |
| `firmware` | OpenSkyLab | **Quantitative (Q)** | String | `v07.02.00` \| `v1.4.12` | Firmware version installed on the sensor during acquisition. |
| `sensor_serial` | OpenSkyLab | **Quantitative (Q)** | String | `REP-2104512-SE` | Hardware serial number for linking to factory calibration sheets. |
| `bit_depth` | OpenSkyLab | **Quantitative (Q)** | Integer (bits) | `12` \| `14` \| `16` | Dynamic range and quantization houghness per pixel. |
| `field_of_view` | OpenSkyLab / ASPRS | **Quantitative (Q)** | String (degrees) | `47.2 x 35.4` \| `50.0 x 38.0` | Angular Field of View (Horizontal × Vertical FOV). |
| `nominal_focal_length` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Float (mm) | `5.4` \| `8.0` \| `13.0` | Manufacturer-stated nominal lens focal length. |
| `calibration_date` | OpenSkyLab / ASPRS | **Quantitative (Q)** | String (ISO 8601) | `2025-11-10` | Date of last laboratory or factory geometric/radiometric calibration. |
| `calibration_provider` | OpenSkyLab | **Quantitative (Q)** | String | `MicaSense Inc. Factory Lab` \| `CTU Photogrammetric Lab` \| `Self-Calibration` | Entity that performed sensor calibration. |
| `platform_serial` | OpenSkyLab | **Optional (O)** | String | `1Z3DFG45678901234` | Aircraft frame serial number. |
| `gimbal_model` | OpenSkyLab | **Optional (O)** | String | `DJI Zenmuse H20T Gimbal` | Gyro-stabilized mount model name. |
| `boresight_angles` | OpenSkyLab / ASPRS | **Optional (O)** | Array (degrees) | `[0.12, -0.24, 0.05]` | Calibrated angular misalignments (Roll, Pitch, Yaw) between IMU and camera axes. |
| `boresight_method` | OpenSkyLab / ASPRS | **Full (F)** | Text | `Boresight flight over calibration field with 20 3D GCPs` | Experimental protocol used to determine boresight angles. |
| `instrument_pid` | OpenSkyLab | **Full (F)** | String (PIDINST) | `[suspicious link removed]` | Persistent Identifier for the physical instrument (PIDINST schema). |
| `pixel_pitch` | OpenSkyLab / ASPRS | **Full (F)** | Float (µm) | `3.45` \| `3.75` \| `17.0` | Physical dimensions of individual detector elements on the sensor matrix. |

**Table 4. Camera Geometry and Optical Calibration**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `calibrated_focal_length` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Float (mm) | `5.421` \| `8.045` | Principal distance (\\(f\\)) derived from self-calibration or lab adjustment. |
| `calibrated_optical_centre` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Array (px) | `[728.4, 544.1]` | Principal point coordinates (\\(x_0, y_0\\)) in sensor pixel space. |
| `radial_distortion` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Array | `[-0.1245, 0.0892, -0.0123]` | Polynomial coefficients of radial lens distortion (\\(k_1, k_2, k_3\\)). |
| `tangential_distortion` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Array | `[0.00012, -0.00045]` | Coefficients of tangential/decentering lens distortion (\\(p_1, p_2\\)). |
| `distortion_model` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Categorical | `Brown-Conrady` \| `Fisheye` \| `Kannala-Brandt` | Mathematical formulation governing optical distortion corrections. |
| `vignetting_coefficients` | OpenSkyLab | **Full (F)** | Array | `[1.0, -0.0023, 0.000015]` | Radial fall-off polynomial coefficients for light attenuation correction. |
| `black_level` | OpenSkyLab | **Full (F)** | Float (DN) | `142.0` \| `256.0` | Dark current noise baseline in Digital Numbers (DN) at zero illumination. |
| `relative_optical_centre` | OpenSkyLab | **Full (F)** | Array | `[0.001, -0.002]` | Normalized offset of principal point relative to physical sensor center. |
| `nonorthogonality` | OpenSkyLab | **Full (F)** | Float | `0.00001` | Non-orthogonality coefficient of sensor matrix axes. |
| `flat_field_factor` | OpenSkyLab | **Optional (O)** | Matrix / File | `calib/flat_field_blue.tif` | 2D correction matrix compensating for spatial sensor response non-uniformity. |

**Table 5. Radiometric and Thermal Calibration (Multispectral & LWIR)**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `band_name` | OpenSkyLab | **Quantitative (Q)** | String | `Blue` \| `Green` \| `Red` \| `RedEdge` \| `NIR` \| `LWIR` | Standardized band designation. |
| `band_centre_wavelength` | OpenSkyLab | **Quantitative (Q)** | Float (nm) | `475` \| `560` \| `668` \| `717` \| `842` \| `11000` | Central wavelength of spectral response in nanometers. |
| `band_fwhm` | OpenSkyLab | **Quantitative (Q)** | Float (nm) | `20` \| `32` \| `10` \| `6000` | Full Width at Half Maximum (FWHM) defining spectral band pass filter. |
| `dark_current` | OpenSkyLab | **Quantitative (Q)** | Array (DN) | `` | Dark current values recorded per spectral channel. |
| `radiometric_gain_offset` | OpenSkyLab | **Quantitative (Q)** | Array | `[0.0124, 0.0]` | Linear multipliers converting raw DN values to spectral radiance. |
| `panel_reflectance` | OpenSkyLab | **Quantitative (Q)** | Array (0–1) | `[0.52, 0.53, 0.52, 0.51, 0.50]` | Lab-calibrated absolute reflectance factor of the reference panel per band. |
| `panel_id` | OpenSkyLab | **Quantitative (Q)** | String | `RP06-210342-SC` | Calibration panel serial number and certificate identifier. |
| `sensor_gain` | OpenSkyLab | **Quantitative (Q)** | Float | `1.0` \| `2.0` \| `4.0` | Hardware gain setting applied during image acquisition. |
| `dls_irradiance` | OpenSkyLab | **Quantitative (Q)** | Array (µW/cm²/nm) | `[124.5, 138.2, 142.0, 135.1, 110.4]` | Incident solar irradiance measured by the Downwelling Light Sensor (DLS). |
| `panel_images` | OpenSkyLab | **Quantitative (Q)** | Array of Files | `["raw/IMG_0001_1.tif", "raw/IMG_0001_2.tif"]` | Raw image filenames capturing reference reflectance panel before/after flight. |
| `spectral_range` | OpenSkyLab | **Quantitative (Q)** | String (µm) | `7.5-13.5` \| `8.0-14.0` | Thermal sensor spectral response window. |
| `planck_constants` | OpenSkyLab | **Quantitative (Q)** | Array | `[14983.6, 1427.5]` | Sensor-specific Planck constants (\\(K_1, K_2\\)) for radiance-to-brightness temperature conversion. |
| `emissivity_references` | OpenSkyLab | **Quantitative (Q)** | Table | `{"bare_soil": 0.95, "vegetation": 0.98, "water": 0.99}` | Surface emissivity (\\(\varepsilon\\)) lookup table assigned to land cover classes. |
| `image_encoding` | OpenSkyLab | **Quantitative (Q)** | Categorical | `16-bit radiometric TIFF` \| `radiometric JPEG` \| `FLIR R-JPEG` | Thermal raw file encoding protocol. |
| `fpa_temperature` | OpenSkyLab | **Quantitative (Q)** | Float (°C) | `32.4` \| `35.1` | Focal Plane Array (FPA) temperature recorded during exposure for thermal drift compensation. |
| `drift_protocol` | OpenSkyLab | **Quantitative (Q)** | Table | `FFC shutter event every 120 seconds` | Internal Flat-Field Correction (FFC / NUC) schedule executed to eliminate drift. |
| `ambient_conditions` | OpenSkyLab | **Quantitative (Q)** | Array | `[22.5, 45.0]` (Air Temp °C, RH %) | Atmospheric parameters used in LOWTRAN/MODTRAN thermal atmospheric attenuation models. |
| `sensor_gain_adjustment` | OpenSkyLab | **Full (F)** | Float | `1.02` | Dynamic gain adjustment factor computed from scene histograms. |
| `dls_attitude` | OpenSkyLab | **Full (F)** | Array (degrees) | `[1.2, -0.5, 184.2]` (roll, pitch, yaw) | DLS orientation vector used for sun-angle trigonometric corrections. |
| `spectral_response` | OpenSkyLab | **Full (F)** | File / Array | `calib/srf_micasense_rededge_p.json` | Continuous Spectral Response Function (SRF) curves per detector. |
| `stated_accuracy` | OpenSkyLab | **Full (F)** | String | `NETD < 50 mK, Absolute Accuracy +/- 2 deg C` | Manufacturer-stated thermal sensitivity (NETD) and absolute accuracy. |
| `warmup_time` | OpenSkyLab | **Full (F)** | Float (min) | `15.0` \| `20.0` | Sensor thermal stabilization time allowed prior to flight execution. |

**Table 6. Atmospheric and Environmental Conditions**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `weather_source` | OpenSkyLab | **Quantitative (Q)** | Text | `On-site Vaisala WXT536 Weather Station at field margin` | Station description, coordinates, and distance to the flight polygon. |
| `air_temperature` | OpenSkyLab | **Quantitative (Q)** | Float (°C) | `21.8` \| `24.2` | Mean ambient air temperature recorded during flight execution. |
| `relative_humidity` | OpenSkyLab | **Quantitative (Q)** | Float (%) | `48.5` \| `62.0` | Mean relative humidity recorded during flight execution. |
| `air_pressure` | OpenSkyLab | **Quantitative (Q)** | Float (hPa) | `1013.25` \| `998.4` | Atmospheric barometric pressure at field level. |
| `wind_speed` | OpenSkyLab | **Quantitative (Q)** | Float (m/s) | `2.4` \| `4.1` | Mean wind speed and gust velocity during acquisition. |
| `cloud_cover` | OpenSkyLab | **Quantitative (Q)** | Float (oktas / %) | `0.0` (0%) \| `2.0` (25%) \| `8.0` (100%) | Sky cloud cover percentage or oktas during acquisition. |
| `sky_condition` | OpenSkyLab | **Quantitative (Q)** | Categorical | `clear` \| `scattered` \| `broken` \| `overcast` \| `variable` | Illumination stability classification. |
| `solar_zenith` | OpenSkyLab | **Quantitative (Q)** | Float (degrees) | `32.41` | Calculated solar zenith angle governing BRDF effects. |
| `solar_azimuth` | OpenSkyLab | **Quantitative (Q)** | Float (degrees) | `154.12` | Calculated solar azimuth angle at mission time and location. |
| `sensor_target_distance` | OpenSkyLab | **Quantitative (Q)** | Float (m) | `50.2` \| `100.5` | Average optical path length through the atmosphere for radiative transfer modeling. |
| `sampling_interval` | OpenSkyLab | **Quantitative (Q)** | Float (s) | `10.0` \| `60.0` | Weather station logging interval. |
| `wind_direction` | OpenSkyLab | **Full (F)** | Float (degrees) | `225.0` (SW) | Wind direction in degrees relative to true North (\\(0^\circ–360^\circ\\)). |
| `surface_condition` | OpenSkyLab | **Full (F)** | Text | `Dry bare soil, no recent precipitation in last 72h` | Surface moisture state, precipitation history, dew presence, or snow cover. |
| `incoming_irradiance_ground` | OpenSkyLab | **Optional (O)** | Float (\\(\text{W/m}^2\\)) | `845.2` | Global downwelling solar irradiance measured by a ground pyranometer. |

**Table 7. Ground Reference and Geodetic Measurements**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `reference_id` | OpenSkyLab | **Quantitative (Q)** | String | `GCP_01` \| `CHK_05` \| `SMC_STATION_A` | Unique identifier assigned to a ground reference target or sampling point. |
| `reference_type` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Categorical | `GCP` \| `Checkpoint` \| `Reflectance_Panel` \| `In_Situ_Soil_Moisture` \| `LST_Target` | Physical functional role of the ground reference. |
| `position` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Array (EPSG) | `[551234.52, 1142567.81, 245.12]` (EPSG:5514) | Precise 3D coordinates (\\(X, Y, Z\\)) in a declared geodetic system. |
| `time_utc` | OpenSkyLab | **Quantitative (Q)** | String (ISO 8601) | `2026-06-12T09:30:00Z` | Timestamp of field sample collection or geodetic survey. |
| `instrument` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Text | `Leica GS18 T RTK-GNSS` \| `Delta-T ThetaProbe ML2x` \| `FLIR Handheld Thermometer` | Survey equipment name, calibration status, and declared instrument accuracy. |
| `quantity` | OpenSkyLab | **Quantitative (Q)** | Categorical | `volumetric_soil_moisture` \| `reflectance` \| `surface_temperature` \| `3d_position` | Measured physical quantity. |
| `value` | OpenSkyLab | **Quantitative (Q)** | Float \\(\pm\\) Error | `0.245 +/- 0.012 m3/m3` \| `24.5 +/- 0.3 deg C` | Measured ground value and associated measurement uncertainty. |
| `emissivity_setting` | OpenSkyLab | **Full (F)** | Float (0–1) | `0.98` | Emissivity setting configured on handheld thermal radiometers. |
| `footprint` | OpenSkyLab | **Full (F)** | Float (\\(\text{m}^2\\)) | `0.05` \| `1.0` | Physical area sampled by the ground instrument for spatial scaling against UAV pixels. |
| `target_size` | OpenSkyLab / ASPRS | **Full (F)** | String (m x m) | `0.6 x 0.6` \| `1.0 x 1.0` | Target dimensions in meters (must comfortably exceed nominal GSD). |
| `target_value_range` | OpenSkyLab | **Full (F)** | Interval | `[0.05, 0.45] m3/m3` | Dynamic range of ground calibration targets across the site. |
| `repeat_interval` | OpenSkyLab | **Full (F)** | Float (min) | `15.0` \| `30.0` | Interval between repeated ground validation measurements. |
| `traceability` | OpenSkyLab | **Full (F)** | Text | `Calibrated against NIST standards / Gravimetric oven drying at 105 deg C` | Metrological traceability to international SI standards or gravimetric calibration protocols. |

**Table 8. Data Processing, Software, and Lineage Provenance**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `workflow_id` | OpenSkyLab | **Quantitative (Q)** | String | `WF_SFM_REFLECTANCE_V2` | Identifier of the data processing pipeline executed. |
| `software` | OpenSkyLab / ASPRS | **Quantitative (Q)** | Array of JSON | `[{"name": "Agisoft Metashape Professional", "version": "2.1.1"}, {"name": "GDAL", "version": "3.8.2"}]` | Complete list of processing software titles and exact software build versions. |
| `steps` | OpenSkyLab | **Quantitative (Q)** | Array of JSON | `[{"step": 1, "action": "Vignetting & Dark Current Correction"}, {"step": 2, "action": "SfM Alignment"}]` | Sequential pipeline execution steps. |
| `photogrammetry_settings` | OpenSkyLab / ASPRS | **Quantitative (Q)** | JSON | `{"key_point_limit": 40000, "tie_point_limit": 4000, "dense_cloud_quality": "high"}` | Key photogrammetric settings executed during bundle block adjustment. |
| `adjustment_quality` | OpenSkyLab / ASPRS | **Quantitative (Q)** | JSON | `{"reprojection_error_px": 0.42, "gcp_rmse_m": 0.012}` | Statistical quality indicators from bundle adjustment (reprojection error, GCP residuals). |
| `radiometric_settings` | OpenSkyLab | **Quantitative (Q)** | JSON | `{"method": "Empirical Line Method", "panel_used": true, "dls_used": true}` | Specific algorithms and parameters executed during radiometric calibration. |
| `thermal_settings` | OpenSkyLab | **Quantitative (Q)** | JSON | `{"atmospheric_transmission": 0.92, "emissivity": 0.97}` | Radiance-to-LST transformation parameters. |
| `uncertainty_budget` | OpenSkyLab | **Quantitative (Q)** | Text / Table | `Total Reflectance Uncertainty: +/- 0.02 (k=2)` | Overall measurement uncertainty budget and error propagation formulation. |
| `dem_used` | OpenSkyLab / ASPRS | **Quantitative (Q)** | String | `Generated High-Resolution UAV DSM (GSD 2.5 cm)` | Elevation model used for orthorectification. |
| `output_crs` | OpenSkyLab / ASPRS | **Quantitative (Q)** | String (EPSG) | `EPSG:5514` (S-JTSK / Krovak) \| `EPSG:32633` (UTM zone 33N) | Coordinate reference system assigned to output spatial products. |
| `code_reference` | OpenSkyLab | **Full (F)** | String (URL / DOI) | `[suspicious link removed]` | DOI or repository link to processing scripts for computational reproducibility. |
| `atmospheric_model` | OpenSkyLab | **Full (F)** | Text | `MODTRAN 6 Atmospheric Radiative Transfer Model` | Atmospheric radiative transfer model executed for surface reflectance/LST retrieval. |
| `radiometric_check` | OpenSkyLab | **Full (F)** | JSON | `{"validation_target": "Tarpaulin 24%", "measured_uav": 0.242, "ground_spec": 0.239}` | Independent reflectance validation check against field spectroradiometers. |
| `sensitivity_analysis` | OpenSkyLab | **Full (F)** | Text / Table | `LST sensitivity to emissivity error +/- 0.01 is +/- 0.45 deg C` | Sensitivity analysis of output products to input parameter uncertainties. |
| `coregistration_quality` | OpenSkyLab | **Full (F)** | Float (px) | `0.25` (Inter-band alignment RMSE in pixels) | Inter-band spatial coregistration accuracy across spectral channels. |
| `view_angle_limits` | OpenSkyLab | **Full (F)** | Float (degrees) | `30.0` (Masked pixels with off-nadir angle > 30 deg) | Applied off-nadir view angle threshold to minimize BRDF distortions. |

**Table 9. Output Data Products and FAIR Metadata**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `product_id` | OpenSkyLab | **Core (C)** | String | `MARQUARDT-20260612-REFLECTANCE-MAP` | Unique product file identifier. |
| `level` | OpenSkyLab | **Core (C)** | Categorical | `L0` \| `L1` \| `L2` \| `L3` \| `L4` | Processing level (`L0` raw \| `L1` calibrated \| `L2` orthomosaic/DEM \| `L3` indices/LST \| `L4` predictive AI models). |
| `product_type` | OpenSkyLab / ASPRS | **Core (C)** | Categorical | `Orthomosaic` \| `DSM` \| `DTM` \| `Point_Cloud` \| `Reflectance_Map` \| `LST_Map` \| `Soil_Moisture_Map` | Geospatial product type. |
| `file` | OpenSkyLab | **Core (C)** | String (Path) | `products/marquardt_20260612_ms_reflectance.tif` | Relative file path within the published data package. |
| `format` | OpenSkyLab | **Core (C)** | Categorical | `Cloud Optimized GeoTIFF (COG)` \| `LAZ v1.4` \| `NetCDF4` | File format encoding. |
| `quantity_unit` | OpenSkyLab | **Core (C)** | String | `reflectance (0-1)` \| `deg C` \| `m3/m3` \| `meters` | Physical quantity and measurement units represented per pixel. |
| `crs` | OpenSkyLab / ASPRS | **Core (C)** | String (EPSG) | `EPSG:5514` \| `EPSG:32633` \| `EPSG:4326` | EPSG code defining product spatial reference system. |
| `gsd` | OpenSkyLab / ASPRS | **Core (C)** | Float (cm/px) | `1.2` \| `2.5` \| `5.0` | Actual spatial resolution (GSD) of the raster product. |
| `derived_from` | OpenSkyLab | **Core (C)** | Array of IDs | `["MARQUARDT-20260612-01"]` | Identifiers of source missions or raw files used to generate this product. |
| `checksum` | OpenSkyLab | **Core (C)** | String (SHA-256) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Cryptographic SHA-256 hash verifying file integrity. |
| `nodata` | OpenSkyLab | **Quantitative (Q)** | Float | `-9999.0` \| `65535` | Reserved numeric value designating unmapped/null pixels. |
| `extent` | OpenSkyLab | **Quantitative (Q)** | Array (CRS) | `[-551200.0, -1142600.0, -551000.0, -1142400.0]` | Bounding box in projected coordinate units. |
| `bands` | OpenSkyLab | **Quantitative (Q)** | Array of JSON | `[{"band": 1, "name": "Blue", "center_nm": 475}, {"band": 2, "name": "Green", "center_nm": 560}]` | Band order, spectral definitions, and physical meanings in multi-band GeoTIFFs. |
| `workflow_id` | OpenSkyLab | **Quantitative (Q)** | String | `WF_SFM_REFLECTANCE_V2` | Reference to the processing workflow that generated this product. |
| `quality_summary` | OpenSkyLab | **Full (F)** | Text | `Orthomosaic passes ASPRS 2024 Horizontal Accuracy Class 2.5 cm` | Summary assessment of product quality, shadow coverage, or saturation. |
| `quality_mask` | OpenSkyLab | **Quantitative (Q)** | File / Band | `products/marquardt_20260612_quality_mask.tif` | Quality mask raster layer (flagging clouds, shadows, saturation, NoData). |
| `uncertainty_layer` | OpenSkyLab | **Full (F)** | File / Band | `products/marquardt_20260612_uncertainty.tif` | Per-pixel measurement uncertainty raster layer. |
| `observed_property` | OpenSkyLab | **Full (F)** | String (IRI) | `[suspicious link removed]` | Controlled semantic URI matching W3C/SOSA/SSN or CF conventions. |
| `annotations` | OpenSkyLab | **Optional (O)** | Text / File | `annotations/soil_crust_polygons.geojson` | Vector annotations for machine learning model training. |

**Table 10. ASPRS (2024) Geodetic Accuracy and Verification**

| Parameter / Metadata Key | Standard Origin | Importance Level | Data Type / Format | Examples (Value Pattern / Controlled Vocabulary) | Detailed Parameter Description & Methodological Function |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `reported_rmse_horizontal` | ASPRS 2024 | **ASPRS Core** | Float (cm) | `1.2` \| `2.5` \| `5.0` | Root Mean Square Error in horizontal plane (\\(RMSE_X, RMSE_Y, RMSE_H\\)). Primary horizontal accuracy metric. |
| `reported_rmse_vertical` | ASPRS 2024 | **ASPRS Core** | Float (cm) | `2.1` \| `4.5` \| `8.0` | Root Mean Square Error in vertical axis (\\(RMSE_Z\\)). Primary vertical accuracy metric. |
| `checkpoint_sample_size` | ASPRS 2024 | **ASPRS Core** | Integer (\\(N\\)) | `30` \| `45` \| `60` | Number of independent Checkpoints. ASPRS 2024 strictly requires \\(N \ge 30\\) for full statistical compliance. |
| `asprs_2024_compliance_status` | ASPRS 2024 | **ASPRS Core** | Categorical | `Tested to Meet` \| `Tested with Reduced Checkpoints` \| `Produced to Meet` | Official ASPRS 2024 compliance statement classification. |
| `combined_rmse_3d` | ASPRS 2024 | **ASPRS Required** | Float (cm) | `2.4` \| `5.1` | Combined 3D positional error (\\(RMSE_{3D} = \sqrt{RMSE_X^2 + RMSE_Y^2 + RMSE_Z^2}\\)) for point clouds/3D mesh. |
| `statistical_residuals_distribution` | ASPRS 2024 | **ASPRS Required** | Matrix / JSON | `{"mean_m": 0.002, "median_m": 0.001, "std_dev_m": 0.011, "min_m": -0.021, "max_m": 0.024, "skewness": 0.12}` | Full residual error distribution statistics evaluated on independent Checkpoints. |
| `outliers_rejection_threshold` | ASPRS 2024 | **ASPRS Required** | Float (cm) | `3.6` (3x \\(RMSE_H\\) threshold) | Rejection threshold for detecting gross errors (\\(> 3 \times RMSE\\)). |
| `nva_vertical_accuracy` | ASPRS 2024 | **ASPRS Required** | Float (cm) | `3.8` (at 95% confidence level = \\(1.96 \times RMSE_Z\\)) | Non-Vegetated Vertical Accuracy (NVA) evaluated on bare ground checkpoints. |
| `vva_vertical_accuracy` | ASPRS 2024 | **ASPRS Required** | Float (cm) | `7.2` (95th percentile error in canopy) | Vegetated Vertical Accuracy (VVA) evaluated in canopy-covered terrain (reported without pass/fail criteria). |
| `low_confidence_areas_mask` | ASPRS 2024 | **ASPRS Recommended** | Vector Polygon | `vectors/low_confidence_dense_canopy.geojson` | Polygon delineation masking low-confidence elevation areas (dense canopy, deep shadows, water bodies). |
| `aerotriangulation_accuracy_ratio` | ASPRS 2024 | **ASPRS Recommended** | Ratio | `RMSE_AT = 0.45 * RMSE_MAP` (\\(\le 0.5 \times RMSE_{MAP}\\)) | Ratio of aerotriangulation accuracy to final product accuracy. |
| `seamline_mismatch_max` | ASPRS 2024 | **ASPRS Recommended** | Float (cm) | `2.2` (\\(\le 2 \times RMSE_H\\)) | Maximum allowable seamline mismatch across orthomosaic boundaries. |
| `swath_to_swath_precision` | ASPRS 2024 | **ASPRS Recommended** | Float (cm) | `1.8` | Relative precision between overlapping adjacent LiDAR swaths (\\(RMS_{DZ}\\)). |

Comprehensive matrix of UAV metadata, parameters, and geodetic accuracy (OpenSkyLab & ASPRS 2024)
:::
