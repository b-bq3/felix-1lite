"""Full FELIX training: 1500 iters on CPU for better quality."""
import sys
sys.path.insert(0, '/home/clawdbot/.openclaw/workspace/felix-1lite')
import felix

felix.CONFIG["n_layer"] = 4
felix.CONFIG["n_embd"] = 192
felix.CONFIG["n_head"] = 6
felix.CONFIG["block_size"] = 128
felix.CONFIG["batch_size"] = 16
felix.CONFIG["max_iters"] = 1500
felix.CONFIG["warmup_iters"] = 100
felix.CONFIG["eval_interval"] = 100
felix.CONFIG["learning_rate"] = 4e-4

print("=" * 50)
print("FELIX-1lite FULL training (1500 iters, CPU)")
print("=" * 50)

felix.train(checkpoint_path="/home/clawdbot/.openclaw/workspace/felix-1lite/felix-full.pt",
            data_path="/home/clawdbot/.openclaw/workspace/felix-1lite/felix_data.txt",
            verbose=True)