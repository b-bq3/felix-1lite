"""Quick demo training: 200 iters, ~5 min on CPU."""
import sys
sys.path.insert(0, '/home/clawdbot/.openclaw/workspace/felix-1lite')
import felix

felix.CONFIG["n_layer"] = 3
felix.CONFIG["n_embd"] = 144
felix.CONFIG["n_head"] = 4
felix.CONFIG["block_size"] = 96
felix.CONFIG["batch_size"] = 16
felix.CONFIG["max_iters"] = 200
felix.CONFIG["warmup_iters"] = 20
felix.CONFIG["eval_interval"] = 50
felix.CONFIG["learning_rate"] = 5e-4

print("=" * 50)
print("FELIX-1lite DEMO training (CPU, ~5 min)")
print("=" * 50)

felix.train(checkpoint_path="/home/clawdbot/.openclaw/workspace/felix-1lite/felix-demo.pt",
            data_path="/home/clawdbot/.openclaw/workspace/felix-1lite/felix_data.txt",
            verbose=True)