pip install huggingface_hub huggingface_hub["cli"]

# Pre-download Wan2.1-T2V-1.3B model
hf download Wan-AI/Wan2.1-T2V-1.3B --local-dir wan_models/Wan2.1-T2V-1.3B

# Pre-download Infinite-Forcing model
hf download SOTAMak1r/Infinite-Forcing --local-dir SOTAMak1r/Infinite-Forcing

# Pre-download causal forcing checkpoint
hf download zhuhz22/Causal-Forcing --local-dir zhuhz22/Causal-Forcing