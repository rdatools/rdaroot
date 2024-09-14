########## Scripts for testing generation of root maps #########

# NC/congress

scripts/rmfrsp_ensemble.py \
--state NC \
--plantype congress \
--roughlyequal 0.01 \
--size 100 \
--data ../rdabase/data/NC/NC_2020_data.csv \
--shapes ../rdabase/data/NC/NC_2020_shapes_simplified.json \
--graph ../rdabase/data/NC/NC_2020_graph.json \
--plans ../../iCloud/fileout/root_maps/NC20C_plans.json \
--log ../../iCloud/fileout/root_maps//NC20C_log.txt \
--no-debug

scripts/approx_root_map.py \
--state NC \
--plans ../../iCloud/fileout/root_maps/NC20C_plans.json \
--data ../rdabase/data/NC/NC_2020_data.csv \
--shapes ../rdabase/data/NC/NC_2020_shapes_simplified.json \
--graph ../rdabase/data/NC/NC_2020_graph.json \
--map ../../iCloud/fileout/root_maps/NC20C_root_map.csv \
--candidates ../../iCloud/fileout/root_maps/NC20C_root_candidates.json \
--log ../../iCloud/fileout/root_maps/NC20C_root_log.txt \
--no-debug


# NC/upper

scripts/rmfrsp_ensemble.py \
--state NC \
--plantype upper \
--roughlyequal 0.10 \
--size 100 \
--data ../rdabase/data/NC/NC_2020_data.csv \
--shapes ../rdabase/data/NC/NC_2020_shapes_simplified.json \
--graph ../rdabase/data/NC/NC_2020_graph.json \
--plans ../../iCloud/fileout/root_maps/NC20U_plans.json \
--log ../../iCloud/fileout/root_maps//NC20U_log.txt \
--no-debug

scripts/approx_root_map.py \
--state NC \
--plans ../../iCloud/fileout/root_maps/NC20U_plans.json \
--data ../rdabase/data/NC/NC_2020_data.csv \
--shapes ../rdabase/data/NC/NC_2020_shapes_simplified.json \
--graph ../rdabase/data/NC/NC_2020_graph.json \
--map ../../iCloud/fileout/root_maps/NC20U_plans.json/NC20U_root_map.csv \
--candidates ../../iCloud/fileout/root_maps/NC20U_root_candidates.json \
--log ../../iCloud/fileout/root_maps/NC20U_root_log.txt \
--no-debug


# NC/lower

scripts/rmfrsp_ensemble.py \
--state NC \
--plantype lower \
--roughlyequal 0.10 \
--size 100 \
--data ../rdabase/data/NC/NC_2020_data.csv \
--shapes ../rdabase/data/NC/NC_2020_shapes_simplified.json \
--graph ../rdabase/data/NC/NC_2020_graph.json \
--plans ../../iCloud/fileout/root_maps/NC20L_plans.json \
--log ../../iCloud/fileout/root_maps//NC20L_log.txt \
--no-debug

scripts/approx_root_map.py \
--state NC \
--plans ../../iCloud/fileout/root_maps/NC20L_plans.json \
--data ../rdabase/data/NC/NC_2020_data.csv \
--shapes ../rdabase/data/NC/NC_2020_shapes_simplified.json \
--graph ../rdabase/data/NC/NC_2020_graph.json \
--map ../../iCloud/fileout/root_maps/NC20L_plans.json/NC20L_root_map.csv \
--candidates ../../iCloud/fileout/root_maps/NC20L_root_candidates.json \
--log ../../iCloud/fileout/root_maps/NC20L_root_log.txt \
--no-debug

##########

# MD/congress

scripts/rmfrsp_ensemble.py \
--state MD \
--plantype congress \
--roughlyequal 0.01 \
--size 100 \
--data ../rdabase/data/MD/MD_2020_data.csv \
--shapes ../rdabase/data/MD/MD_2020_shapes_simplified.json \
--graph ../rdabase/data/MD/MD_2020_graph.json \
--plans ../../iCloud/fileout/root_maps/MD20C_plans.json \
--log ../../iCloud/fileout/root_maps//MD20C_log.txt \
--no-debug

scripts/approx_root_map.py \
--state MD \
--plans ../../iCloud/fileout/root_maps/MD20C_plans.json \
--data ../rdabase/data/MD/MD_2020_data.csv \
--shapes ../rdabase/data/MD/MD_2020_shapes_simplified.json \
--graph ../rdabase/data/MD/MD_2020_graph.json \
--map ../../iCloud/fileout/root_maps/MD20C_plans.json/MD20C_root_map.csv \
--candidates ../../iCloud/fileout/root_maps/MD20C_root_candidates.json \
--log ../../iCloud/fileout/root_maps/MD20C_root_log.txt \
--no-debug


# MD/upper

scripts/rmfrsp_ensemble.py \
--state MD \
--plantype upper \
--roughlyequal 0.10 \
--size 100 \
--data ../rdabase/data/MD/MD_2020_data.csv \
--shapes ../rdabase/data/MD/MD_2020_shapes_simplified.json \
--graph ../rdabase/data/MD/MD_2020_graph.json \
--plans ../../iCloud/fileout/root_maps/MD20U_plans.json \
--log ../../iCloud/fileout/root_maps//MD20U_log.txt \
--no-debug

scripts/approx_root_map.py \
--state MD \
--plans ../../iCloud/fileout/root_maps/MD20U_plans.json \
--data ../rdabase/data/MD/MD_2020_data.csv \
--shapes ../rdabase/data/MD/MD_2020_shapes_simplified.json \
--graph ../rdabase/data/MD/MD_2020_graph.json \
--map ../../iCloud/fileout/root_maps/MD20U_plans.json/MD20U_root_map.csv \
--candidates ../../iCloud/fileout/root_maps/MD20U_root_candidates.json \
--log ../../iCloud/fileout/root_maps/MD20U_root_log.txt \
--no-debug


# MD/lower -- N/A, uses MMD


##########

# PA/congress

scripts/rmfrsp_ensemble.py \
--state PA \
--plantype congress \
--roughlyequal 0.01 \
--size 100 \
--data ../rdabase/data/PA/PA_2020_data.csv \
--shapes ../rdabase/data/PA/PA_2020_shapes_simplified.json \
--graph ../rdabase/data/PA/PA_2020_graph.json \
--plans ../../iCloud/fileout/root_maps/PA20C_plans.json \
--log ../../iCloud/fileout/root_maps//PA20C_log.txt \
--no-debug

scripts/approx_root_map.py \
--state PA \
--plans ../../iCloud/fileout/root_maps/PA20C_plans.json \
--data ../rdabase/data/PA/PA_2020_data.csv \
--shapes ../rdabase/data/PA/PA_2020_shapes_simplified.json \
--graph ../rdabase/data/PA/PA_2020_graph.json \
--map ../../iCloud/fileout/root_maps/PA20C_plans.json/PA20C_root_map.csv \
--candidates ../../iCloud/fileout/root_maps/PA20C_root_candidates.json \
--log ../../iCloud/fileout/root_maps/PA20C_root_log.txt \
--no-debug


# PA/upper

scripts/rmfrsp_ensemble.py \
--state PA \
--plantype upper \
--roughlyequal 0.10 \
--size 100 \
--data ../rdabase/data/PA/PA_2020_data.csv \
--shapes ../rdabase/data/PA/PA_2020_shapes_simplified.json \
--graph ../rdabase/data/PA/PA_2020_graph.json \
--plans ../../iCloud/fileout/root_maps/PA20U_plans.json \
--log ../../iCloud/fileout/root_maps//PA20U_log.txt \
--no-debug

scripts/approx_root_map.py \
--state PA \
--plans ../../iCloud/fileout/root_maps/PA20U_plans.json \
--data ../rdabase/data/PA/PA_2020_data.csv \
--shapes ../rdabase/data/PA/PA_2020_shapes_simplified.json \
--graph ../rdabase/data/PA/PA_2020_graph.json \
--map ../../iCloud/fileout/root_maps/PA20U_plans.json/PA20U_root_map.csv \
--candidates ../../iCloud/fileout/root_maps/PA20U_root_candidates.json \
--log ../../iCloud/fileout/root_maps/PA20U_root_log.txt \
--no-debug


# PA/lower

scripts/rmfrsp_ensemble.py \
--state PA \
--plantype lower \
--roughlyequal 0.10 \
--size 100 \
--data ../rdabase/data/PA/PA_2020_data.csv \
--shapes ../rdabase/data/PA/PA_2020_shapes_simplified.json \
--graph ../rdabase/data/PA/PA_2020_graph.json \
--plans ../../iCloud/fileout/root_maps/PA20L_plans.json \
--log ../../iCloud/fileout/root_maps//PA20L_log.txt \
--no-debug

scripts/approx_root_map.py \
--state PA \
--plans ../../iCloud/fileout/root_maps/PA20L_plans.json \
--data ../rdabase/data/PA/PA_2020_data.csv \
--shapes ../rdabase/data/PA/PA_2020_shapes_simplified.json \
--graph ../rdabase/data/PA/PA_2020_graph.json \
--map ../../iCloud/fileout/root_maps/PA20L_plans.json/PA20L_root_map.csv \
--candidates ../../iCloud/fileout/root_maps/PA20L_root_candidates.json \
--log ../../iCloud/fileout/root_maps/PA20L_root_log.txt \
--no-debug

##########