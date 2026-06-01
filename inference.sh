python inference.py \
    --config_path configs/self_forcing_dmd.yaml \
    --checkpoint_path ./ckpt/Steady-Forcing-T2V-1.3B/steady_forcing_t2v.pt \
    --output_folder videos/steady_forcing/t2v \
    --data_path prompts/static.txt \
    --num_output_frames 300 \
    --use_ema 
