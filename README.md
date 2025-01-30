# How I Used DeepSeek to Build a Profitable DeFi Trading Algorithm in One Morning

AI-driven trading algorithms are revolutionizing DeFi, and DeepSeek just helped me build one **in a single morning**. In this post, I'll show you how I leveraged DeepSeek's coding power to streamline DeFi trading, automate vault selection, and deploy it to [ProfitView](https://profitview.net) for real-world execution.

## Background: Why I Wanted a DeFi Trading Algorithm  

Previously, I demonstrated [how easy it is to build a news trading algorithm](https://profitview.net/blog/what-i-learned-when-building-an-ai-news-trading-bot) using ProfitView's [**Python-based IDE**](https://profitview.net/docs/trading/).  

This time, I wanted to create something more practical and actionable. **Vaults** caught my attention when a senior member of BitMEX's sales team introduced them to me last week. After some research, I found **DeFiChain’s implementation**, which operates on a simple principle:

1. **Users deposit collateral** into a vault.
2. **Vaults generate loans** at an interest rate.
3. **Users can borrow against** their vault balance.

The key **insight?** All this data is **publicly available** on the blockchain—perfect for algorithmic trading.

## How the DeFi Trading Algorithm Works  

I designed a simple **algorithmic strategy** based on vault data:

1. **Fetch** the list of active vaults with loans and collateral.
2. **Filter** only those with collateral that is tradable via **Perpetual Contracts (Perps)** on supported exchanges.
3. **Generate** a trading signal based on the **collateral ratio**.
4. **Execute** trades based on the signal.

👉 See the code [here](/src/VaultFollow.py) and the notebook I used to develop it [here](/src/vault-face.ipynb).

---

## Using DeepSeek to Supercharge DeFi Algorithm Development  

Like many developers, I’ve been hearing the buzz about **DeepSeek**, but I hadn’t seriously tested it yet. Since I use [Cursor](https://www.cursor.com/) for coding, I checked its model list and saw `deepSeek-v3` as an option.  

Until now, I had mainly used **Claude 3.5 Sonnet** and **GPT-4o**, both of which performed well for me. But I wanted to see if **DeepSeek** lived up to the hype.

At first glance: **impressive.** 🚀  

To be clear, **this isn’t a full review**, just my **first-hand experience** using DeepSeek for coding. 

---

## The Code Challenge: Fetching Vault Data  

I started with this simple script to retrieve **vault data**:

```python
vaults_url = "https://ocean.defichain.com/v0/mainnet/loans/vaults"

all_vaults = response.json()["data"]

# Filter active vaults with loans and collateral
active_vaults = [
    vault for vault in all_vaults
    if float(vault.get("loanValue", 0)) > 0 and float(vault.get("collateralValue", 0)) > 0
]
```

But something was off. The API only returned two vaults—with a total of about $100 in collateral. 🤔

Had DeFiChain fallen out of favor? Or was the bull run reducing the need for borrowing?

Before abandoning this dataset, I decided to quickly test DeepSeek. I highlighted the code in Cursor, hit Ctrl-K, and asked:

"Improve this code."

To my surprise, DeepSeek immediately started a major rewrite. I was skeptical. I thought "this thing's going crazy" - but didn't even read the code. I was in too much of a hurry preparing for a meeting. It was in a Jupyter notebook so I just hit Shift-Enter to run it. It started running... and running. I was tempted to kill it and classify DeepSeek as a fail. I just went on with my work on another screen and forgot about it.

Ten minutes later, I needed to test something else in Jupyter so I went back to the code. It had finished. And... WTF? 🤯

| Total vaults: 11,372  
| Active vaults with loans and collateral: 402  

The problem? I had forgotten to handle pagination. Most REST APIs limit the number of results per request, so pagination is required to fetch the full dataset.

DeepSeek not only optimized my code but also caught an issue I didn’t realize existed. This is exactly the kind of AI-powered assistance that accelerates algorithmic trading development.

## The Fix: DeepSeek’s Optimized Code

Here’s what DeepSeek generated:

```python
vaults_url = "https://ocean.defichain.com/v0/mainnet/loans/vaults"
params, all_vaults = {"size": 100}, []

while True:
    response = requests.get(vaults_url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch vault data: {response.status_code}, {response.text}")
        return None
        
    data = response.json()
    all_vaults.extend(data["data"])
    if "page" not in data or not data["page"].get("next"): break
    params["next"] = data["page"]["next"]

active_vaults = [vault for vault in all_vaults 
                if float(vault.get("loanValue", 0)) > 0 and float(vault.get("collateralValue", 0)) > 0]
```

## Deploying the DeFi Algorithm with ProfitView

With the data issue fixed, I deployed the algorithm to ProfitView, using its Python IDE to integrate it with our high-performance trading infrastructure.

For the first iteration, I kept things simple:

- Rank vault owners by total collateral deployed
- Select the top 10 as potential smart-money traders
- Execute trades based on the collateral ratio signal

Right now, the only supported assets (i.e., available as collateral in **DeFiChain vaults** and tradable via **Perps** on **BitMEX**) are **BTC** and **ETH**.

## See the Algorithm in Action 🚀

👉 If you're in the BitMEX Bot Creator Beta program, check out the live bots:

* [BTC Bot](https://www.bitmex.com/app/trade/XBTUSD?botId=58a12c25-5f3c-4908-bd4f-eb3f0ccdcad5&action=share)
* [ETH Bot](https://www.bitmex.com/app/trade/ETHUSD?botId=3023d6ed-f9bf-4b6a-a664-699ae85cfb0a&action=share)

Want access?
📩 Contact BitMEX at [support@bitmex.com](mailto:support@bitmex.com) to join the beta.

## Final Thoughts

This experience showed me that AI-powered coding assistants like DeepSeek can drastically improve algorithm development—not just by fixing errors but by proactively improving code in unexpected ways.

If you're building DeFi trading algorithms, I highly recommend testing DeepSeek for yourself.

🔔 Follow me for more insights on AI-powered trading and algorithm development! 🚀

