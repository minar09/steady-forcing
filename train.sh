#!/bin/bash

#!/bin/bash
rm -f /dev/shm/nccl-* 2>/dev/null || true
mount -o remount,size=32G /dev/shm 2>/dev/null || true

export NCCL_SHM_DISABLE=1
export NCCL_DEBUG=WARN
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

torchrun \
  --nnodes=1 \
  --nproc_per_node=8 \
  --rdzv_endpoint=$MASTER_PORT \
  --rdzv_id=5235 \
  --rdzv_backend=c10d  \
  train.py \
  --config_path configs/steady_forcing_train.yaml \
  --logdir ./checkpoints/steady_forcing_additional \
  --disable-wandb