start:
	python3 scripts/network_output_clean.py && python3 main.py "$(notes)"
start-multiple-simulations:
	python3 scripts/network_output_clean.py && python3 main.py multiple_simulations && python scripts/network_output_merge.py
merge-outputs:
	python3 scripts/network_output_merge.py "$(folder_id)" "$(cortex_id)"
start-create-spikes-table:
	python3 main.py create_spikes_table
start-create-support-table:
	python3 main.py create_support_table

start-webapp:
	flask --app webapp --debug run