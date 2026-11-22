import {
  Callout,
  Checkbox,
  CollapsibleSection,
  Divider,
  Grid,
  H1,
  Pill,
  Row,
  Stack,
  Stat,
  Text,
  useCanvasState,
} from "cursor/canvas";

type Paper = {
  id: number;
  year: number;
  authors: string;
  lead: string;
  title: string;
  doi: string;
  platform: string;
  abstract: string;
  keywords: string;
  /** Publisher correction of this extraction ID — do not count as a second study. */
  sameAs?: number;
};

const PAPERS: Paper[] = [
  {
    "id": 45,
    "year": 2020,
    "authors": "Basurto-Lozada, D.; Hillier, A.; Medina, D.; Pulido, D.; Karaman, S.; Salas, J.",
    "lead": "Basurto-Lozada, D.",
    "title": "Dynamics of soil surface temperature with unmanned aerial systems",
    "doi": "10.1016/j.patrec.2020.07.003",
    "platform": "uav, satellite",
    "abstract": "Thermographies are a source of rich information, valuable in precision agriculture tasks such as crop stress assessment, plant disease analysis, and soil moisture evaluation. Traditionally, practitioners obtain soil temperature from the ground or using satellites and other airborne methods, which are costly and offer limited spatial and temporal resolution. In this paper, we introduce a method to measure soil surface temperature dynamics with the use of an unmanned aerial system (UAS). In our approach, we fuse information from thermal and multispectral cameras with ambient variables to generate estimates for soil temperature using computational intelligence models. Using the images, we produce a spatial reconstruction using structure from motion (SfM). After the multimodal registration of the resulting geo-referenced orthomosaics, we characterize the dynamics of the soil surface temperature using the differences between consecutively captured temperature orthomosaics. In our results, we are capable of estimating soil surface temperature from a UAS flying at 30 m AGL with a RMSE of 3.24∘C ± 0.3 and 1.77∘C ± 0.2, at one standard deviation, for two test fields with average ground sampling distances below 6.0 cm/pixel, using a Random Forest regressor. © 2020",
    "keywords": "Remote sensing; Soil surface temperature; Thermographic imaging; Unmanned aerial systems; Agricultural robots; Antennas; Atmospheric temperature; Decision trees; Dynamics; Soil moisture; Unmanned aerial vehicles (UAV); Ground sampling distances; Multi-spectral cameras; Multimodal registration; Soil surface temperatures; Spatial and temporal resolutions; Spatial reconstruction; Structure from motion; Unmanned aerial systems; Surface properties"
  },
  {
    "id": 40,
    "year": 2020,
    "authors": "Bhatti, S.; Heeren, D.M.; Barker, J.B.; Neale, C.M.U.; Woldt, W.E.; Maguire, M.S.; Rudnick, D.R.",
    "lead": "Bhatti, S.",
    "title": "Site-specific irrigation management in a sub-humid climate using a spatial evapotranspiration model with satellite and airborne imagery",
    "doi": "10.1016/j.agwat.2019.105950",
    "platform": "uav, satellite",
    "abstract": "Variable Rate Irrigation (VRI) considers spatial variability in soil and plant characteristics to optimize irrigation management in agricultural fields. The advent of unmanned aircraft systems (UAS) creates an opportunity to utilize high-resolution (spatial and temporal) imagery into irrigation management due to decreasing costs, ease of operation, and reduction of regulatory constraints. This research aimed to evaluate the use of UAS data for VRI, and to quantify the potential of VRI in terms of relative crop and water response. Irrigation treatments were: (1) VRI using Landsat imagery (VRI-L), (2) VRI using UAS imagery (VRI-U), (3) uniform (U), and (4) rainfed (R). An updated remote-sensing-based evapotranspiration and water balance model, incorporating soil water measurements, was used to make prescriptions for the VRI treatments at a field site in eastern Nebraska. In 2017, the mean prescribed seasonal irrigation depth (Ip) for VRI-L was significantly greater (α = 0.05) than the Ip for U for soybean. In 2018, Ip for soybean was greatest for VRI-U treatment followed by the U and VRI-L treatments, with all being significantly different from each other. No significant differences in Ip for maize were observed in 2017 or 2018. In all crop-year combinations, the VRI and U treatments had significantly greater evapotranspiration (ET) than the R treatment. Yield differences among treatments were not significant (except for rainfed maize compared to VRI-L in 2017). For maize in 2017, IWUE for VRI-L was comparable to the U treatment. The UAS imagery was a better match for the scale of crop management than Landsat imagery, particularly for thermal data. The multispectral UAS data was successfully used in the crop coefficient ET model for real-time irrigation, but using UAS to determine accurate canopy temperatures for surface energy balance modeling remains a challenge. © 2019 Elsevier B.V.",
    "keywords": "Evapotranspiration; Remote sensing; Soil water content; Spatial variability; Unmanned aircraft systems; Variable rate irrigation; Nebraska; United States; Glycine max; Zea mays; Climate models; Crops; Evapotranspiration; Irrigation; Remote sensing; Satellite imagery; Soil moisture; Soil surveys; Water distribution systems; Evapotranspiration modeling; Site specific irrigation; Soil water content; Soil water measurements; Spatial variability; Surface energy balance modeling; Unmanned aircraft system; Variable rate irrigations; airborne sensing; airborne survey; energy balance; evapotranspiration; irrigation system; Landsat; maize; model; rainfed agriculture; remote sensing; satellite imagery; soil water; soil-vegetation interaction; soybean; spatial variation; spectral analysis; water budget; water content; Unmanned aerial vehicles (UAV)"
  },
  {
    "id": 44,
    "year": 2020,
    "authors": "Montzka, C.; Brogi, C.; Mengen, D.; Matveeva, M.; Baum, S.; Schuttemeyer, D.; Bayat, B.; Bogena, H.; Coccia, A.; Masalias, G.; Graf, V.; Jakobi, J.; Jonard, F.; Ma, Y.; Mattia, F.; Palmisano, D.; Rascher, U.; Satalino, G.; Jagdhuber, T.; Fluhrer, A.; Schumacher, M.; Schmidt, M.; Vereecken, H.",
    "lead": "Montzka, C.",
    "title": "Sarsense: A C- and L-Band SAR Rehearsal Campaign in Germany in Preparation for ROSE-L",
    "doi": "10.1109/IGARSS39084.2020.9324090",
    "platform": "uav, satellite",
    "abstract": "In summer 2019 the SARSense campaign was held in Jülich, Germany, to provide insights into the potentials and specifications of the ESA Copernicus candidate mission ROSE-L (Radar Observation System for Europe). ROSE-L will consist of two satellites that carry a polarimetric L-band SAR. Since the L-band signal can penetrate through many natural materials such as vegetation, dry snow and ice, the mission will provide additional information that cannot be gathered by the Copernicus Sentinel-1 C-band SAR mission. The overall objective of the SARSense 2019 campaign is to analyze the mission design concerning its potential for agricultural monitoring services including target applications such as soil moisture monitoring, irrigation management, crop type discrimination, food security and precision farming. The SARSense in situ measurements of soil moisture, soil temperature, vegetation properties, UAS-based multispectral and thermal mapping, as well as the airborne SAR observations are presented as well as strategies for soil moisture retrieval and first analysis. © 2020 IEEE.",
    "keywords": "Airborne Campaign; L-Band; ROSE-L; SAR; Agricultural robots; Agriculture; Food supply; Geology; Ice; Moisture control; Remote sensing; Soil moisture; Vegetation; Agricultural monitoring; In-situ measurement; Irrigation management; Natural materials; Radar observations; Soil moisture retrievals; Target application; Vegetation properties; Synthetic aperture radar"
  },
  {
    "id": 39,
    "year": 2021,
    "authors": "Chakhar, A.; Hernández-López, D.; Ballesteros, R.; Moreno, M.A.",
    "lead": "Chakhar, A.",
    "title": "Improvement of the soil moisture retrieval procedure based on the integration of uav photogrammetry and satellite remote sensing information",
    "doi": "10.3390/rs13244968",
    "platform": "uav, satellite",
    "abstract": "In countries characterized by arid and semi-arid climates, a precise determination of soil moisture conditions on the field scale is critically important, especially in the first crop growth stages, to schedule irrigation and to avoid wasting water. The objective of this study was to apply the operative methodology that allowed surface soil moisture (SSM) content in a semi-arid environment to be estimated. SSM retrieval was carried out by combining two scattering models (IEM and WCM), supplied by backscattering coefficients at the VV polarization obtained from the C-band Synthetic Aperture Radar (SAR), a vegetation descriptor NDVI obtained from the optical sensor, among other essential parameters. The inversion of these models was performed by Neural Networks (NN). The combined models were calibrated by the Sentinel 1 and Sentinel 2 data collected on bare soil, and in cereal, pea and onion crop fields. To retrieve SSM, these scattering models need accurate measurements of the roughness surface parameters, standard deviation of the surface height (hrms) and correlation length (L). This work used a photogrammetric acquisition system carried on Unmanned Aerial Vehicles (UAV) to reconstruct digital surface models (DSM), which allowed these soil roughness parameters to be acquired in a large portion of the studied fields. The obtained results showed that the applied improved methodology effectively estimated SSM on bare and cultivated soils in the principal early growth stages. The bare soil experimentation yielded an R2 = 0.74 between the estimated and observed SSMs. For the cereal field, the relation between the estimated and measured SSMs yielded R2 = 0.71. In the experimental pea fields, the relation between the estimated and measured SSMs revealed R2 = 0.72 and 0.78, respectively, for peas 1 and peas 2. For the onion experimentation, the highest R2 equaled 0.5 in the principal growth stage (leaf development), but the crop R2 drastically decreased to 0.08 in the completed growth phase. The acquired results showed that the applied improved methodology proves to be an effective tool for estimating the SSM on bare and cultivated soils in the principal early growth stages. © 2021 by the authors. Licensee MDPI, Basel, Switzerland.",
    "keywords": "IEM; Photogrammetric acquisition; Roughness parameters; Sentinel 1; Sentinel 2; Soil moisture; UAV; WCM; Antennas; Backscattering; Crops; Photogrammetry; Remote sensing; Soil surveys; Surface roughness; Synthetic aperture radar; Unmanned aerial vehicles (UAV); Bare soils; Growth stages; IEM; Photogrammetric acquisition; Roughness parameters; Scattering model; Sentinel 2; Sentinel-1; Surface soil moisture; WCM; Soil moisture"
  },
  {
    "id": 48,
    "year": 2021,
    "authors": "Chandel, AK; Khot, LR; Molaei, B; Peters, RT; Stöckle, CO; Jacoby, PW",
    "lead": "Chandel, AK",
    "title": "High-Resolution Spatiotemporal Water Use Mapping of Surface and Direct-Root-Zone Drip-Irrigated Grapevines Using UAS-Based Thermal and Multispectral Remote Sensing",
    "doi": "10.3390/rs13050954",
    "platform": "uav, satellite",
    "abstract": "Site-specific irrigation management for perennial crops such as grape requires water use assessments at high spatiotemporal resolution. In this study, small unmanned-aerial-system (UAS)-based imaging was used with a modified mapping evapotranspiration at high resolution with internalized calibration (METRIC) energy balance model to map water use (UASM-ET approach) of a commercial, surface, and direct-root-zone (DRZ) drip-irrigated vineyard. Four irrigation treatments, 100%, 80%, 60%, and 40%, of commercial rate (CR) were also applied, with the CR estimated using soil moisture data and a non-stressed average crop coefficient of 0.5. Fourteen campaigns were conducted in the 2018 and 2019 seasons to collect multispectral (ground sampling distance (GSD): 7 cm/pixel) and thermal imaging (GSD: 13 cm/pixel) data. Six of those campaigns were near Landsat 7/8 satellite overpass of the field site. Weather inputs were obtained from a nearby WSU-AgWeatherNet station (1 km). First, UASM-ET estimates were compared to those derived from soil water balance (SWB) and conventional Landsat-METRIC (LM) approaches. Overall, UASM-ET (2.70 +/- 1.03 mm day(-1) [mean +/- std. dev.]) was higher than SWB-ET (1.80 +/- 0.98 mm day(-1)). However, both estimates had a significant linear correlation (r = 0.64-0.81, p < 0.01). For the days of satellite overpass, UASM-ET was statistically similar to LM-ET, with mean absolute normalized ET departures (ETd,MAN) of 4.30% and a mean r of 0.83 (p < 0.01). The study also extracted spatial canopy transpiration (UASM-T) maps by segmenting the soil background from the UASM-ET, which had strong correlation with the estimates derived by the standard basal crop coefficient approach (T-d,T-MAN = 14%, r = 0.95, p < 0.01). The UASM-T maps were then used to quantify water use differences in the DRZ-irrigated grapevines. Canopy transpiration (T) was statistically significant among the irrigation treatments and was highest for grapevines irrigated at 100% or 80% of the CR, followed by 60% and 40% of the CR (p < 0.01). Reference T fraction (TrF) curves established from the UASM-T maps showed a notable effect of irrigation treatment rates. The total water use of grapevines estimated using interpolated TrF curves was highest for treatments of 100% (425 and 320 mm for the 2018 and 2019 seasons, respectively), followed by 80% (420 and 317 mm), 60% (391 and 318 mm), and 40% (370 and 304 mm) of the CR. Such estimates were within 5% to 11% of the SWB-based water use calculations. The UASM-T-estimated water use was not the same as the actual amount of water applied in the two seasons, probably because DRZ-irrigated vines might have developed deeper or lateral roots to fulfill water requirements outside the irrigated soil volume. Overall, results highlight the usefulness of high-resolution imagery toward site-specific water use management of grapevines.",
    "keywords": "grapevines; direct root zone irrigation; evapotranspiration; high-resolution aerial imagery; METRIC energy balance model; site-specific irrigation management; REGULATED DEFICIT IRRIGATION; ENERGY-BALANCE; CROP COEFFICIENTS; SOIL-MOISTURE; EVAPOTRANSPIRATION; VINEYARD; COMPONENTS; MODEL; PARAMETERIZATION; AGRICULTURE"
  },
  {
    "id": 38,
    "year": 2022,
    "authors": "Döpper, V.; Rocha, A.D.; Berger, K.; Gränzig, T.; Verrelst, J.; Kleinschmit, B.; Förster, M.",
    "lead": "Döpper, V.",
    "title": "Estimating soil moisture content under grassland with hyperspectral data using radiative transfer modelling and machine learning",
    "doi": "10.1016/j.jag.2022.102817",
    "platform": "uav, satellite",
    "abstract": "The monitoring of soil moisture content (SMC) at very high spatial resolution (<10 m) using unmanned aerial systems (UAS) is of high interest for precision agriculture and the validation of large scale SMC products. Data-driven approaches are the most common method to retrieve SMC with UAS-borne data at water limited sites over non-disturbed agricultural crops. A major disadvantage of data-driven algorithms is the limited transferability in space and time and the need of a high number of ground reference samples. Physically-based approaches are less dependent on the amount of samples and are transferable in space and time. This study explores the potential of (1) a hybrid method targeting the soil brightness factor of the PROSAIL model using a variational heteroscedastic Gaussian Processes regression (VHGPR) algorithm, and (2) a data-driven method employing VHGPR for the retrieval of SMC over three grassland sites based on UAS-borne VIS–NIR (399–1001 nm) hyperspectral data. The sites were managed by mowing (Fendt), grazing (Grosses Bruch) and irrigation (Marquardt). With these distinct local pre-conditions we aimed to identify factors that favor and limit the retrieval of SMC. The hybrid approach presented encouraging results in Marquardt (RMSE = 1.5 Vol_%, R2 = 0.2). At the permanent grassland sites (Fendt, Grosses Bruch) the thatch layer jeopardized the application of the hybrid model. We identified the complex canopy structure of grassland as the main factor impacting the hybrid SMC retrieval. The data-driven approach showed high accuracy for Fendt (R2 = 0.84, RMSE = 8.66) and Marquardt (R2 = 0.4, RMSE = 10.52). All data-driven models build on the LAI-SMC relationship. However, this relationship was hampered by mowing (Fendt), leading to a lack of transferability in time. The alteration of plant traits by grazing prevents finding a relationship with SMC in Grosses Bruch. In Marquardt, we identified the timelag between changes in SMC and plant response as the main reason of decrease in model accuracy. Yet, the model performance is accurate in undisturbed and water-limited areas (Marquardt). The analysis points to challenges that need to be tackled in future research and opens the discussion for the development of robust models to retrieve high resolution SMC from UAS-borne remote sensing observations. © 2022 The Author(s)",
    "keywords": "Anthropogenic Influence; Gaussian Processes; Grazing; Irrigation; LAI; Leaf Area Index; Mowing; PROSAIL; Time Lag; Unmanned Aerial Systems; airborne sensing; anthropogenic effect; Gaussian method; grassland; grazing; irrigation; leaf area index; machine learning; modeling; moisture content; mowing; radiative transfer; satellite data; soil moisture"
  },
  {
    "id": 46,
    "year": 2022,
    "authors": "Niu, H.; Zhao, T.; Wang, D.; Chen, Y.Q.",
    "lead": "Niu, H.",
    "title": "Estimating Evapotranspiration of Pomegranate Trees Using Stochastic Configuration Networks (SCN) and UAV Multispectral Imagery",
    "doi": "10.1007/s10846-022-01588-2",
    "platform": "uav, satellite",
    "abstract": "Evapotranspiration (ET) estimation is important in precision agriculture water management, such as evaluating soil moisture, drought monitoring, and assessing crop water stress. As a traditional method, evapotranspiration estimation using crop coefficient (Kc) has been commonly used. Since there are strong similarities between the Kc curve and the vegetation index curve, the crop coefficient Kc is usually estimated as a function of the vegetation index. Researchers have developed linear regression models for the Kc and the normalized difference vegetation index (NDVI), usually derived from satellite imagery. However, the spatial resolution of the satellite image is often insufficient for crops with clumped canopy structures, such as vines and trees. Therefore, in this article, the authors used Unmanned Aerial Vehicles (UAVs) to collect high-resolution multispectral imagery in a pomegranate orchard located at the USDA-ARS, San Joaquin Valley Agricultural Sciences Center, Parlier, CA. The Kc values were measured from a weighing lysimeter and the NDVI values were derived from UAV imagery. Then, the authors established a relationship between the NDVI and Kc by using a linear regression model and a stochastic configuration networks (SCN) model, respectively. Based on the research results, the linear regression model has an R2 of 0.975 and RMSE of 0.05. The SCN regression model has an R2 and RMSE value of 0.995 and 0.046, respectively. Compared with the linear regression model, the SCN model improved performance in predicting Kc from NDVI. Then, actual evapotranspiration was estimated and compared with lysimeter data in an experimental pomegranate orchard. The UAV imagery provided a spatial and tree-by-tree view of ET distribution. © 2022, The Author(s).",
    "keywords": "Evapotranspiration; NDVI; SCNs; Unmanned aerial vehicles; Antennas; Crops; Evapotranspiration; Forestry; Irrigation; Remote sensing; Satellite imagery; Soil moisture; Soil surveys; Stochastic models; Unmanned aerial vehicles (UAV); Vegetation; Water management; Crop coefficient; Linear regression modelling; Multispectral imagery; Network models; Normalized difference vegetation index; Precision Agriculture; SCN; Stochastics; Vegetation index; Waters managements; Stochastic systems"
  },
  {
    "id": 47,
    "year": 2022,
    "authors": "Yu, J.; Wang, J.; Leblon, B.; Song, Y.",
    "lead": "Yu, J.",
    "title": "Nitrogen Estimation for Wheat Using UAV-Based and Satellite Multispectral Imagery, Topographic Metrics, Leaf Area Index, Plant Height, Soil Moisture, and Machine Learning Methods",
    "doi": "10.3390/nitrogen3010001",
    "platform": "uav, satellite",
    "abstract": "To improve productivity, reduce production costs, and minimize the environmental impacts of agriculture, the advancement of nitrogen (N) fertilizer management methods is needed. The objective of this study is to compare the use of Unmanned Aerial Vehicle (UAV) multispectral imagery and PlanetScope satellite imagery, together with plant height, leaf area index (LAI), soil moisture, and field topographic metrics to predict the canopy nitrogen weight (g/m2) of wheat fields in southwestern Ontario, Canada. Random Forests (RF) and support vector regression (SVR) models, applied to either UAV imagery or satellite imagery, were evaluated for canopy nitrogen weight prediction. The top-performing UAV imagery-based validation model used SVR with seven selected variables (plant height, LAI, four VIs, and the NIR band) with an R2 of 0.80 and an RMSE of 2.62 g/m2. The best satellite imagery-based validation model was RF, which used 17 variables including plant height, LAI, the four PlanetScope bands, and 11 VIs, resulting in an R2 of 0.92 and an RMSE of 1.75 g/m2. The model information can be used to improve field nitrogen predictions for the effective management of N fertilizer. © 2021 by the authors.",
    "keywords": "machine learning; nitrogen management; PlanetScope imagery; precision agriculture; Random Forests; Support Vector Regression (SVR); Unmanned Aerial Vehicle (UAV); wheat"
  },
  {
    "id": 41,
    "year": 2023,
    "authors": "Heistermann, M.; Francke, T.; Scheiffele, L.; Dimitrova Petrova, K.; Budach, C.; Schrön, M.; Trost, B.; Rasche, D.; Güntner, A.; Döpper, V.; Förster, M.; Köhli, M.; Angermann, L.; Antonoglou, N.; Zude-Sasse, M.; Oswald, S.E.",
    "lead": "Heistermann, M.",
    "title": "Three years of soil moisture observations by a dense cosmic-ray neutron sensing cluster at an agricultural research site in north-east Germany",
    "doi": "10.5194/essd-15-3243-2023",
    "platform": "uav, satellite",
    "abstract": "Cosmic-ray neutron sensing (CRNS) allows for the estimation of root-zone soil water content (SWC) at the scale of several hectares. In this paper, we present the data recorded by a dense CRNS network operated from 2019 to 2022 at an agricultural research site in Marquardt, Germany - the first multi-year CRNS cluster. Consisting, at its core, of eight permanently installed CRNS sensors, the cluster was supplemented by a wealth of complementary measurements: data from seven additional temporary CRNS sensors, partly co-located with the permanent ones; 27 SWC profiles (mostly permanent); two groundwater observation wells; meteorological records; and Global Navigation Satellite System reflectometry (GNSS-R). Complementary to these continuous measurements, numerous campaign-based activities provided data by mobile CRNS roving, hyperspectral imagery via UASs, intensive manual sampling of soil properties (SWC, bulk density, organic matter, texture, soil hydraulic properties), and observations of biomass and snow (cover, depth, and density). The unique temporal coverage of 3 years entails a broad spectrum of hydro-meteorological conditions, including exceptional drought periods and extreme rainfall but also episodes of snow coverage, as well as a dedicated irrigation experiment. Apart from serving to advance CRNS-related retrieval methods, this data set is expected to be useful for various disciplines, for example, soil and groundwater hydrology, agriculture, or remote sensing. Hence, we show exemplary features of the data set in order to highlight the potential for such subsequent studies. The data are available at doi.org/10.23728/b2share.551095325d74431881185fba1eb09c95 . © 2023 Copernicus GmbH. All rights reserved.",
    "keywords": ""
  },
  {
    "id": 42,
    "year": 2023,
    "authors": "Zajc, M.; Koroša, A.; Urbanc, J.; Rupar, L.; Koçyigit, B.; Krivic, A.; Pecan, U.; Glavan, M.",
    "lead": "Zajc, M.",
    "title": "GPR and UAV remote sensing for detecting changes in soil moisture across a heterogeneous agricultural field",
    "doi": "10.3997/2214-4609.202320145",
    "platform": "uav, satellite",
    "abstract": "We compared past satellite images with new UAV thermal mapping results and GPR measurements, carried out on a heterogeneous agricultural field with areas of poor crop growth. Combining all three methods and comparing their results made it possible to determine, which methodology is most efficient for analysing soil properties in such settings. Results from applied methodologies correlate well with each other as well as with actual field conditions in areas of poor vegetation growth. Infrared and multispectral UAV mapping provide results with the highest contrast, making the differences in the field conditions most visible. Visual mapping of the bare soil gave the least information on the soil conditions, while GPR measurements confirmed the presence of higher amounts of water and/or clay due to GPR signal attenuation. In future research, additional analyses of soil samples, pedological profiles, data from lysimeters and dielectric probes as well as periodical UAV mapping for crop growth monitoring will be carried out. The obtained results will help determine the advantages and disadvantages of different remote sensing techniques and improve the field methodology needed for implementing precision agriculture in areas with changing soil conditions. © NSG 2023.All rights reserved.",
    "keywords": "Crops; Geological surveys; Geophysical prospecting; Mapping; Remote sensing; Soil moisture; Soil surveys; Unmanned aerial vehicles (UAV); Agricultural fields; Crop growth; Field conditions; Multi-spectral; Satellite images; Soil conditions; Soil property; Thermal mapping; UAV remote sensing; Vegetation growth; Ground penetrating radar systems"
  },
  {
    "id": 26,
    "year": 2024,
    "authors": "Chen, Z.; Chen, H.; Dai, Q.; Wang, Y.; Hu, X.",
    "lead": "Chen, Z.",
    "title": "Estimation of Soil Moisture during Different Growth Stages of Summer Maize under Various Water Conditions Using UAV Multispectral Data and Machine Learning",
    "doi": "10.3390/agronomy14092008",
    "platform": "uav, satellite",
    "abstract": "Accurate estimation of soil moisture content (SMC) is vital for effective farmland water management and informed irrigation decision-making. The utilization of unmanned aerial vehicle (UAV)-based remote sensing technology to monitor SMC offers advantages such as mobility, high timeliness, and high spatial resolution, thereby compensating for the limitations of in-situ observations and satellite remote sensing. However, previous research has primarily focused on SMC diagnostics for the entire crop growth period, often neglecting the development of targeted soil moisture modeling paradigms that account for the specific characteristics of the canopy and root zone at different growth stages. Furthermore, the variations in soil moisture status between fields, resulting from the hysteresis of water flow in irrigation channels at different levels, may influence the development of soil moisture modeling schemes, an area that has been seldom explored. In this study, SMC models based on UAV spectral information were constructed using Random Forest (RF) and Particle Swarm Optimization-Support Vector Machine (PSO-SVM) algorithms. The soil moisture modeling paradigms (i.e., input–output mapping) under different growth stages and soil moisture conditions of summer maize were systematically compared and discussed, along with the corresponding physical interpretability. Our results showed that (1) the SMC modeling schemes differ significantly across the various growth stages, with distinct input–output mappings recommended for the early (i.e., jointing, tasselling, and silking stages), middle (i.e., blister and milk stages), and late (i.e., maturing stage) periods. (2) these machine learning-based models performed best at the jointing stage, while subsequently, their accuracy generally exhibited a downward trend as the maize grew. (3) the RF model demonstrates superior robustness in estimating soil moisture status across different fields (moisture conditions), achieving optimal estimation accuracy in fields with overall higher SMC in line with the PSO-SVM model. (4) unlike the RF model’s robustness in spatial SMC diagnostics, the PSO-SVM model more reliably captured the temporal dynamics of SMC across different growth stages of summer maize. This study offers technical references for future modelers in UAV-based SMC modeling across various spatial and temporal conditions, addressing both the types of models as well as their input features. © 2024 by the authors.",
    "keywords": "machine learning; multispectral; soil moisture content; summer maize; UAV"
  },
  {
    "id": 30,
    "year": 2024,
    "authors": "Du, R.; Xiang, Y.; Zhang, F.; Chen, J.; Shi, H.; Liu, H.; Yang, X.; Yang, N.; Yang, X.; Wang, T.; Wu, Y.",
    "lead": "Du, R.",
    "title": "Combing transfer learning with the OPtical TRApezoid Model (OPTRAM) to diagnosis small-scale field soil moisture from hyperspectral data",
    "doi": "10.1016/j.agwat.2024.108856",
    "platform": "uav, satellite",
    "abstract": "Accurate, timely, and continuous soil moisture information is helpful for crop stress diagnosis and irrigation management decision. OPtical TRApezoid Model (OPTRAM) based on optical satellite data has been proven to be an effective method for assessing soil moisture status. However, the applicability of OPTRAM to small-scale field soil moisture assessment remains to be explored. In this study, we propose a strategy for the genetically parameterized OPTRAM and evaluate its applicability on Unmanned Aerial Vehicle (UAV) high-resolution hyspectral data. The results showed that: (1) When OPTRAM was used to genetically parameterized with PROSAIL generated dataset, 46 characteristic narrowband bands (|R|= 0.52–0.78) were determined in the spectral region of near infrared (NIR) (750–850 nm) and SWIR (1060–1080 and 1450–1500 nm); (2) By fine-tuned soil moisture estimation model using transfer learning strategy, the reliable soil moisture estimation was achieved in three crops (R2=0.57–0.64; RMSE=0.008–0.022 m3m−3);(3) Compared to soil moisture estimation model using a single spectral region (NIR or SWIR), the DSWC model that combine NIR and SWIR was more effective for tracking soil moisture; (4) The scale effect was observed when the fine-tuned soil moisture estimation model was applied on the high-resolution UAV images. The model performance was stable in pixel size of 1–7 cm and began to drop at pixel size of 11 cm. The above results advance the application of OPTRAM on small farmland soil moisture assessment and demonstrate the application potential of OPTRAM on narrow-band hyperspectral data. This study provides a new candidate for the use of hyperspectral data to estimate soil moisture, and scientific support for precision agriculture and irrigation scheduling. © 2024 The Authors",
    "keywords": "Canola; Irrigation management; Remote sensing; Soybean; UAV; Wheat; Antennas; Crops; Infrared devices; Infrared radiation; Irrigation; Learning systems; Optical remote sensing; Pixels; Soil surveys; Unmanned aerial vehicles (UAV); Aerial vehicle; Canola; Hyperspectral Data; Irrigation management; Optical-; Remote-sensing; Soil moisture estimation; Soybean; Unmanned aerial vehicle; Wheat; agricultural land; canola; irrigation system; pixel; precision agriculture; remote sensing; satellite data; scale effect; soil moisture; soybean; unmanned vehicle; wheat; Soil moisture"
  },
  {
    "id": 36,
    "year": 2024,
    "authors": "Surendran, U.; Nagakumar, K.C.V.; Samuel, M.P.",
    "lead": "Surendran, U.",
    "title": "Remote Sensing in Precision Agriculture",
    "doi": "10.1007/978-3-031-43548-5_7",
    "platform": "uav, satellite",
    "abstract": "Agriculture plays a vital role in feeding the world’s growing population despite facing challenges such as dwindling arable land, water scarcity, changing climatic conditions, and the need for sustainable resource management. To address these challenges and to optimize agricultural productivity, the integration of remote sensing technologies has emerged as a transformative approach within the realm of precision agriculture. Remote sensing, encompassing satellite imagery, drones, and ground-based sensors, provides invaluable data and insights for informed decision-making, resource allocation, and yield optimization. This chapter explores the significance of remote sensing applications in modern agriculture. Satellite imagery, acquired at various spatial and temporal scales, allows farmers, agronomists, and researchers to monitor crop health, identify areas of stress, and assess the impact of environmental factors. Drones equipped with high-resolution cameras and multispectral sensors enable localized data collection, facilitating detailed field-level analysis. Ground-based sensors complement these technologies by providing real-time data on soil moisture, nutrient levels, and weather conditions. The integration of remote sensing data with geographic information systems (GIS) and data analyt-ics tools empowers stakeholders to make precise interventions, leading to reduced resource wastage and increased efficiency. Through the identification of variability within fields, growers can implement site-specific management strategies, tailoring irrigation, fertilization, and pest control practices to the unique needs of each area. This targeted approach not only maximizes crop yield but also minimizes the environmental impact of agricultural operations. Furthermore, remote sensing fosters early detection of disease outbreaks, pest infestations, and nutrient defi-ciencies. Timely interventions based on accurate and up-to-date information result in improved crop health and reduced reliance on chemical inputs. Additionally, remote sensing assists in monitoring land-use changes, assessing soil erosion, and promoting sustainable land management practices. To conclude, remote sensing applications are revolutionizing agriculture by enabling precise and data-driven decision-making. By harnessing the power of satellite imagery, drones, and ground-based sensors, the agricultural sector can achieve enhanced productivity, resource efficiency, and environmental sustainability. © The Editor(s) (if applicable) and The Author(s), under exclusive license to Springer Nature Switzerland AG 2024.",
    "keywords": "Agricultural productivity; Drones; GIS; Precision agriculture; Remote sensing; Resource efficiency; Satellite imagery; Sensors; Sustainability; Explosives detection; Fertilizers; Fumigation; Landsat; Weed control; Agricultural productivity; Arable land; Decisions makings; Geographic information; Ground based sensors; Precision Agriculture; Remote sensing applications; Remote-sensing; Resource efficiencies; Water scarcity; Insect control"
  },
  {
    "id": 35,
    "year": 2024,
    "authors": "Ye, N.; Walker, J.P.; Gao, Y.; Popstefanija, I.; Hills, J.",
    "lead": "Ye, N.",
    "title": "Comparison between Thermal-Optical and L-Band Passive Microwave Soil Moisture Remote Sensing at Farm Scales: Towards UAV-Based Near-Surface Soil Moisture Mapping",
    "doi": "10.1109/JSTARS.2023.3329015",
    "platform": "uav, satellite",
    "abstract": "The unmanned aerial vehicle (UAV) based remote sensing has drawn increased attention in precision agriculture. Lightweight optical and thermal sensors have been used widely on UAVs for a range of applications, and have been proposed by some as the best approach to map soil moisture at farm scales. However, passive microwave remote sensing has been widely acknowledged as the most accurate soil moisture mapping technology, and adopted by the soil moisture and ocean salinity and soil moisture active and passive satellite missions. Accordingly, it is postulated that this will also be the best technique for UAV-based near-surface soil moisture remote sensing, overcoming the spatial resolution limitation from low earth orbit altitude. Being so far limited by sensor availability, only a small number of studies have illustrated the potential of UAV-based near-surface soil moisture mapping using L-band microwave radiometers, and there has been no direct comparison with the thermal-optical alternative. To guide the design of future UAV-based soil moisture mapping systems, airborne optical, thermal infrared, and passive microwave observations collected from a scientific aircraft at low altitude over a center-pivot irrigation farm in Tasmania, Australia were used in this study to simulate UAV-based observations, and the performances of the thermal-optical and microwave techniques when compared at 75 m scale. The L-band microwave emission showed a superior sensitivity to near-surface soil moisture, and a higher and more consistent soil moisture retrieval accuracy than thermal-optical, with a root-mean-squared error of 0.05-0.06 m3/m3 and 0.05-0.09 m3/m3, respectively. © 2008-2012 IEEE.",
    "keywords": "Airborne field experiments; microwave; optical; remote sensing; soil moisture; thermal; unmanned aerial vehicle (UAV); Antennas; Mapping; Mean square error; Microwave devices; Microwave sensors; Optical remote sensing; Orbits; Soil surveys; Unmanned aerial vehicles (UAV); Aerial vehicle; Airborne field experiment; Field experiment; Near surfaces; Optical-; Remote-sensing; Surface soil moisture; Thermal; Thermal-optical; Unmanned aerial vehicle; comparative study; image resolution; remote sensing; satellite data; satellite imagery; soil moisture; unmanned vehicle; Soil moisture"
  },
  {
    "id": 29,
    "year": 2025,
    "authors": "Farhad, M.M.; Senyurek, V.; Rafi, M.A.S.; Baray, S.B.; McCraine, C.; Hathcock, L.A.; Adeli, A.; Yanbo, H.; Gurbuz, A.C.; Kurum, M.",
    "lead": "Farhad, M.M.",
    "title": "Integrating UAS-Based GNSS-R, LiDAR, and Multispectral Data for Soil Moisture Estimation: Summary of Results from a Three-Year-Long Field Campaign",
    "doi": "10.1109/JSTARS.2025.3580114",
    "platform": "uav, satellite",
    "abstract": "Accurate and high-resolution soil moisture (SM) measurement is a critical component for site-specific precision agriculture (PA) management. Efficiently observing SM at high resolution on a subfield scale can enhance irrigation planning and management, leading to improved yields and product quality while also conserving environmental resources. However, obtaining such detailed SM measurements across large fields remains a significant challenge. Uncrewed aircraft systems (UASs) offer a promising solution in this regard. While microwave remote sensing via satellites has gained popularity for retrieving spatially distributed SM on regional and global scales, it falls short in delivering the high-resolution measurements needed for subfield applications. In response, this study has developed a UAS-based passive global navigation satellite system reflectometry (GNSS-R) technique to retrieve a high-resolution SM map at the subfield scale, designed for PA. This approach employs custom-made UASs equipped with a low-cost GNSS receiver and ancillary sensor systems. The experiment spans three years of data collection over 2.31 hectares of corn and cotton fields, incorporating GNSS-R, multispectral imaging, light detection and ranging, and in situ SM measurements. This article examines the impact of receiver antenna characteristics, surface factors, and GNSS constellations on GNSS-R measurements. It also identifies relevant features and normalization techniques that contribute to reliable SM estimation. The results highlight both the potential and the challenges of using UAS-based GNSS-R for accurate and reliable SM measurement in PA. © IEEE. 2025 IEEE.",
    "keywords": "Global navigation satellite system reflectometry (GNSS-R); L-band; light detection and ranging (LiDAR); multispectral; precision agriculture (PA); reflectometry; soil moisture; uncrewed aircraft system (UAS); Air navigation; Aircraft detection; Antennas; Communication satellites; Conservation; Environmental management; Fighter aircraft; Global positioning system; Irrigation; Precision agriculture; Reflection; Remote sensing; Soil surveys; Unmanned aerial vehicles (UAV); %moisture; Aircraft systems; Global navigation satellite system reflectometry; Global Navigation Satellite Systems; L-band; Light detection and ranging; Multi-spectral; Precision Agriculture; Reflectometry; Uncrewed aircraft system; accuracy assessment; agricultural management; GNSS; image resolution; lidar; multispectral image; precision agriculture; reflectometry; soil moisture; Soil moisture"
  },
  {
    "id": 27,
    "year": 2025,
    "authors": "Gil, H.A.P.; Marcillo, C.M.D.; Alcívar, R.A.D.; Zambrano, L.F.F.; Suc, N.E.C.; Castro, E.J.J.",
    "lead": "Gil, H.A.P.",
    "title": "Remote sensing applied for the estimation of crop coefficient and detection of forest cover changes",
    "doi": "10.47280/RevFacAgron(LUZ).v42.n1.XI",
    "platform": "uav, satellite",
    "abstract": "With the objective of applying remote sensing techniques for crop coefficient estimation and detection of changes in forest cover, in order to generate information that contributes to the sustainable management of agricultural and forestry resources, a study was conducted based on the theoretical foundations of agriculture 4.0, through the implementation of advanced technologies and intelligent data integration to optimize the entire agricultural production cycle. The methodology adopted includes the capture and processing of multispectral images from satellite platforms and unmanned aerial vehicles (UAVs), in order to obtain geometric and spectral information on various crops. Calculations of spectral indices (NDVI, NDMI, NDWI, Kc) and analysis of forest stand losses were performed using advanced software tools in GIS environment and the Google Earth Engine platform. The drone images made it possible to calculate the NDWI to classify soil moisture in high, moderate and low levels. Satellite images facilitated the identification of relationships between crop evaporation coefficient (Kc) and climatic parameters, as well as the detection of areas with forest losses in the Carrizal river basin. The results suggest strategies for the development of precision agriculture activities, promoting the substitution of conventional practices for sustainable development mechanisms based on geospatial technologies. This study contributes to the literature by demonstrating the application of advanced geospatial technologies to optimize agricultural production and sustainability. © The Authors, 2025, Published by the Universidad del Zulia.",
    "keywords": "Change detection; GEE; Kc; Spectral indices; UAV"
  },
  {
    "id": 28,
    "year": 2025,
    "authors": "Hussain, S.; Arshad, M.; Cheema, M.J.M.; Qamar, M.U.; Wajid, S.A.; Daccache, A.",
    "lead": "Hussain, S.",
    "title": "Advancing Soil Moisture Prediction Using Satellite and UAV-based Imagery Using Moisture Indices with Machine Learning Models",
    "doi": "10.1007/s41748-025-00761-5",
    "platform": "uav, satellite",
    "abstract": "Crop yields in Pakistan are significantly lower than their potential, primarily due to limited water availability and the reliance on rotation water delivery instead of demand-based water supply. The absence of spatially explicit information on water stress at the farm level further constrains overall crop productivity. Therefore, it is essential to map soil moisture availability and monitor moisture stress to enhance the efficiency of water delivery at the district level and promote precision in on-farm irrigation application. To continuously monitor soil moisture availability and identify moisture stress hotspots, peanut crops were cultivated during the 2021 and 2022 growing seasons at PMAS-Arid Agriculture University Research Center, Koont Farm, Rawalpindi. Experimental trials were conducted in both irrigated (drip irrigation) and rainfed fields to address soil moisture variability in the context of precision irrigation management. Soil moisture monitoring was performed using a combination of proximal soil moisture sensors, satellite data (Landsat 8/9 and Sentinel-2), and Unmanned Aerial Vehicles (UAVs) equipped with multispectral sensors. Satellite data and UAV imagery were processed to calculate soil moisture indices, including the Normalized Difference Water Index (NDWI), Moisture Vegetation Index (MVI), Water Stress Index (WSI), and Drought Stress Water Index (DSWI-4). Ground-truth data, including in situ soil moisture measurements at 15 cm depth and crop yield observations, were recorded for validation. A machine learning (ML) model, Random Forest (RF), was employed to accurately predict soil moisture content at 15 cm depth. The spatial maps were generated using satellite data and UAV-based imagery to identify the specific areas experiencing moisture stress. Among the moisture stress indices, WSI demonstrated a strong positive correlation with soil moisture (R² = 0.95 in 2022 and 0.85 in 2021) in the drip irrigated field. The RF model predicted soil moisture with a high accuracy (R² = 0.97 to 0.99 and RMSE = 0.00) using UAV-based moisture indices as input parameters. Furthermore, the improved surveillance of moisture stress enabled the identification of hotspot areas, allowing for the targeted implementation of protective measures for precision irrigation at the farm level. © King Abdulaziz University and Springer Nature Switzerland AG 2025.",
    "keywords": "Hot spot; NDWI; Random forest; Surveillance; Water stress; Water supply"
  },
  {
    "id": 31,
    "year": 2025,
    "sameAs": 28,
    "authors": "Hussain, S.; Arshad, M.; Cheema, M.J.M.; Qamar, M.U.; Wajid, S.A.; Daccache, A.",
    "lead": "Hussain, S.",
    "title": "Correction: Advancing Soil Moisture Prediction Using Satellite and UAV-based Imagery Using Moisture Indices with Machine Learning Models (Earth Systems and Environment, (2025), 10.1007/s41748-025-00761-5)",
    "doi": "10.1007/s41748-025-00890-x",
    "platform": "uav, satellite",
    "abstract": "In this paper, author would like to make changes in the article title, replace revised Figure 2 and changes in the acknowledgement section as given below: Published title: Advancing Soil Moisture Prediction Using Satellite and UAV-based Imagery Using Moisture Indices with Machine Learning Models Revised title: Advancing Soil Moisture Prediction Using Satellite and UAV-based Imagery with Machine Learning Models Published Figure 2 (Figure presented.) Revised Figure 2 (Figure presented.) DJI Matrices 300 UAV (a), multispectral RedEdge-MX sensor (b), GCPs (c), and calibration panel (d) Published Acknowledgement: The authors gratefully acknowledge PSDP-funded project DDSDP staff and Center for Precision Agriculture (C4PA) staff at PMAS-Arid Agriculture University Rawalpindi (UAAR), for their continuous support throughout the execution of this research. Additionally, authors would also like to thank Dr. Muhammad Naveed Tahir, Dr. Shoaib Rashid Saleem, and Dr. Muhammad Amin for their valuable guidance and support during the project. Special thanks are also extended to Basit Shahzad and Zainab Haroon for their assistance in data collection. Revised Acknowledgement: The authors gratefully acknowledge PSDP-funded project DDSDP staff and Center for Precision Agriculture (C4PA) staff at PMAS-Arid Agriculture University Rawalpindi (UAAR), for their continuous support throughout the execution of this research. Additionally, authors would also like to thank Dr. Muhammad Naveed Tahir, Dr. Shoaib Rashid Saleem, and Dr. Muhammad Amin for their valuable guidance and support during the project. Special thanks are also extended to Basit Shahzad and Zainab Haroon for their assistance in data collection. Authors are also thankful to Dr. Fitsum T. Teshome, Dr. Haimanote K. Bayabil, and the staff of Water Resources Research Group at the University of Florida, USA, for the capacity building of Saddam Hussain. © King Abdulaziz University and Springer Nature Switzerland AG 2025.",
    "keywords": ""
  },
  {
    "id": 33,
    "year": 2025,
    "authors": "Inocencio, L.C.; dos Reis, B.S.; Tognoli, F.M.W.; Moreira, C.A.; Diniz, J.L.",
    "lead": "Inocencio, L.C.",
    "title": "Soil Moisture Acquisition Through Multispectral Sensors Coupled to Unmanned Aerial Vehicle (UAV)",
    "doi": "10.1109/IGARSS55030.2025.11242585",
    "platform": "uav, satellite",
    "abstract": "This study aims to evaluate the use of remote sensing technologies in the determination of soil moisture content in an exposed soil area prepared for irrigated rice cultivation, as the knowledge of this soil property is crucial for control and productivity. These values are usually determined in a conventional way, which requires a large amount of time and allows only a few points of information in the area. With the technological advances in remote sensing, several studies are in development to determine these properties through satellite imagery, which allows mapping in large scale, but with a low spatial resolution. Therefore, the possibility of using sensors coupled in an unmanned aerial vehicle (UAV) presents a lower cost and adds a gain of time in the collection of samples. In order to generate a product representing the soil moisture from the reflectance data, aerial images were obtained using the Sequoia multispectral sensor from Parrot, which was developed for use in precision agriculture, and also were collected 85 soil samples which moisture was determined by the conventional method, serving as the basis for the study. From the samples collected in the same study area, a controlled experiment was reproduced in the laboratory using 16 samples with different moisture contents. Their spectral response was measured with a spectroradiometer to generate mathematical models that could be applied in the data collected by the Sequoia sensor and define the moisture from reflectance data. It was verified that the data from the Sequoia can be influenced by external factors, which may compromise its direct application in the models generated in the controlled experiment. In addition, there is the limitation of spectral bands of the Sequoia when compared to the spectroradiometer. ©2025 IEEE.",
    "keywords": "Multispectral Sensor; Precision Agriculture; Soil Moisture; Spectrometry; Unmanned Aerial Vehicle; Aerial photography; Aircraft control; Antennas; Cultivation; Moisture determination; Photomapping; Precision agriculture; Reflection; Remote sensing; Satellite imagery; Soil surveys; Spectrometers; %moisture; Aerial vehicle; Controlled experiment; Multispectral sensors; Precision Agriculture; Reflectance data; Remote sensing technology; Soil moisture content; Spectro-radiometers; Unmanned aerial vehicle; Soil moisture; Spectrometry; Unmanned aerial vehicles (UAV)"
  },
  {
    "id": 34,
    "year": 2025,
    "authors": "Shokati, H.; Mashal, M.; Noroozi, A.; Mirzaei, S.; Mohammadi-Doqozloo, Z.; Nabiollahi, K.; Taghizadeh-Mehrjardi, R.; Khosravani, P.; Adhikari, R.; Hu, L.; Scholten, T.",
    "lead": "Shokati, H.",
    "title": "Comparing UAV-Based Hyperspectral and Satellite-Based Multispectral Data for Soil Moisture Estimation Using Machine Learning",
    "doi": "10.3390/w17111715",
    "platform": "uav, satellite",
    "abstract": "Accurate estimation of soil moisture content (SMC) is crucial for effective water management, enabling improved monitoring of water stress and a deeper understanding of hydrological processes. While satellite remote sensing provides broad coverage, its spatial resolution often limits its ability to capture small-scale variations in SMC, especially in landscapes with diverse land-cover types. Unmanned aerial vehicles (UAVs) equipped with hyperspectral sensors offer a promising solution to overcome this limitation. This study compares the effectiveness of Sentinel-2, Landsat-8/9 multispectral data and UAV hyperspectral data (from 339.6 nm to 1028.8 nm with spectral bands) in estimating SMC in a research farm consisting of bare soil, cropland and grassland. A DJI Matrice 100 UAV equipped with a hyperspectral spectrometer collected data on 14 field campaigns, synchronized with satellite overflights. Five machine-learning algorithms including extreme learning machines (ELMs), Gaussian process regression (GPR), partial least squares regression (PLSR), support vector regression (SVR) and artificial neural network (ANN) were used to estimate SMC, focusing on the influence of land cover on the accuracy of SMC estimation. The findings indicated that GPR outperformed the other models when using Landsat-8/9 and hyperspectral photography data, demonstrating a tight correlation with the observed SMC (R2 = 0.64 and 0.89, respectively). For Sentinel-2 data, ELM showed the highest correlation, with an R2 value of 0.46. In addition, a comparative analysis showed that the UAV hyperspectral data outperformed both satellite sources due to better spatial and spectral resolution. In addition, the Landsat-8/9 data outperformed the Sentinel-2 data in terms of SMC estimation accuracy. For the different land-cover types, all types of remote-sensing data showed the highest accuracy for bare soil compared to cropland and grassland. This research highlights the potential of integrating UAV-based spectroscopy and machine-learning techniques as complementary tools to satellite platforms for precise SMC monitoring. The findings contribute to the further development of remote-sensing methods and improve the understanding of SMC dynamics in heterogeneous landscapes, with significant implications for precision agriculture. By enhancing the SMC estimation accuracy at high spatial resolution, this approach can optimize irrigation practices, improve cropping strategies and contribute to sustainable agricultural practices, ultimately enabling better decision-making for farmers and land managers. However, its broader applicability depends on factors such as scalability and performance under different conditions. © 2025 by the authors.",
    "keywords": "machine learning; precision agriculture; soil moisture; spectroscopy; UAV; Landsat; Linear regression; %moisture; Aerial vehicle; HyperSpectral; Land-cover types; LANDSAT; Machine-learning; Multi-spectral; Precision Agriculture; Soil moisture content; Unmanned aerial vehicle; bare soil; estimation method; machine learning; moisture content; multispectral image; precision agriculture; satellite altimetry; soil moisture; spectroscopy; unmanned vehicle; Target drones"
  },
  {
    "id": 24,
    "year": 2025,
    "authors": "Young, C.J.C.; Williams, H.J.; Ferro, C.F.; Wardour, E.F.; Pask, E.N.; Lee, S.-J.",
    "lead": "Young, C.J.C.",
    "title": "Advanced Crop Management and Health Assessment using Multispectral UAVs for Precision Agriculture",
    "doi": "10.2514/6.2025-3271",
    "platform": "uav, satellite",
    "abstract": "Agricultural analysis is crucial for the effective and efficient management of crops. However, the current crop monitoring processes are imprecise and slow. In this report, UAVs equipped with a full soil and crop sensor packages are used to analyze the crop health, soil quality, and moisture level of a field. The UAVs are able to collect precise data and decrease the amount of time required for the plots to be analyzed and field management plan developed. It was determined that the time required for data collection drastically decreased in comparison to typical analysis methods while also gathering more precise data and sampling more field area. Specifically, the use of UAVs with advanced sensor packages, when paired with a drone mapping tool with data processing capabilities, allows for high-resolution monitoring of soil moisture, nutrient levels, and crop health, enabling farmers to make datadriven decisions in real time. © 2025, American Institute of Aeronautics and Astronautics Inc, AIAA. All rights reserved.",
    "keywords": "Data Acquisition System; Data Processing; Drone; Machine Learning; Maximum Takeoff Weight; Multispectral Sensors; Normalized Difference Vegetation Index; Satellite Imagery; Structural Analysis; Thermal Imaging; Agricultural machinery; Crops; Data acquisition; Image processing; Information management; Learning systems; Precision agriculture; Quality control; Soil moisture; Soil quality; Soil surveys; Crop managements; Data acquisition system; Health assessments; Machine-learning; Management assessment; Maximum takeoff weights; Multispectral sensors; Normalized difference vegetation index; Sensor packages; Thermal-imaging; Data handling"
  },
  {
    "id": 32,
    "year": 2025,
    "authors": "Zhang, X.; Ram, B.; Vullaganti, N.; Aderholdt, W.; Overby, P.; Sun, X.",
    "lead": "Zhang, X.",
    "title": "Soil moisture classification using hyperspectral imaging and deep learning models on ground robot vehicles",
    "doi": "10.1016/j.atech.2025.101413",
    "platform": "uav, satellite",
    "abstract": "Soil moisture monitoring is increasingly critical in precision agriculture due to growing concerns over food security and sustainable water use. While technologies like UAVs, satellite remote sensing, IoT, and wireless sensor networks have advanced single-depth soil moisture assessment, a major gap remains in leveraging on-the-go sensing systems, particularly unmanned ground vehicles (UGVs) with hyperspectral cameras. UGV-based hyperspectral systems offer real-time, high-resolution, and cost-effective monitoring potential across multiple soil depths. Although machine learning and deep learning (DL) models have shown strong performance in predicting soil properties like soil organic matter using hyperspectral imagery, their application to soil moisture classification remains limited. This study addresses that gap by developing one-dimensional convolutional neural network (1D-CNN) to classify real-time soil moisture at 6-24 inches (15.2-61.0 cm) depth using UGV-acquired hyperspectral data. Ground truth was determined using gravimetric water content, and hyperspectral data were captured at 6, 12, 18, and 24 inches (15.2, 30.5, 45.7, and 61.0 cm). The best results were achieved using full spectral datasets enhanced with spectral augmentation methods, standard normal variation, and first/second derivative Savitzky-Golay filtering, along with balanced class weighting. The 1D-CNN models achieved testing accuracies up to 0.67 and AUC values of 0.85, outperforming models using only the top spectral bands selected by random forest and partial least squares regression. Green visible (500-565 nm) and near-infrared (750-1000 nm) regions were consistently critical for classification. This research demonstrates the potential of integrating hyperspectral imaging and DL for timely and accurate soil moisture classification, supporting precision irrigation and offering valuable tools for researchers and policymakers in agricultural water management. © 2025 The Author(s)",
    "keywords": "Convolutional neural networks; Hyperspectral imaging; Partial least squares regression; Random forest; Soil moisture; Unmanned ground vehicles"
  },
  {
    "id": 23,
    "year": 2026,
    "authors": "Liu, Q.; Wang, M.; Cui, N.; Zheng, S.; Wu, Z.; Jiang, S.; Wang, Z.; Gong, D.; Zhao, L.; Xing, L.; Zhu, G.",
    "lead": "Liu, Q.",
    "title": "Cross-regional estimation of leaf chlorophyll and soil moisture content in drip-irrigated citrus orchards using UAV data and transfer learning",
    "doi": "10.1016/j.agwat.2026.110317",
    "platform": "uav, satellite",
    "abstract": "Optimizing precision drip irrigation hinges on the synergistic management of water and fertilizer, which requires simultaneous monitoring of soil moisture content (SMC) and plant nitrogen status. However, the spatial generalization of estimation models for these key parameters remains a major challenge due to environmental heterogeneity. This study developed a transfer learning framework to achieve cross-regional estimation of both leaf chlorophyll content (LCC) and SMC in drip-irrigated citrus orchards using UAV multispectral data. Three attention mechanism-based deep learning models (CNN-LSTM-Attention (CLA), CNN-LSTM-Attention-Adaboost (CLA-A), and CNN-LSTM-Attention-XGBoost (CLA-X)) were constructed and compared. To enhance cross-regional generalization, we evaluated unsupervised (DANN, TCA) and semi-supervised (Fine-tuning, Multi-task Learning) transfer learning strategies. When directly transferred to the target domain, the models trained on the source domain exhibited performance degradation for both LCC (R2 ranging from 0.158 to 0.308) and SMC (SMC10, SMC20, and SMC40), with R2 generally below 0.20 across all depths, underscoring the limitation of direct model transfer. Notably, Fine-tuning strategies significantly enhanced the estimation accuracy in the target domain. The Fine-tuned CLA-X model achieved the best performance, yielding high accuracy for LCC (R2=0.751) and clear improvements for SMC (SMC10, SMC20, and SMC40). In contrast, unsupervised strategies (DANN, TCA) showed limited improvement (ΔR2<0.10). SHAP interpretation revealed region-specific changes in dominant predictors: REVI, GNDVI, and NDYI governed LCC estimation in the source domain, whereas NOG became more influential after transfer, suggesting stronger effects of canopy structure and background reflectance. For SMC, CERR, NDVI, and RVI2 consistently contributed most across domains, highlighting the coupling between canopy architecture and soil water status. This research proposed a viable and efficient framework that can provide crucial decision-making basis for citrus water and fertilizer management, enabling precise irrigation and nitrogen application in drip irrigation systems. © 2026 The Authors.",
    "keywords": "Cross-regional; Deep learning; Precision drip irrigation; SHAP analysis; Site-specific management; Chlorophyll; Forestry; Learning systems; Long short-term memory; Moisture determination; Orchards; Soil surveys; Subirrigation; Transfer learning; Tuning; Unmanned aerial vehicles (UAV); Unsupervised learning; Citrus orchards; Cross-regional; Deep learning; Drip irrigation; Leaf chlorophyll content; Precision drip irrigation; SHAP analyze; Site specific management; Soil moisture content; Transfer learning; canopy architecture; chlorophyll; drip irrigation; estimation method; leaf; machine learning; moisture content; NDVI; orchard; precision agriculture; satellite data; soil moisture; soil water; unmanned vehicle; Soil moisture"
  }
];

const YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026] as const;
type YearFilter = "all" | (typeof YEARS)[number];

const CATEGORIES = [
  { value: "data fusion", label: "data fusion" },
  { value: "downscaling", label: "downscaling" },
  { value: "multi-scale", label: "multi-scale" },
  { value: "one source", label: "one source" },
  { value: "ostatní", label: "ostatní" },
] as const;
type Category = (typeof CATEGORIES)[number]["value"];
type CatFilter = "all" | "unset" | Category;

function CategoryRadios({
  value,
  onChange,
}: {
  value: Category | "";
  onChange: (next: Category | "") => void;
}) {
  return (
    <Row gap={16} wrap>
      {CATEGORIES.map((c) => (
        <span key={c.value}>
          <Checkbox
            checked={value === c.value}
            onChange={(on) => onChange(on ? c.value : "")}
            label={c.label}
          />
        </span>
      ))}
    </Row>
  );
}

export default function ScalingNoneAbstracts() {
  const [year, setYear] = useCanvasState<YearFilter>("year", "all");
  const [cat, setCat] = useCanvasState<CatFilter>("cat", "all");
  const [picks, setPicks] = useCanvasState<Record<string, Category | "">>(
    "picks",
    {},
  );

  const pickOf = (id: number) => picks[String(id)] ?? "";
  const setPick = (id: number, next: Category | "") => {
    setPicks((prev) => ({ ...prev, [String(id)]: next }));
  };

  const unique = PAPERS.filter((p) => p.sameAs == null);
  const nPicked = (c: Category) =>
    unique.filter((p) => pickOf(p.id) === c).length;
  const nUnset = unique.filter((p) => pickOf(p.id) === "").length;

  const rows = PAPERS.filter((p) => {
    if (p.sameAs != null && cat !== "all") return false;
    if (year !== "all" && p.year !== year) return false;
    if (p.sameAs != null) return true;
    const v = pickOf(p.id);
    if (cat === "unset") return v === "";
    if (cat !== "all") return v === cat;
    return true;
  });

  return (
    <Stack gap={20}>
      <Stack gap={6}>
        <H1>HIGH Scaling_type = none (22 unique + Hussain correction)</H1>
        <Text tone="secondary">
          Zaškrtni právě jednu kategorii. Hussain 2025 Correction (ID 31) se
          nepočítá — je to oprava ID 28. Excel:{" "}
          30_screening/32_exports/HIGH_Scaling_none_with_abstracts.xlsx
        </Text>
      </Stack>

      <Grid columns={3} gap={12}>
        <Stat value={nUnset} label="bez zaškrtnutí" tone="warning" />
        <Stat value={nPicked("data fusion")} label="data fusion" />
        <Stat value={nPicked("downscaling")} label="downscaling" />
        <Stat value={nPicked("multi-scale")} label="multi-scale" />
        <Stat value={nPicked("one source")} label="one source" />
        <Stat value={nPicked("ostatní")} label="ostatní" />
      </Grid>

      <Callout tone="warning" title="data fusion = víc senzorů, i jedna platforma">
        Dva přístroje na jednom UAV (MS + TIR, GNSS-R + LiDAR) sloučené do
        jednoho odhadu = data fusion. Jedna MS kamera s více pásmy = one
        source. Porovnání bez sloučení = one source. Pozemní data jen jako
        validace k jednomu senzoru = one source. ostatní = nejde zařadit
        jinam.
      </Callout>
      <Callout tone="info" title="Jedna možnost na článek">
        data fusion = víc než jeden senzor nebo platforma, sloučené do jednoho
        odhadu. downscaling = z hrubšího na jemnější. multi-scale = více
        měřítek zároveň, ne převod. one source = jeden senzor, nebo dva zdroje
        vedle sebe bez sloučení. ostatní = nejde zařadit jinam.
      </Callout>

      <Row gap={8} wrap>
        <span>
          <Pill active={year === "all"} onClick={() => setYear("all")}>
            Všechny roky
          </Pill>
        </span>
        {YEARS.filter((y) => PAPERS.some((p) => p.year === y)).map((y) => (
          <span key={y}>
            <Pill active={year === y} onClick={() => setYear(y)}>
              {String(y)}
            </Pill>
          </span>
        ))}
      </Row>
      <Row gap={8} wrap>
        <span>
          <Pill active={cat === "all"} onClick={() => setCat("all")}>
            Vše
          </Pill>
        </span>
        <span>
          <Pill active={cat === "unset"} onClick={() => setCat("unset")}>
            Bez zaškrtnutí
          </Pill>
        </span>
        {CATEGORIES.map((c) => (
          <span key={c.value}>
            <Pill active={cat === c.value} onClick={() => setCat(c.value)}>
              {c.label}
            </Pill>
          </span>
        ))}
      </Row>

      <Divider />

      <Stack gap={8}>
        {rows.map((p, i) => {
          const isCorrection = p.sameAs != null;
          const selected = isCorrection ? pickOf(p.sameAs as number) : pickOf(p.id);
          return (
            <div key={p.doi}>
              <CollapsibleSection
                title={
                  (isCorrection ? "Correction k ID " + String(p.sameAs) + " — " : "") +
                  p.lead.replace(/,.*/, "") +
                  " " +
                  String(p.year) +
                  " — " +
                  p.title
                }
                trailing={
                  <Text size="small" tone={isCorrection ? "tertiary" : selected ? "secondary" : "tertiary"}>
                    {isCorrection
                      ? "nepočítat (stejný článek)"
                      : selected || "vyber jednu"}
                  </Text>
                }
                defaultOpen={i === 0}
              >
                <Stack gap={10}>
                  {isCorrection ? (
                    <Callout tone="warning" title="Publisher correction">
                      Stejný článek jako Hussain 2025 (ID 28). Do kategorií
                      uvádět jen jednou — kategorii má ID 28.
                    </Callout>
                  ) : (
                    <CategoryRadios
                      value={selected}
                      onChange={(next) => setPick(p.id, next)}
                    />
                  )}
                  <Text size="small" tone="secondary">
                    {p.authors}
                  </Text>
                  <Text size="small" tone="tertiary">
                    {p.doi} · platform: {p.platform} · ID {p.id}
                  </Text>
                  <Text>{p.abstract}</Text>
                  {p.keywords ? (
                    <Text size="small" tone="tertiary">
                      KW: {p.keywords}
                    </Text>
                  ) : null}
                </Stack>
              </CollapsibleSection>
            </div>
          );
        })}
      </Stack>
    </Stack>
  );
}
