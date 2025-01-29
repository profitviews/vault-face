from profitview import Link, http, logger, cron
import requests


class Signals(Link):
    """A ProfitView bot that copies trading strategies based on DeFiChain vault data."""

    exchange = "bitmex"  # Example exchange
    assets = [  # Liquid perps on BitMEX
        { "asset": "BTC", "perp": "XBTUSD" },
        { "asset": "ETH", "perp": "ETHUSD" },
        { "asset": "XRP", "perp": "XRPUSD" },
        { "asset": "SOL", "perp": "SOLUSD" },
		{ "asset": "SUI", "perp": "SUIUSD" },
		{ "asset": "DOGE", "perp": "DOGEUSDT" },
		{ "asset": "LTC", "perp": "LTCUSD" },
		{ "asset": "ADA", "perp": "ADAUSD" },
		{ "asset": "LINK", "perp": "LINKUSD" },
		{ "asset": "PEPE", "perp": "PEPEUSD" },
		{ "asset": "DOT", "perp": "DOTUSD" },
		{ "asset": "BNB", "perp": "BNBUSD" },
		{ "asset": "BCH", "perp": "BCHUSD" },
		{ "asset": "AVAX", "perp": "AVAXUSD" },
		{ "asset": "NEAR", "perp": "NEARUSD" },
		{ "asset": "WLD", "perp": "WLDUSD" },
		{ "asset": "APT", "perp": "APTUSD" },
		{ "asset": "FIL", "perp": "FILUSD" },
		{ "asset": "ARB", "perp": "ARBUSD" }
	]
    asset_to_perp = {asset['asset']: asset['perp'] for asset in assets}

    vaults_url = "https://ocean.defichain.com/v0/mainnet/loans/vaults"
    
    top_owner_number = 10
    
    active_vaults = []
    vaults_by_asset = {}
    vaults_by_owner = {}
    vaults_by_owner_collateral = []
    top_vaults_by_asset = {}
    weighted_collateral_for_asset = {}

    def on_start(self):
        self.get_active_vaults()
        self.process_vaults()

    def get_active_vaults(self):
        """Fetch and analyze active vaults with loans and collateral"""
        params = {"size": 100}  # Fetch 100 vaults per request
        all_vaults = []

        while True:
            response = requests.get(self.vaults_url, params=params)

			if response.status_code != 200:
				logger.info(f"Failed to fetch vault data: {response.status_code}, {response.text}")
				return None

			data = response.json()
			all_vaults.extend(data["data"])

			# Check if there are more vaults to fetch
			if "page" not in data or not data["page"].get("next"):
				break

			params["next"] = data["page"]["next"]

		logger.info(f"Total vaults: {len(all_vaults)}")
		
		# Filter active vaults with loans and collateral
		self.active_vaults = [
			vault for vault in all_vaults
			if float(vault.get("loanValue", 0)) > 0 and float(vault.get("collateralValue", 0)) > 0
		]
		
	def process_vaults(self):
		# Process vaults for all assets in the assets list
		for asset in self.assets:
			asset_symbol = asset['asset']
			asset_vaults = self.get_vaults_by_asset(asset_symbol, self.active_vaults)

			# Store the results in the dictionary
			self.vaults_by_asset[asset_symbol] = []

			for vault in asset_vaults:
				# Extract the specific collateral amount for this asset
				collateral_amount = next(
					(c['amount'] for c in vault['collateralAmounts'] 
					 if c['symbol'] == asset_symbol),
					'0.00000000'  # Default value if not found
				)

				# Create vault data structure
				vault_data = {
					'ownerAddress': vault['ownerAddress'],
					'vaultId': vault['vaultId'],
					'collateralValue': float(vault['collateralValue']),
					'collateralAmount': collateral_amount,
					'symbols': [c['symbol'] for c in vault['collateralAmounts']]
				}

				# Add to the asset's vault list
				self.vaults_by_asset[asset_symbol].append(vault_data)

				# Update owner's total collateral
				owner = vault['ownerAddress']
				if owner not in self.vaults_by_owner:
					self.vaults_by_owner[owner] = {
						'totalCollateralValue': float(vault['collateralValue']),  # Initialize with this vault's value
						'vaults': [vault_data]
					}
				else:
					# Only add the vault data, don't add to total collateral value
					# since it's already the total value for the vault
					self.vaults_by_owner[owner]['vaults'].append(vault_data)

		# Sort owners by total collateral value in descending order
		self.vaults_by_owner_collateral = sorted(
			self.vaults_by_owner.items(),
			key=lambda x: x[1]['totalCollateralValue'],
			reverse=True
		)
		
		top_owners = self.vaults_by_owner_collateral[:self.top_owner_number]

		# Create a set to store unique vault IDs from top owners
		top_vaults = set()

		# Iterate through top owners and collect their vaults
		for owner, vault_info in top_owners:
			for vault in vault_info['vaults']:
				top_vaults.add(vault['vaultId'])

		# Iterate through top owners and organize vaults by collateral asset
		for owner, vault_info in top_owners:
			for vault in vault_info['vaults']:
				for symbol in vault['symbols']:
					if symbol not in self.top_vaults_by_asset:
						self.top_vaults_by_asset[symbol] = set()
					self.top_vaults_by_asset[symbol].add(vault['vaultId'])
		
	def get_vaults_by_asset(self, asset_symbol, vaults):
		return sorted(
			[vault for vault in vaults if any(c['symbol'] == asset_symbol for c in vault.get('collateralAmounts', []))],
			key=lambda x: float(x['collateralValue']),
			reverse=True
		)

	def get_current_vault_details(self, vault_id):
        url = f"{self.vaults_url}/{vault_id}"
		response = requests.get(url)
		return response.json()['data']

	def get_weighted_collateral(self):
		self.weighted_collateral_for_asset = {}
		for asset, vault_ids in self.top_vaults_by_asset.items():
			total_collateral_for_asset = 0
			total_collateral_for_asset_ratio = 0
			for vault_id in vault_ids:
				vault_details = self.get_current_vault_details(vault_id)
				collateral_ratio = float(vault_details['collateralRatio'])
				total_collateral = float(vault_details['collateralValue'])
				total_collateral_for_asset += total_collateral
				total_collateral_for_asset_ratio += collateral_ratio*total_collateral
			self.weighted_collateral_for_asset[asset] = total_collateral_for_asset_ratio/total_collateral_for_asset
	
	@cron.run(every=60)
    def fetch_vault_data(self):
        """Fetches vault data from the DeFiChain API."""
		self.get_weighted_collateral()
		for asset, collateral_ratio in self.weighted_collateral_for_asset.items():
			if asset in self.asset_to_perp:
				self.decide_signal(self.exchange, asset, collateral_ratio)

    def decide_signal(self, src, asset, collateral_ratio):
        """Makes trading decisions based on the collateral ratio."""
        if collateral_ratio < 150:  # Risk of liquidation
            size = -1.0  # Go fully short
        elif collateral_ratio > 200:  # Vault is safe
            size = 1.0  # Go fully long
        else:
            size = 0  # Neutral position
		
		logger.info(f"signal: Exchange {self.exchange}, Asset: {asset}, Contract: {self.asset_to_perp[asset]}, size: {size}")
        self.signal(self.exchange, self.asset_to_perp[asset], size=size)	
