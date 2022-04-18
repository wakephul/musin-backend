start:
	python scripts/network_output_clean.py && python3 main.py "$(notes)" && python scripts/network_output_merge.py
start-multiple-simulations:
	python scripts/network_output_clean.py && python3 main.py multiple_simulations && python scripts/network_output_merge.py
start-generate-spikes:
	python3 main.py generate_spikes && python scripts/network_output_merge.py
start-create-spikes-table:
	python3 main.py create_spikes_table
start-create-support-table:
	python3 main.py create_support_table