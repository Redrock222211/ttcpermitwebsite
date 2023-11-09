from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
import time

app = Flask(__name__)


# Define your keywords here
KEYWORDS = {
    "FWO": {"Floodway Overlay (FWO): no tree controls"},
    "SBO":  {"Special Building Overlay (SBO): no tree controls"},
    "WMO" : {"Wildfire Management Overlay (WMO): no tree controls"},
    "BANYULE":  {"BANYULE: A permit is required for trees over 3m or with a trunk diameter over 50mm at breast height."},
    "BAYSIDE" : {"BAYSIDE: A permit is required to remove, destroy or lop any vegetation native to Australia in Beaumaris, Black Rock and parts of Cheltenham. This does not apply to: The removal destruction or lopping of vegetation which is less than 2 metres high or has a single trunk circumference of less than 0.5 metre at a height of 1 metre above ground level.\n The pruning of vegetation to remove that part of any branch which overhangs an existing dwelling or is within 2 metres of an existing dwelling."},
    "BALLARAT" : {"BALLARAT Exceptional Tree Register https://www.ballarat.vic.gov.au/sites/default/files/2020-10/Exceptional%20Tree%20Register%20Information.pdf"},
    "BOROONDARA": {"BOROONDARA: A permit is required for Canopy amd significant trees that have a trunk circumference of either: 110 cm or more, measured at 1.5 m above ground level 150 cm or more at ground level."},
    "BRIMBANK" :{"BRIMBANK: A trunk diameter, measured at breast height, of 50 centimetres or more A height of 15 metres or more Canopy cover of 100 square metres or more"},
    "CARDINIA": {"CARDINIA: 1 acre rule and overlays"},
    "CASEY" : {"CASEY: Significant Tree Strategy and Register."},
    "DAREBIN" : {"DAREBIN: A significant tree is a tree that has a single or combined trunk circumference greater than 100cm (1000mm) measured at 1.5m above ground level and is taller than 8m."},
    "FRANKSTON" : {"FRANKSTON: A tree that has a trunk circumference, equal to, or greater than, 110cm (measured at the base)."},
    "GEELONG" : {"GEELONG: view map https://www.planning.vic.gov.au/schemes-and-amendments/browse-planning-scheme/maps?f.Scheme%7CplanningSchemeName=greatergeelong"},
    "GLEN EIRA": {"GLEN EIRA: No LGO laws just overlays"},
    "GREATER DANDENONG": {"GREATER DANDENONG: A permit is required a protected tree with a stem diameter equal to or greater than 40cm measured at 1.4m above ground level or noxious weed."},
    "HUME" : {"HUME: You will need consent from Council"},
    "KNOX": {"KNOX: planning permit is generally required for the pruning or removal of trees see overlays"},
    "MARIBYRNONG":   {"MARIBYRNONG:\nSignificant Tree Register https://www.maribyrnong.vic.gov.au/files/assets/public/planning-services-documents/city-strategy/amendments/c163/adopted-amendment/updated-maribyrnong-significant-tree-register-august-2021-clean-version.pdf"},
    "MELBOURNE":   {"MELBOURNE:The Exceptional Tree Register AND The Significant Tree Register AND Planning Schemes"},
    "merri-bek":    {"Merri-bekYou will need a Tree Works Permit to prune more than 15% of the tree canopy or remove a tree, on private property if: the tree is considered mature or significant according to our definitions, or the tree is listed on Councils Significant Tree Register\n permit reqiored if tree taller than 8 metres, and has a single trunk diameter greater than 40cm or has multiple trunks with a combined diameter greater than 40cm (when measured at 1.2 metres above ground level)."},
    "MITCHELL":   {"MITCHELL: No LGA laws but Overlays apply"},
    "MONASH":   {"MONASH: A permit is required for 10m and has a trunk circumference greater than 50cm (16cm diameter) at 120cm above ground level "},
    "MOONEE_VALLEY":   {"MOONEE VALLEY: a permit is required for a Canopy tree is any tree with a total trunk circumference of 110 centimetres or more measured at a point 1.5 metres and Significant Tree Register "},
    "MOORABOOL":   {"MOORABOOL:Use https://www.moorabool.vic.gov.au/Building-and-planning/Do-I-need-a-permit/Remove-destroy-or-lop-a-tree-or-other-vegetation-on-your-property"},
    "MANNINGHAM": {"NO LGA LAWS OVERLAYS APPLY"},
    "MORELAND":   {"MORELAND: Mature trees  8 metres in height and has a trunk diameter greater than 40 centimetres (measured 1.2 metres from the ground). Significant trees: Any tree taller than 6 metres or listed on a proposed significant tree register."},
    "MORNINGTON_PENINSULA":   {"MORNINGTON PENINSULA:No LGA LAWS OVERLAYS apply "},
    "MURRINDINDI":   {"MURRINDINDI: Overlays and contact LGA"},
    "NILLUMBIK":   {"NILLUMBIK: trunk circumference of 50cm or greater measured at one metre above ground level; total circumference of all its trunks of 50cm or greater measured at one metre above ground level;trunk circumference of 50cm or greater measured at its base; ortrunk circumference of all its trunks of 50cm or greater measured at its base."
                    "Some exemptions from the Amenity Tree Local Law permit requirement apply to properties that are outside of the Urban Growth Boundary or properties within a designated Bushfire Prone Area or the Bushfire Management Overlay. \nAn exemption also applies where permission has already been provided for in a planning permit issued under the Nillumbik Planning Scheme; where the tree is dead; if the tree is a Pinus radiata (pine tree); or if the tree is listed on the Shire of Nillumbik Environmental Weed List 2009."},
    "PORT_PHILLIP":   {"PORT PHILLIP: Significant Tree means a tree or palm on private land With a trunk circumference of 150 centimetres or greater measured 1 metre from the baseA multi-stemmed tree where the circumference of its exterior stems equals or is greater than 1.5 metres when measured 1 metre from its base; or If the tree has been removed, a trunk circumference of 150 centimetres or greater measured at its base.Application requirement"},
    "STONNINGTON":   {"STONNINGTON: Pruning and Removal A Significant Tree is a tree or palm with a trunk circumference of 140 cm or greater measured at 1.4 m above its base with a total circumference of all its trunks of 140 cm  or greater measured at 1.4 m above its base with a trunk circumference of 180 cm or greater measured at its base with a total circumference of all its trunks of 180 cm  or greater measured at its base."},
    "KINGSTON":   {"A permit is needed to remove, prune or undertake works to any tree (including multi-stemmed trees) with a trunk circumference of 110cm or more measured at ground"},
    "SURF_COAST":   {"SURF COAST: 'Removal of any native vegetation from a property greater than 4000m2, removal of any vegetation within an Environmental Significance Overlay, removal of any vegetation specified in a schedule under a Significant Landscape Overlay or a Vegetation Protection Overlay, removal of any vegetation within a Salinity Management Overlay, removal of some trees specified in a schedule under the Heritage Overlay."},
    "YARRA":    {"YARRA significant if the diameter of its trunk or trunks measured at either ground level or a height of 1.5 meters from ground level is 40cm (400mm) or more,Significant Tree Register. Pruning permit will be requiredis tree is 40cm or more at DBH or Ground level." },
    "LGA WHITEHORSE" : {"WHITEHORSE: A planning permit is required to remove, destroy or lop native vegetation, including dead vegetation, on a property with an area greater than 0.4 hectares (4000m2).  A tree which is dead or dying or has become dangerous can be removed to the satisfaction of the responsible authority."},
    "Neighbourhood_Character_Overlay":   {"Neighbourhood Character Overlay (NCO) no tree controls"},
    "Design_and_Development_Overlay" : {"(DDO) no tree controls"},
    "Floodway_Overlay":   {"(FWO) no tree controls"},
    "Special_Building_Overlay":   {"(SBO) no tree controls"},
    "Wildfire_Management_Overlay":   {"(WMO) no tree controls"},
    "BMO":   {"BMO: Bushfire Management Overlay overlay is not defined you will need to contact the council."},
    "BMO1":   {"BMO1: Trees within 10 meters of a building should be pruned to a height of at least 2 meters and should not overhang the building's roof. Dead wood, hanging branches, and other hazardous parts of trees within 30 meters of a building should be removed. Trees should be kept away from powerlines."},
    "BMO2":   {"BMO2: Trees should be pruned or removed to reduce the risk of bushfire and protect against flooding."},
    "BMO3":   {"BMO3: Trees within 10 meters of a building should be pruned to a height of at least 2 meters and should not overhang the buildings roof. Dead wood, hanging branches, and other hazardous parts of trees within 30 meters of a building should be removed. Trees should be kept away from powerlines."},
    "ESO":   {"ESO': 'a permit is required to Remove, destroy or lop any vegetation, including dead vegetation."},
    "ESO1":   {"Environmental Significance Overlay - Schedule 1: Permit exemptions: The vegetation is identified as a pest plant in the Shire of Nillumbik Environmental Weed List 2009 as incorporated in this scheme. The vegetation is dead. This exemption does not apply to \nstanding dead trees with a trunk diameter of 40 centimetres or more at a height of 1.3 metres above ground level. The vegetation is Kunzea leptospermoides (Yarra Burgan) and is being removed for fire prevention purposes. The vegetation has been planted or grown for aesthetic or amenity purposes,\n including: agroforestry (the simultaneous and substantial production of forest and other agricultural products from the same land unit), shelter belts, woodlots, street trees, gardens or the like.\n This exemption does not apply if public funding was provided to assist in planting or managing the vegetation and the terms of the funding did not anticipate removal or harvesting of the vegetation."},
    "ESO2":   {"Environmental Significance Overlay - Schedule 2: Permit exemptions: The vegetation is identified as a pest plant in the Shire of Nillumbik Environmental Weed List 2009. The vegetation is dead (excluding standing dead trees with a trunk diameter of 40cm or more at a height of 1.3m above ground level). The vegetation is Kunzea leptospermoides and is being removed for fire prevention purposes. The vegetation has been planted or grown for aesthetic or amenity purposes, including: agroforestry, shelter belts, woodlots, street trees, gardens or the like. This exemption does not apply if public funding was provided to assist in planting or managing the vegetation and the terms of the funding did not anticipate removal or harvesting of the vegetation."},
    "ESO3":   {"Environmental Significance Overlay - Schedule 3: A permit is required to remove, destroy or lop any vegetation within this overlay. The Shire of Nillumbik will not grant a permit for the removal or destruction of any native vegetation unless it is satisfied that the proposed removal or destruction of native vegetation will not result in a net loss of vegetation or habitat values."},
    "ESO4":   {"Environmental Significance Overlay - Schedule 4: Permit exemptions: The vegetation is identified as a pest plant in the Shire of Nillumbik Environmental Weed List 2009. The vegetation is dead (excluding standing dead trees with a trunk diameter of 40cm or more at a height of 1.3m above ground level). The vegetation is Kunzea leptospermoides and is being removed for fire prevention purposes. The vegetation has been planted or grown for aesthetic or amenity purposes, including: agroforestry, shelter belts, woodlots, street trees, gardens or the like."},
    "ESO5":   {"Environmental Significance Overlay - Schedule 5: Call planning."},
    "ESO6":   {"Environmental Significance Overlay - Schedule 6: Permit exemptions: Construct a building or carry out works, remove, destroy or lop vegetation according to an agreement under section 69 of the Conservation, Forests and Lands Act 1987;\n carry out works or remove, destroy or lop vegetation by or on behalf of a public authority involving revegetation; extend or alter an existing dwelling (if the extension or alteration is less than 50 sqm and more than 5m from any existing native vegetation); \nremove, destroy or lop vegetation proclaimed as a weed, planted for aesthetic or amenity purposes (unless public funding was provided to assist planting or managing vegetation for conservation purposes), or for maintenance purposes such as mowing, slashing or maintaining an existing fence, as long as it does not exceed a combined maximum width of 4m either side of the fence."},
    "ESO7":   {"Environmental Significance Overlay - Schedule 7: Permit exemptions: A permit is not required to remove, destroy or lop vegetation that is not native vegetation."},
    "ESO8":   {"Environmental Significance Overlay - Schedule 8: Permit exemptions: A permit is not required to remove, destroy or lop vegetation that is not native vegetation."},
    "ESO9":   {"Environmental Significance Overlay - Schedule 9: Permit exemptions: A permit is not required to remove, destroy or lop vegetation that is not native vegetation."},
    "ESO10":   {"Environmental Significance Overlay - Schedule 10: Permit exemptions: Remove destroy or lop non-native vegetation; remove, destroy or lop native vegetation specified in the schedule to Clause 52.17; construct buildings and works associated with a Section 1 use in the Green Wedge Zone, Special Use Zone or Public Use Zone as long as certain requirements are met, including no building exceeding a height of 8m, total site coverage of all buildings not exceeding 10%, external cladding and roofing being painted or finished in low reflective (40% or less), neutral tones which blend with the surrounding landscape, \nand not locating septic system or development within certain distances from streams, wetlands, erosion areas or conservation zones."},
    "ESO11":   {"Environmental Significance Overlay - Schedule 11: Permit exemptions: "},
    "ESO12":   {"Environmental Significance Overlay - Schedule 12: Permit exemptions: A permit is not required to remove, destroy or lop vegetation that is not native vegetation."},
    "ESO13":   {"Environmental Significance Overlay - Schedule 13: Permit exemptions: A permit is not required to remove, destroy or lop vegetation that is not native vegetation."},
    "ESO14":   {"Environmental Significance Overlay - Schedule 14: No data."},
    "ESO15":   {"Environmental Significance Overlay - Schedule 15: Permit exemptions: A permit is not required to remove, destroy or lop vegetation that is not native vegetation."},
    "EMO":      {"A permit is required to remove, destroy or lop any vegetation. This does not apply: If a schedule to this overlay specifically states that a permit is not required. If the table to Clause 44.01-3 specifically states that a permit is not required. To the removal, destruction or lopping of native vegetation in accordance with a native vegetation precinct plan specified in the schedule to Clause 52.16"},
    "VPO":   {"Vegetation Protection Overlay - Schedule 3 Permit requirements: A permit is required to remove, destroy or lop any vegetation native to Australia, except under certain circumstances. Examples of exemptions include the removal of vegetation less than 2 metres high or with a single trunk circumference of less than 0.5 metre at a height of 1 metre above ground level,\n and the pruning of vegetation to remove part of any branch that overhangs an existing dwelling or is within 2 metres of an existing dwelling."},
    "VPO1": {"Vegetation Protection Overlay - Schedule 1 Permit requirements: A permit is required to remove, destroy or lop any vegetation, except under certain circumstances. Examples of exemptions include the removal of vegetation in conjunction with a development approved under a planning permit,\n the removal of vegetation necessary for the construction of a dwelling or outbuilding (provided no planning permit is required and certain criteria are met), \nand the removal of dead timber or branches resulting from natural causes or the spread of noxious weeds."},
    "VPO2":   {"Vegetation Protection Overlay - Schedule 2 Permit requirements: A permit is required to remove, destroy or lop any of the following vegetation: a native tree with a trunk or main stem with a girth of at least 1 metre measured 30 centimetres above ground level, or any vegetation included in a specified list."},
    "VPO3":   {"Vegetation Protection Overlay - Schedule 3 Permit requirements: A permit is required to remove, destroy or lop any vegetation native to Australia, except under certain circumstances. Examples of exemptions include the removal of vegetation less than 2 metres high or with a single trunk circumference of less than 0.5 metre at a height of 1 metre above ground level, and the pruning of vegetation to remove part of any branch that overhangs an existing dwelling or is within 2 metres of an existing dwelling."},
    "VPO4":   {"Vegetation Protection Overlay - Schedule 4 Permit requirements: A permit is required to remove, destroy or lop vegetation having a single trunk circumference of 1.0 metre or more at a height of one metre above ground level, except under certain circumstances. Examples of exemptions include the removal of vegetation deemed unsafe by a suitably qualified arborist, pruning for regeneration or ornamental shaping, and maintenance in accordance with a management program developed by a suitably qualified arborist and approved by the responsible authority."},
    "VPO5":   {"Vegetation Protection Overlay - ScheduleO5 A permit is required to remove, destroy or lop those trees which meet either of the following: Has a height of 12 metres or more, or Has a trunk or stems that collectively are more than 400mm in diameter, measured at 1400mm above the base of the tree. A permit is not required to remove, destroy or lop vegetation on land within the formation of a road or railway line which has previously been cleared where seedlings or regrowth are less than 10 years old,\n To maintain public utility services for the transmission of water, sewage, gas, electricity, electronic communications or the like, deemed immediately hazardous by a suitably qualified arborist and to the satisfaction of the responsible authority, For pruning vegetation to maintain or improve its health or appearance including regeneration or ornamental shaping, Dead to the satisfaction of the responsible authority, unless the dead vegetation is a habitat tree containing hollows, being maintained in accordance with a management program developed by a suitably qualified arborist and approved by the responsible authority, Identified as environmental weed species in Banyule City Council, Environmental Weeds 2006, unless otherwise specified in Schedule 4 to the Environmental Significance Overlay, or street trees in accordance with the Banyule Street Tree Strategy."},
    "VP06":   {"Vegetation Protection Overlay - Schedule06 Vegetation Protection Overlay - Schedule 6 A permit is required to remove, destroy or lop any native vegetation. This does not apply in the following circumstances: vegetation that is deadthe minimum extent of vegetation necessary for the maintenance of existing fences; for theremoval or lopping of the minimum extent of vegetation necessary for regular maintenance carried out by or on behalf of a public authority, government department or municipal council;\n for the removal, destruction or lopping of any vegetation deemed unsafe by a suitably qualified arborist and/or to the satisfaction of the responsible authority; for activities conducted on public land by or on behalf of the Department of Natural Resources and Environment under the relevant provisions of the Reference Areas Act 1978, the National Parks Act 1975, the Fisheries Act 1995 the Wildlife Act 1975, the Land Act 1958, the Crown Land (Reserves) Act 1978 or the Forests Act 1958."},
    "VP07":   {"Vegetation Protection Overlay - ScheduleO7 Vegetation Protection Overlay - Schedule 7 A permit is required to remove, destroy or lop any vegetation. This does not apply in the following circumstances: Vegetation that is dead or less than 2 metres in height. The minimum extent of vegetation necessary for the maintenance of existing fences. For the removal or lopping of the minimum extent of vegetation necessary for regular maintenance carried out by or on behalf of a public authority,\n government department or municipal council. For the removal, destruction or lopping of any vegetation deemed unsafe by a suitably qualified arborist and/or to the satisfaction of the responsible authority."},
    "VPO8":   {"Vegetation Protection Overlay - ScheduleO8 Vegetation Protection Overlay - Schedule 8 A permit is required to remove, destroy or lop any vegetation. This does not apply to the following circumstances:To vegetation that is dead or less than 2 metres in height or less than 10 years old.To pruning of garden vegetation in the course of regular maintenance, providing this does not significantly affect the extent or nature of vegetation on a lot.To the minimum extent of vegetation necessary for the \nmaintenance of existing fences.For the removal or lopping of the minimum extent of vegetation necessary for regular maintenance carried out by or on behalf of a public authority, government department or municipal council.For the removal, destruction or lopping of any vegetation deemed unsafe by a suitably qualified arborist and/or to the satisfaction of the responsible authority.For activities conducted on public land by or on behalf of the Department of Sustainability and Environment under the relevant provisions of the Reference Areas Act 1978, the National Parks Act 1975, the Fisheries Act 1995, the Wildlife Act 1975, the Land Act 1958, the Crown Land (Reserves) Act 1978 or the Forests Act 1958.To the minimum extent of vegetation necessary for fire prevention or mitigation as determined in the East Gippsland Municipal Fire Prevention Plan, or as directed from time to time by the Municipal Fire Prevention Officer or authorised Officer of the Country Fire Authority acting pursuant to the Country Fire Authority Act or as directed by an Officer of the Country Fire Authority or Department of Sustainability and Environment in the performance of their duties necessary in the control of wildfire."},
    "VPO9":   {"Vegetation Protection Overlay - Schedule 9 A permit is required to remove, destroy or lop any native vegetation. This does not apply to the removal, destruction and lopping of vegetation which is associated with the collection of firewood for private use."},
    "VPO10":   {"Vegetation Protection Overlay - Schedule 10 No permit is required to remove destroy or lop vegetation to the minimum extent necessary if any of the following apply: Bracken The vegetation is bracken Pteridium esculentum which has naturally established or regenerated on land lawfully cleared of naturally established vegetation. This exemption does not apply to land on which vegetation has been cleared or otherwise destroyed or damaged as a result of flood, fire or other natural disaster. \nCrown land The vegetation is to be removed, destroyed or lopped on Crown land and by a person acting under and in accordance with an authorisation order made under sections 82 or 84 of the Traditional Owner Settlement Act 2010. Emergency works 2022 The vegetation presents an immediate risk of personal injury or damage to property and only that part of vegetation which presents the immediate risk is removed, destroyed or lopped. The vegetation is to be removed, destroyed or lopped by a public authority or municipal council to create an emergency access or to enable emergency works. Fire protection 2022 The vegetation is to be removed, destroyed or lopped for the making of a fuel break by or on behalf of a public authority in accordance with a strategic fuel break plan approved by the Secretary to the Department of Environment, Land, Water and Planning (as constituted under Part 2 of the Conservation, Forest and Lands Act 1987). The maximum width of a fuel break must not exceed 40 metres. The vegetation is to be removed, destroyed or lopped for fire fighting measures, fuel reduction burning, or the making of a fuel break up to 6 metres wide. The vegetation is ground fuel within 30 metres of a building. The vegetation is to be removed, destroyed or lopped in accordance with a fire prevention notice under: Section 65 of the Forests Act 1958. Section 41 of the Country Fire Authority Act 1958. Section 8 of the Local Government Act 1989. The vegetation is to be removed, destroyed or lopped to keep the whole or any part of any vegetation clear of an electric line in accordance with a code of practice prepared under Part 8 of the Electricity Safety Act 1998. The vegetation is to be removed, destroyed or lopped in accordance with any code of practice prepared in accordance with Part 8 of the Electricity Safety Act 1998 in order to minimise the risk of bushfire ignition in the proximity of electricity lines. The vegetation is to be removed, destroyed or lopped to reduce fuel loads on roadsides to minimise the risk to life and property from bushfire of an existing public road managed by the relevant responsible road authority (as defined by the Road Management Act 2004)  in accordance with the written}"},
    "VPO11":   {"Vegetation Protection Overlay - Schedule 11 The removal of vegetation which is to be carried out in conjunction with a development approved under a planning permit and in accordance with an endorsed plan. The removal of vegetation necessary for the construction of a dwelling, dwelling extension or outbuilding where no planning permit is required and provided that: A building permit has been granted for the proposed development. Vegetation is only removed from the building footprint or within 2 metres of the proposed building.\n No tree with a trunk circumference greater than 0.35 metres is removed within 6 metres of a road frontage. The removal of vegetation, not within a road reserve, to enable the formation of a single crossing and access driveway with a maximum width of 3.7 metres. The removal of vegetation which presents an immediate risk of personal injury or damage to property including the culling of single trees located within 3 metres of a dwelling or outbuilding, or which overhangs a boundary line. The removal of any dead timber or branch which has occurred through natural circumstances, fire or the spread of noxious weeds. The removal of any tree or branch of a tree which impairs the access of motor vehicles along any existing or approved access track, provided that such access track has a width no greater than 3.7 metres. The maintenance of landscaping, including pruning, which does not effect the stability, general form and viability of the vegetation. The removal of vegetation that has been established for less than 10 years and which is not required as landscaping under a planning approval. The removal of vegetation specified in the schedule to Clause 52.17"},
    "HO":   {"will need to manually search the folowing https://vhd.heritagecouncil.vic.gov.au/"},
    "SLO1":   {"SLO1 : A permit is required to remove, destroy, prune or lop substantial trees and native vegetation except where:The vegetation is an environmental weed as specified in Table 1 to this schedule Undertaken by or on behalf of Parks Victoria as a public land manager.The pruning or loping of limbs is less than one-third (1/3rd) of the crown of the tree.The vegetation is within a building envelope, fire protection buffer, or is required to be removed for the construction of roads, property access and services shown on an endorsed plan required by section 1.0 of schedule 6, to the Development Plan Overlay."},
    "SLO2":   {"SLO2 : A permit is required to remove, destroy, prune or lop Australian native trees and remnant indigenous understory vegetation, except where: The vegetation is an environmental weed as specified in Table 1 to this schedule."},
    "SLO3":   {"SLO3 : A permit is required to remove, destroy prune or lop any substantial tree except where: The substantial tree is an environmental weed as specified in Table 1 to this schedule.The pruning or loping of limbs is less than one-third (1/3rd) of the crown of the tree."},
    "SLO4":   {"SLO4 : A permit is required to remove, destroy prune or lop any substantial tree except where: The substantial tree is an environmental weed as specified in Table 1 to this schedule.The pruning or loping of limbs is less than one-third (1/3rd) of the crown of the tree."},
    "SLO5":   {" SLO5 : A permit is required: To remove, destroy or lop vegetation that is listed in Table 1 to this schedule.For buildings and works within the tree protection zone of any tree that is listed in Table 1 to this schedule.A permit is not required: For buildings and works outside the tree protection zone of any tree listed in Table 1 to this schedule. To prune lop limbs less than 75mm in diameter and not more than a total of 10% of the canopy of any significant tree listed in the table to this schedule for:- maintaining access to existing roads, driveways and footpaths clearing within two metres of an existing permanent structure;- maintaining of an existing specialised pruning method such as hedging, espalier or topiary reducing overhang to neighbouring properties. To remove dead and broken limbs.All pruning works must be carried out in accordance with Australian Standard AS4373-2009 Pruning of Amenity Trees Before deciding on an application to remove, destroy, prune or lop any specified tree or area of vegetation, the responsible authority may require the applicant to provide a report prepared by a qualified arborist ecologist, or botanist on the reason and need for the proposed work, options for alternative treatments and any remedial or restorative action proposed"},
    "SLO6":   {"SLO6 : A permit is required to remove, destroy prune or lop any substantial tree except where: The substantial tree is an environmental weed as specified in Table 1 to this schedule.The pruning or 'loping of limbs is less than one-third (1/3rd) of the crown of the tree."},
   }



def scrape_website(query):
    # Initialize your web scraping logic here
    result = ""

    # Create an instance of the Chrome driver in headless mode
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--allow-insecure-localhost")
    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to the website
        driver.get('https://mapshare.vic.gov.au/Vicplan')

        # Wait for the modal to load and agree to the terms
        modal_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "modal-title"))
        )
        agree_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div[4]/div/div[3]/div/div/form/div[2]/button[2]")
            )
        )
        agree_btn.click()

        # click the overlays
        modal_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "modal-title"))
        )
        agree_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[1]/div/div[1]/div/div[1]/div[4]/div/div/div[2]/div[1]/ul/li[1]/div/ul/li[7]/button")
            )
        )
        agree_btn.click()

        # Find the search box using XPATH
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[2]/div[5]/div[5]/div/span/input")
            )
        )
        # Click on the search box to give it focus
        search_box.click()

        # Find the search box using XPATH and input the search term
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[2]/div[5]/div[5]/div/span/input")
            )
        )
        # Input the search term with a 0.1-second delay between characters
        for char in query:
            search_box.send_keys(char)
            time.sleep(0.01)

        # Find the search box using XPATH
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[2]/div[5]/div[5]/div/span/input")
            )
        )

        # Click on the search box to give it focus
        search_box.click()

        # Wait for the suggestion and click it
        time.sleep(0.5)
        suggestion = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//html/body/div[1]/div/div[1]/div/div[2]/div[2]/div/div/div[2]/div[5]/div[5]/div/span/div/div[1]/div")
            )
        )
        suggestion.click()

        time.sleep(0.5)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[5]/div/div[3]/div[3]/div/div[2]/div[6]")
            )
        )

        # Get the HTML source of the page
        html_source = driver.page_source

        # Parse the HTML content into an lxml tree
        tree = html.fromstring(html_source)

        # Find the element using its XPath expression
        elements = tree.xpath(
            '/html/body/div[1]/div/div[1]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[5]/div/div[3]/div[3]/div/div[2]'
        )

        element = driver.find_element(
            By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[5]/div/div[3]/div[3]/div/div[2]"
        )
        element_text = element.text
        print("Element Text:", element_text)

        # Build the result string
        result = f"Element Text: {element_text}\n\n"

        # Loop through the lines of text and check for matching keywords
        matched_lines = []

        # Loop through each line in the text
        for line in element_text.split('\n'):
            # Loop through each keyword in the list of keywords
            for keyword, values in KEYWORDS.items():
                # if the keyword is found in the line, add the keyword to the list of matched lines
                if keyword in line:
                    matched_lines.append(keyword)
                else:
                    print(f"Keyword '{keyword}' not found in line: '{line}'")

        # Create a set of matched keywords
        matched_keywords = {keyword: value for keyword, value in KEYWORDS.items() if keyword in matched_lines}

        # Add matched keywords to the result string
        result += "\nMatched Keywords:\n"
        for key, value in matched_keywords.items():
            result += f"{key}: {value}\n"

    except Exception as e:
        print("An error occurred:", str(e))

    finally:
        if driver is not None:
            driver.quit()  # Close the driver if it was created

    if not result:
        result = "No matching data found."

    return result


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""  # Initialize result variable
    if request.method == "POST":
        query = request.form.get("query")
        result = scrape_website(query)
    return render_template("index.html", result=result)



if __name__ == "__main__":
    app.run(debug=True)
