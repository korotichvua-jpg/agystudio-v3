import numpy as np

class FloatingHeatmapEngine:
    """
    Component 1: Classical Floating Heatmap Engine
    Generates theoretical liquidation clusters based on current price, total OI, and leverage tiers.
    """
    def __init__(self):
        # Define the three leverage tiers based on the specification
        self.tiers = {
            'high': {'leverage': 20, 'm_maint': 0.025, 'weight': 0.45},
            'med':  {'leverage': 10, 'm_maint': 0.050, 'weight': 0.35},
            'low':  {'leverage': 3,  'm_maint': 0.150, 'weight': 0.20}
        }
        # Dispersion parameters for intra-tier entry price simulation
        self.multipliers = np.array([0.60, 0.85, 1.00, 1.25, 1.60])
        self.density_weights = np.array([0.50, 0.80, 1.00, 0.70, 0.40])

    def get_liquidation_distance(self, leverage: float, m_maint: float) -> float:
        """Calculate the percentage distance to liquidation."""
        return max(0.005, (1.0 / leverage) - m_maint)

    def generate_clusters(self, current_price: float, total_oi_notional: float):
        """
        Distributes Open Interest across tiers and sub-clusters.
        Returns a dictionary of 'long' and 'short' liquidation clusters.
        """
        clusters = {'long': [], 'short': []}
        
        for tier_name, tier in self.tiers.items():
            dist = self.get_liquidation_distance(tier['leverage'], tier['m_maint'])
            v_t = total_oi_notional * tier['weight']
            
            # Vectorized cluster price and intensity generation
            p_short = current_price * (1 + dist * self.multipliers)
            p_long = current_price * (1 - dist * self.multipliers)
            intensities = v_t * self.density_weights
            
            for i in range(len(self.multipliers)):
                clusters['short'].append({
                    'price': p_short[i], 
                    'intensity': intensities[i], 
                    'tier': tier_name
                })
                clusters['long'].append({
                    'price': p_long[i], 
                    'intensity': intensities[i], 
                    'tier': tier_name
                })
                
        return clusters


class AnchoredSurvivorshipEngine:
    """
    Component 2: Historical ΔOI Position Anchoring & Survivorship Engine
    Vectorized NumPy pipeline that anchors liquidation levels to historical candles and 
    eliminates positions pierced by subsequent market wicks.
    """
    def __init__(self, decay_lambda: float = 0.0035):
        self.decay_lambda = decay_lambda

    def process_candles(self, open_p: np.ndarray, high_p: np.ndarray, low_p: np.ndarray, 
                        close_p: np.ndarray, volume: np.ndarray, current_price: float, 
                        delta_dist_long: float, delta_dist_short: float):
        """
        Executes the historical survivorship analysis across N candles using SIMD operations.
        Input arrays should be chronologically ordered (index 0 is oldest, N-1 is newest).
        """
        N = len(close_p)
        
        # 4.1 Candle Volume & Entry Proxy
        p_entry = (open_p + high_p + low_p + 2 * close_p) / 5.0
        notional = volume * close_p
        
        # 4.2 Directional Order Flow Bias
        range_max = np.maximum(high_p - low_p, 1e-5)
        beta = np.clip((close_p - open_p) / range_max, -0.85, 0.85)
        
        b_long = 0.50 + 0.35 * beta
        b_short = 0.50 - 0.35 * beta
        
        # 4.3 Recency Exponential Decay
        # candle age: oldest candle is N-1 (index 0), newest is 0 (index N-1)
        age = (N - 1) - np.arange(N)
        decay = np.exp(-self.decay_lambda * age)
        notional_eff = notional * decay
        
        # 4.4 Cumulative Forward Wick Penetration & Elimination
        p_liq_long = p_entry * (1 - delta_dist_long)
        p_liq_short = p_entry * (1 + delta_dist_short)
        
        # Fast suffix min/max using accumulated backwards rolling
        suffix_min_low = np.minimum.accumulate(low_p[::-1])[::-1]
        suffix_max_high = np.maximum.accumulate(high_p[::-1])[::-1]
        
        # Elimination Masks
        eliminated_long = (suffix_min_low <= p_liq_long) | (current_price <= p_liq_long)
        eliminated_short = (suffix_max_high >= p_liq_short) | (current_price >= p_liq_short)
        
        survived_long_mask = ~eliminated_long
        survived_short_mask = ~eliminated_short
        
        surviving_notional_long = notional_eff * b_long * survived_long_mask
        surviving_notional_short = notional_eff * b_short * survived_short_mask
        
        # Survivor Rates
        total_notional_long = np.sum(notional_eff * b_long)
        total_notional_short = np.sum(notional_eff * b_short)
        
        s_rate_long = np.sum(surviving_notional_long) / total_notional_long if total_notional_long > 0 else 0.0
        s_rate_short = np.sum(surviving_notional_short) / total_notional_short if total_notional_short > 0 else 0.0
        
        return {
            'survived_long_notional': surviving_notional_long,
            'survived_short_notional': surviving_notional_short,
            's_rate_long': s_rate_long,
            's_rate_short': s_rate_short,
            'p_liq_long': p_liq_long[survived_long_mask],
            'p_liq_short': p_liq_short[survived_short_mask]
        }

if __name__ == "__main__":
    # Quick sanity test of the math
    print("--- Testing Floating Heatmap ---")
    engine1 = FloatingHeatmapEngine()
    clusters = engine1.generate_clusters(current_price=60000.0, total_oi_notional=100_000_000.0)
    print(f"Generated {len(clusters['long'])} Long Clusters and {len(clusters['short'])} Short Clusters")
    print(f"Top High-Tier Long Cluster Price: {clusters['long'][2]['price']:.2f}")

    print("\n--- Testing Survivorship Engine ---")
    engine2 = AnchoredSurvivorshipEngine()
    # Mocking 5 candles
    open_p = np.array([58000, 59000, 60000, 59500, 60500])
    high_p = np.array([59500, 60500, 61000, 60000, 61000])
    low_p =  np.array([57500, 58500, 59000, 59000, 60000])
    close_p= np.array([59000, 60000, 59500, 59500, 60800])
    vol =    np.array([100,   150,   120,   80,    200])
    
    res = engine2.process_candles(open_p, high_p, low_p, close_p, vol, current_price=60800.0, 
                                  delta_dist_long=0.05, delta_dist_short=0.05)
    print(f"Long Survivorship Rate:  {res['s_rate_long'] * 100:.1f}%")
    print(f"Short Survivorship Rate: {res['s_rate_short'] * 100:.1f}%")
