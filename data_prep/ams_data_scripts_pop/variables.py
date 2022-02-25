import os
import psycopg2
from sqlalchemy import create_engine

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
city ='ams'
# Paths for the Population Data --------------------------------------------------------------
#path to ancillary data folder
ancillary_data_folder_path = base_dir + "/data_prep/{}_Projectdata/AncillaryData".format(city)
ancillary_POPdata_folder_path = base_dir + "/data_prep/{}_Projectdata/PopData".format(city)
ancillary_EUROdata_folder_path =  base_dir + "/data_prep/euroData"

# Other Paths to necessary python scripts and functions ----------------------------------------------------------------
# path to folder containing gdal_calc.py and gdal_merge.py
python_scripts_folder_path = r'C:/Users/NM12LQ/Anaconda3/envs/pop_env/Scripts' #O:/projekter/PY000014_D/popnet_env/Scripts
#path to folder with gdal_rasterize.exe
gdal_rasterize_path = r'C:/Users/NM12LQ/Anaconda3/envs/pop_env/Library/bin' #O:/projekter/PY000014_D/popnet_env/Library/bin
gdal_path = r'C:/Users/NM12LQ/Anaconda3/envs/pop_env/Lib/site-packages/osgeo'

deliver_path = base_dir + "/data_prep/Deliverable"
# Specify database information -----------------------------------------------------------------------------------------
# path to postgresql bin folder
pgpath = r";C:/Program Files/PostgreSQL/9.5/bin"
pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = '{}_data'.format(city)
engine = create_engine(f'postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}?gssencmode=disable')
conn = psycopg2.connect(database=pgdatabase, user=pguser, host=pghost, password=pgpassword,sslmode="disable",gssencmode="disable")
cur = conn.cursor()

# Specify countries by region -----------------------------------------------------------------------------------------
country_Orig = {"Oceania" : ["aus","cxr", "cck", "hmd", "nzl", "nfk",
                        "fji","png","slb","vut", "ncl",
                        "gum","kir","mhl","fsm","nru","mnp","plw","umi",
                        "asm","cok","pyf","niu","pcn","wsm","tkl","ton","tuv","wlf"], #29
            "Australia" : ["aus","cxr", "cck", "hmd", "nzl", "nfk"], #6
            "Malanesia":["fji","png","slb","vut", "ncl"], #5
            "Micronesia": ["gum","kir","mhl","fsm","nru","mnp","plw","umi"], #8
            "Polynesia": ["asm","cok","pyf","niu","pcn","wsm","tkl","ton","tuv","wlf"], #10
            
            "Europe": ["pol", "blr","bgr","cze","hun","mda","rou","rus","svk","ukr",
                        "bih","mkd","alb","and","hrv","gib","grc","vat","mlt","mne",
                        "prt","ita","smr","srb","svn","esp",
                        "deu","nld","aut","bel","fra","lie","lux","mco","che",
                        "gbr","nor","irl","swe","lva","est","isl","sjm","fro","fin",
                        "jey","imn","ltu","ggy","ala", "dnk"],
            "EuropenoLocal": ["pol", "blr","bgr","cze","hun","mda","rou","rus","svk","ukr",
                        "bih","mkd","alb","and","hrv","gib","grc","vat","mlt","mne",
                        "prt","ita","smr","srb","svn","esp",
                        "deu","aut","bel","fra","lie","lux","mco","che",
                        "gbr","nor","irl","swe","lva","est","isl","sjm","fro","fin",
                        "jey","imn","ltu","ggy","ala", "dnk"],#"nld",
            "Eastern_Europe":["pol", "blr","bgr","cze","hun","mda","rou","rus","svk","ukr"], #10
            "Southern_Europe":["bih","mkd","alb","and","hrv","gib","grc","vat","mlt","mne",
                                "prt","ita","smr","srb","svn","esp"], #16
            "Western_Europe": ["deu","nld","aut","bel","fra","lie","lux","mco","che"], #9
            "Western_EuropenoLocal": ["deu","aut","bel","fra","lie","lux","mco","che"], #8 #"nld",
            "Northern_Europe": ["gbr","nor","irl","swe","lva","est","isl","sjm","fro","fin",
                                "jey","imn","ltu","ggy","ala", "dnk"], #16 with Channel Islands, missing Sark
            "EuropeEU": ["lie","nor", "isl","che",
                        "gbr",
                        "bgr","cze","hun","rou","svk","dnk","est","fin","irl","cyp",
                        "swe","lva","hrv","grc","ita","mlt","prt","svn","esp","aut",
                        "bel","fra","deu","lux","mco","nld","pol"],#32
            "EuropeNotEU": [ "blr","mda","rus", "ukr", "ala", "ggy", "jey", "fro", "imn","sjm",
                                "alb", "and", "bih", "gib", "vat", "mne", "mkd", "smr", "srb"],
            "EuropeEUnoLocal": ["lie","nor", "isl","che",
                        "gbr",
                        "bgr","cze","hun","rou","svk","dnk","est","fin","irl","cyp",
                        "swe","lva","hrv","grc","ita","mlt","prt","svn","esp","aut",
                        "bel","fra","deu","lux","mco"],#"nld"
            
            "Asia":["kaz","kgz","tjk","tkm","uzb",
                    "chn", "hkg", "mac", "prk", "jpn", "mng", "kor",
                    "phl","vnm","brn","khm","idn","lao","mys","mmr","sgp","tha",
                    "tls",
                    "afg","ind","irn","pak","bgd","btn","npl", "mdv","lka",
                    "arm","aze","bhr","geo","irq","isr","jor","kwt","lbn","omn",
                    "qat","sau","pse","syr","tur","are","yem","cyp"],
            "Central_Asia":["kaz","kgz","tjk","tkm","uzb"], #5
            "Eastern_Asia":["chn", "hkg", "mac", "prk", "jpn", "mng", "kor"], #7
            "Southern-Eastern_Asia":["phl","vnm","brn","khm","idn","lao","mys","mmr","sgp","tha",
                                    "tls"], #11
            "Southern_Asia":["afg","ind","irn","pak","bgd","btn","npl", "mdv","lka"], #9
            
            "Western_Asia":["arm","aze","bhr","geo","irq","isr","jor","kwt","lbn","omn",
                            "qat","sau","pse","syr","tur","are","yem","cyp"], #18
            "Antarctica":["ata"],

            "Americas":["bmu","can","grl","spm","usa",
                        "aia","atg","abw","bhs","brb","bes","vgb","cym","cub","cuw",
                        "dma","dom","grd","glp","hti","jam","mtq","msr","pri","blm",
                        "kna","lca","maf","vct","sxm","tto","tca","vir","blz","cri",
                        "slv","gtm","hnd","mex","nic","pan","arg","bol","bvt","bra",
                        "chl","col","ecu","flk","guf","guy","pry","per","sgs","sur",
                        "ury","ven"],
            "Northern_America":["bmu","can","grl","spm","usa"],#5
            "Latin_America_and_the_Caribbean": ["aia","atg","abw","bhs","brb","bes","vgb","cym","cub","cuw",
                                                "dma","dom","grd","glp","hti","jam","mtq","msr","pri","blm",
                                                "kna","lca","maf","vct","sxm","tto","tca","vir","blz","cri",
                                                "slv","gtm","hnd","mex","nic","pan","arg","bol","bvt","bra",
                                                "chl","col","ecu","flk","guf","guy","pry","per","sgs","sur",
                                                "ury","ven"],#52
            
            "Africa":["mar","dza","egy","lby","sdn","tun","esh",
                        "cmr","som","nga","sen", "iot","bdi","com","dji","eri","eth",
                        "atf","ken","mdg","mwi","mus","myt","moz","reu","rwa","syc",
                        "ssd","uga","tza","zmb","zwe","ago","caf","tcd","cog","cod",
                        "gnq","gab","stp","bwa","swz","lso","nam","zaf","ben","bfa",
                        "cpv","civ","gmb","gha","gin","gnb","lbr","mli","mrt","ner",
                        "shn","sle","tgo"], 
            "Northern_Africa":["mar","dza","egy","lby","sdn","tun","esh"], #7
            "Sub-Saharan_Africa":["cmr","som","nga","sen", "iot","bdi","com","dji","eri","eth",
                                    "atf","ken","mdg","mwi","mus","myt","moz","reu","rwa","syc",
                                    "ssd","uga","tza","zmb","zwe","ago","caf","tcd","cog","cod",
                                    "gnq","gab","stp","bwa","swz","lso","nam","zaf","ben","bfa",
                                    "cpv","civ","gmb","gha","gin","gnb","lbr","mli","mrt","ner",
                                    "shn","sle","tgo"], #53
            
            "OutsideEurope":["aus","cxr", "cck", "hmd", "nzl", "nfk",
                        "fji","png","slb","vut", "ncl",
                        "gum","kir","mhl","fsm","nru","mnp","plw","umi",
                        "asm","cok","pyf","niu","pcn","wsm","tkl","ton","tuv","wlf",
                        
                        "kaz","kgz","tjk","tkm","uzb",
                        "chn", "hkg", "mac", "prk", "jpn", "mng", "kor",
                        "phl","vnm","brn","khm","idn","lao","mys","mmr","sgp","tha",
                        "tls",
                        "afg","ind","irn","pak","bgd","btn","npl", "mdv","lka",
                        "arm","aze","bhr","geo","irq","isr","jor","kwt","lbn","omn",
                        "qat","sau","pse","syr","tur","are","yem","cyp",
                    
                        "bmu","can","grl","spm","usa",
                        "aia","atg","abw","bhs","brb","bes","vgb","cym","cub","cuw",
                        "dma","dom","grd","glp","hti","jam","mtq","msr","pri","blm",
                        "kna","lca","maf","vct","sxm","tto","tca","vir","blz","cri",
                        "slv","gtm","hnd","mex","nic","pan","arg","bol","bvt","bra",
                        "chl","col","ecu","flk","guf","guy","pry","per","sgs","sur",
                        "ury","ven",
                        
                        "mar","dza","egy","lby","sdn","tun","esh",
                        "cmr","som","nga","sen", "iot","bdi","com","dji","eri","eth",
                        "atf","ken","mdg","mwi","mus","myt","moz","reu","rwa","syc",
                        "ssd","uga","tza","zmb","zwe","ago","caf","tcd","cog","cod",
                        "gnq","gab","stp","bwa","swz","lso","nam","zaf","ben","bfa",
                        "cpv","civ","gmb","gha","gin","gnb","lbr","mli","mrt","ner",
                        "shn","sle","tgo"],
            "Others": ["oth","unk","othe","urs","otham","yug","othaf","cenam","nstd","othme","othas","scg","tch","othna","sta"] ,
            "Colonies" :['ukcol','belcol','prtcol','nldcol','fracol' ]}

country_OrigWnW = {"nld":['nld'],
                   "ant":['ant'],
                   "mar":['mar'],
                   "tur":['tur'],     
            "Western":["aus","cxr", "cck", "hmd", "nzl", "nfk",
                        "fji","png","slb","vut", "ncl",
                        "gum","kir","mhl","fsm","nru","mnp","plw","umi",
                        "asm","cok","pyf","niu","pcn","wsm","tkl","ton","tuv","wlf",
                        "pol", "blr","bgr","cze","hun","mda","rou","rus","svk","ukr",
                        "bih","mkd","alb","and","hrv","gib","grc","vat","mlt","mne",
                        "prt","ita","smr","srb","svn","esp",
                        "deu","aut","bel","fra","lie","lux","mco","che",
                        "gbr","nor","irl","swe","lva","est","isl","sjm","fro","fin",
                        "jey","imn","ltu","ggy","ala", "dnk",
                        "bmu","can","grl","spm","usa",
                        "jpn", "idn"],
            "nonWestern":["kaz","kgz","tjk","tkm","uzb",
                    "chn", "hkg", "mac", "prk", "mng", "kor",
                    "phl","vnm","brn","khm","lao","mys","mmr","sgp","tha",
                    "tls",
                    "afg","ind","irn","pak","bgd","btn","npl", "mdv","lka",
                    "arm","aze","bhr","geo","irq","isr","jor","kwt","lbn","omn",
                    "qat","sau","pse","syr","are","yem","cyp",
                        "aia","atg","abw","bhs","brb","bes","vgb","cym","cub","cuw",
                        "dma","dom","grd","glp","hti","jam","mtq","msr","pri","blm",
                        "kna","lca","maf","vct","sxm","tto","tca","vir","blz","cri",
                        "slv","gtm","hnd","mex","nic","pan","arg","bol","bvt","bra",
                        "chl","col","ecu","flk","guf","guy","pry","per","sgs","sur",
                        "ury","ven",
                        "dza","egy","lby","sdn","tun","esh",
                        "cmr","som","nga","sen", "iot","bdi","com","dji","eri","eth",
                        "atf","ken","mdg","mwi","mus","myt","moz","reu","rwa","syc",
                        "ssd","uga","tza","zmb","zwe","ago","caf","tcd","cog","cod",
                        "gnq","gab","stp","bwa","swz","lso","nam","zaf","ben","bfa",
                        "cpv","civ","gmb","gha","gin","gnb","lbr","mli","mrt","ner",
                        "shn","sle","tgo"
                    'ukcol','belcol','prtcol','fracol', #'nldcol'
                    "oth","unk","othe","urs","otham","yug","othaf","cenam","nstd","othme","othas","scg","tch","othna","sta"
            ]}