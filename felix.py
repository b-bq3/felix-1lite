import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import math
import os
import json
import re
from collections import Counter
CONFIG = {
    "name": "felix-1lite",
    "vocab_size": 0,
    "block_size": 256,
    "n_layer": 6,
    "n_head": 8,
    "n_embd": 384,
    "dropout": 0.1,
    "batch_size": 32,
    "learning_rate": 3e-4,
    "max_iters": 3000,
    "warmup_iters": 200,
    "eval_interval": 300,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
}
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"
BOS_TOKEN = "<BOS>"
EOS_TOKEN = "<EOS>"
USR_TOKEN = "<USER>"
FELIX_TOKEN = "<FELIX>"
SEP_TOKEN = "<SEP>"
SPECIAL_TOKENS = [PAD_TOKEN, UNK_TOKEN, BOS_TOKEN, EOS_TOKEN, USR_TOKEN, FELIX_TOKEN, SEP_TOKEN]
class ArabicTokenizer:
    def __init__(self):
        self.token_to_id = {}
        self.id_to_token = {}
    @staticmethod
    def _normalize(text):
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
        text = text.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
        text = text.replace('ى', 'ي').replace('ؤ', 'و').replace('ئ', 'ي')
        text = text.replace('ة', 'ه')
        return text
    def fit(self, texts, min_freq=2, max_vocab=20000):
        counter = Counter()
        for text in texts:
            text = self._normalize(text)
            tokens = text.split()
            counter.update(tokens)
        self.token_to_id = {tok: i for i, tok in enumerate(SPECIAL_TOKENS)}
        for tok, freq in counter.most_common(max_vocab - len(SPECIAL_TOKENS)):
            if freq >= min_freq:
                self.token_to_id[tok] = len(self.token_to_id)
        self.id_to_token = {i: t for t, i in self.token_to_id.items()}
        return len(self.token_to_id)
    def encode(self, text):
        text = self._normalize(text)
        tokens = text.split()
        unk_id = self.token_to_id[UNK_TOKEN]
        return [self.token_to_id.get(t, unk_id) for t in tokens]
    def decode(self, ids):
        tokens = [self.id_to_token.get(i, UNK_TOKEN) for i in ids]
        clean = [t for t in tokens if t not in SPECIAL_TOKENS or t == ""]
        return " ".join(clean)
    def vocab_size(self):
        return len(self.token_to_id)
class CausalSelfAttention(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        assert n_embd % n_head == 0
        self.n_head = n_head
        self.head_dim = n_embd // n_head
        self.qkv = nn.Linear(n_embd, 3 * n_embd, bias=False)
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer('mask', torch.tril(torch.ones(block_size, block_size)))
    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x).reshape(B, T, 3, self.n_head, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        att = (q @ k.transpose(-2, -1)) * (self.head_dim ** -0.5)
        att = att.masked_fill(self.mask[:T, :T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.dropout(att)
        out = (att @ v).transpose(1, 2).reshape(B, T, C)
        return self.proj(out)
class MLP(nn.Module):
    def __init__(self, n_embd, dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )
    def forward(self, x):
        return self.net(x)
class Block(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        self.ln1 = nn.LayerNorm(n_embd)
        self.attn = CausalSelfAttention(n_embd, n_head, block_size, dropout)
        self.ln2 = nn.LayerNorm(n_embd)
        self.mlp = MLP(n_embd, dropout)
    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x
class FELIX(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.token_emb = nn.Embedding(config["vocab_size"], config["n_embd"])
        self.pos_emb = nn.Embedding(config["block_size"], config["n_embd"])
        self.blocks = nn.ModuleList([
            Block(config["n_embd"], config["n_head"], config["block_size"], config["dropout"])
            for _ in range(config["n_layer"])
        ])
        self.ln_f = nn.LayerNorm(config["n_embd"])
        self.head = nn.Linear(config["n_embd"], config["vocab_size"], bias=False)
        self.head.weight = self.token_emb.weight
        self.apply(self._init_weights)
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok = self.token_emb(idx)
        pos = self.pos_emb(torch.arange(T, device=idx.device))
        x = tok + pos
        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)
        logits = self.head(x)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
                ignore_index=-100,
            )
        return logits, loss
    @torch.no_grad()
    def generate(self, idx, max_new_tokens=200, temperature=0.8, top_k=50, top_p=0.9):
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.config["block_size"]:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            if top_k is not None:
                v, _ = torch.topk(logits, top_k)
                logits[logits < v[:, [-1]]] = -float('inf')
            probs = F.softmax(logits, dim=-1)
            if top_p is not None:
                sorted_probs, sorted_idx = torch.sort(probs, descending=True)
                cum = torch.cumsum(sorted_probs, dim=-1)
                mask = cum > top_p
                mask[..., 1:] = mask[..., :-1].clone()
                mask[..., 0] = False
                sorted_probs[mask] = 0
                probs = sorted_probs.scatter(1, sorted_idx, sorted_probs)
                probs = probs / probs.sum(dim=-1, keepdim=True).clamp(min=1e-9)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx
class TextDataset(Dataset):
    def __init__(self, ids, block_size):
        self.ids = ids
        self.block_size = block_size
    def __len__(self):
        return len(self.ids) - self.block_size - 1
    def __getitem__(self, i):
        x = torch.tensor(self.ids[i:i+self.block_size], dtype=torch.long)
        y = torch.tensor(self.ids[i+1:i+1+self.block_size], dtype=torch.long)
        return x, y
def load_data(path="felix_data.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
def train(checkpoint_path="felix-1lite.pt", data_path="felix_data.txt", verbose=True):
    text = load_data(data_path)
    if verbose:
        print(f"Loaded {len(text):,} chars of Arabic text")
    tokenizer = ArabicTokenizer()
    lines = [l for l in text.split("\n") if l.strip()]
    vocab_n = tokenizer.fit(lines, min_freq=1, max_vocab=12000)
    if verbose:
        print(f"Vocab size: {vocab_n:,}")
    CONFIG["vocab_size"] = vocab_n
    data_ids = tokenizer.encode(text)
    if verbose:
        print(f"Encoded into {len(data_ids):,} tokens")
    n = int(0.9 * len(data_ids))
    train_ids = data_ids[:n]
    val_ids = data_ids[n:]
    train_ds = TextDataset(train_ids, CONFIG["block_size"])
    val_ds = TextDataset(val_ids, CONFIG["block_size"])
    train_dl = DataLoader(train_ds, batch_size=CONFIG["batch_size"], shuffle=True, drop_last=True)
    val_dl = DataLoader(val_ds, batch_size=CONFIG["batch_size"], shuffle=False, drop_last=True)
    model = FELIX(CONFIG).to(CONFIG["device"])
    n_params = sum(p.numel() for p in model.parameters())
    if verbose:
        print(f"FELIX-1lite: {n_params/1e6:.1f}M parameters on {CONFIG['device']}")
    optimizer = torch.optim.AdamW(model.parameters(), lr=CONFIG["learning_rate"], betas=(0.9, 0.95))
    def get_lr(it):
        if it < CONFIG["warmup_iters"]:
            return CONFIG["learning_rate"] * it / CONFIG["warmup_iters"]
        if it > CONFIG["max_iters"]:
            return CONFIG["learning_rate"] * 0.1
        decay_ratio = (it - CONFIG["warmup_iters"]) / (CONFIG["max_iters"] - CONFIG["warmup_iters"])
        return CONFIG["learning_rate"] * (0.1 + 0.9 * (0.5 * (1.0 + math.cos(math.pi * decay_ratio))))
    @torch.no_grad()
    def estimate_loss():
        model.eval()
        out = {}
        for name, dl in [("train", train_dl), ("val", val_dl)]:
            losses = []
            for x, y in dl:
                x, y = x.to(CONFIG["device"]), y.to(CONFIG["device"])
                _, loss = model(x, y)
                losses.append(loss.item())
            out[name] = sum(losses) / len(losses)
        model.train()
        return out
    best_val = float('inf')
    for it in range(CONFIG["max_iters"]):
        lr = get_lr(it)
        for pg in optimizer.param_groups:
            pg["lr"] = lr
        if it % CONFIG["eval_interval"] == 0:
            losses = estimate_loss()
            if verbose:
                print(f"step {it:5d} | lr {lr:.2e} | train {losses['train']:.4f} | val {losses['val']:.4f}")
            if losses["val"] < best_val:
                best_val = losses["val"]
                torch.save({
                    "model": model.state_dict(),
                    "config": CONFIG,
                    "tokenizer": {
                        "token_to_id": tokenizer.token_to_id,
                        "id_to_token": tokenizer.id_to_token,
                    },
                }, checkpoint_path)
                if verbose:
                    print(f"  → saved (val {best_val:.4f})")
        x, y = next(iter(train_dl))
        x, y = x.to(CONFIG["device"]), y.to(CONFIG["device"])
        _, loss = model(x, y)
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
    torch.save({
        "model": model.state_dict(),
        "config": CONFIG,
        "tokenizer": {
            "token_to_id": tokenizer.token_to_id,
            "id_to_token": tokenizer.id_to_token,
        },
    }, checkpoint_path)
    if verbose:
        print(f"Training complete. Saved to {checkpoint_path}")
    return model, tokenizer
def chat(prompt, checkpoint="felix-1lite.pt", max_tokens=200, temperature=0.8):
    ckpt = torch.load(checkpoint, map_location=CONFIG["device"])
    cfg = ckpt["config"]
    cfg["device"] = CONFIG["device"]
    tokenizer = ArabicTokenizer()
    tokenizer.token_to_id = ckpt["tokenizer"]["token_to_id"]
    tokenizer.id_to_token = ckpt["tokenizer"]["id_to_token"]
    model = FELIX(cfg).to(CONFIG["device"])
    model.load_state_dict(ckpt["model"])
    model.eval()
    full_prompt = f"{USR_TOKEN} {prompt} {SEP_TOKEN} {FELIX_TOKEN} "
    ids = tokenizer.encode(full_prompt)
    idx = torch.tensor([ids], dtype=torch.long).to(CONFIG["device"])
    out = model.generate(idx, max_new_tokens=max_tokens, temperature=temperature, top_k=50, top_p=0.9)
    text = tokenizer.decode(out[0].tolist())
    if SEP_TOKEN in text:
        text = text.split(SEP_TOKEN)[0]
    return text
def interactive():
    print("=" * 50)
    print("FELIX-1lite — Interactive Chat")
    print("Type 'quit' to exit")
    print("=" * 50)
    while True:
        try:
            user_input = input("\n> ")
            if user_input.strip().lower() in ("quit", "exit", "خروج"):
                break
            response = chat(user_input)
            print(f"\nFELIX: {response}")
        except KeyboardInterrupt:
            break
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "chat":
        prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "مرحبا"
        print(chat(prompt))
    elif len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive()
    else:
        train()
