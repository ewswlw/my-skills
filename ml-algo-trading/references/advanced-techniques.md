# Advanced Techniques for Algorithmic Trading

## Deep Learning Architectures

### When Deep Learning Makes Sense

| Condition | DL Viable? | Why |
|-----------|-----------|-----|
| N > 10,000 observations | Yes | Enough data to learn representations |
| N = 2,000-10,000 | Maybe | Shallow architectures only (1-2 layers, <50 units) |
| N < 2,000 | No | Insufficient data; use gradient boosting |
| Sequential patterns suspected | Yes | RNN/LSTM excel at temporal dependencies |
| Image/grid features available | Yes | CNN for pattern recognition |
| Multi-asset cross-attention needed | Yes | Transformer architecture |
| Tabular features only | Usually no | GBM typically wins on pure tabular |

### Recurrent Neural Networks (RNN / LSTM / GRU)

Best for sequential/temporal patterns in price or feature time series.

```python
import torch
import torch.nn as nn

class TradingLSTM(nn.Module):
    """
    LSTM for binary signal generation.
    Input: (batch, sequence_length, n_features)
    Output: P(next_period_return > 0)
    """
    def __init__(self, n_features: int, hidden_size: int = 20,
                 n_layers: int = 1, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_size,
            num_layers=n_layers,
            batch_first=True,
            dropout=dropout if n_layers > 1 else 0,
        )
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        # x shape: (batch, seq_len, features)
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]  # Take last timestep
        return self.sigmoid(self.fc(last_hidden))

# Hyperparameters by data size
# N = 5,000-10,000:  hidden=10-20, layers=1, seq_len=13-26
# N = 10,000-50,000: hidden=20-64, layers=1-2, seq_len=26-52
# N > 50,000:        hidden=64-128, layers=2-3, seq_len=52-104
```

### Data Preparation for RNN

```python
import numpy as np

def create_sequences(features: np.ndarray, labels: np.ndarray, 
                     seq_length: int = 26) -> tuple:
    """
    Convert flat feature matrix to sequences for RNN input.
    
    Args:
        features: (N, n_features) array
        labels: (N,) array
        seq_length: Lookback window (e.g., 26 weeks ≈ 6 months)
    
    Returns:
        X: (N - seq_length, seq_length, n_features)
        y: (N - seq_length,)
    """
    X, y = [], []
    for i in range(seq_length, len(features)):
        X.append(features[i - seq_length:i])
        y.append(labels[i])
    return np.array(X), np.array(y)

# Normalization: use expanding window (point-in-time safe)
from sklearn.preprocessing import StandardScaler

def expanding_normalize(df, feature_cols, min_periods=52):
    """Normalize features using expanding window (no look-ahead)."""
    result = pd.DataFrame(index=df.index, columns=feature_cols)
    for i in range(min_periods, len(df)):
        window = df[feature_cols].iloc[:i]
        mean = window.mean()
        std = window.std()
        std[std == 0] = 1  # Avoid division by zero
        result.iloc[i] = (df[feature_cols].iloc[i] - mean) / std
    return result.dropna()
```

### Training Best Practices for Financial DL

```python
# 1. Use MSE for regression, BCE for classification
criterion = nn.BCELoss()  # Binary classification

# 2. RMSProp or Adam (not SGD) for financial data
optimizer = torch.optim.RMSprop(model.parameters(), lr=0.001)

# 3. Early stopping on validation loss
class EarlyStopping:
    def __init__(self, patience=10, min_delta=1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
    
    def should_stop(self, val_loss):
        if self.best_loss is None or val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            return False
        self.counter += 1
        return self.counter >= self.patience

# 4. Dropout for regularization (0.2-0.5)
# 5. Batch size: 32-128 (smaller = more noise = regularization)
# 6. Max epochs: 100-200 with early stopping
```

### Convolutional Neural Networks (CNN)

Best for grid-like data representations (e.g., candlestick images, correlation matrices, multi-timeframe feature grids).

```python
class TradingCNN(nn.Module):
    """
    CNN for image-like trading features.
    Input: (batch, channels, height, width)
    Example: 20-day × 5 features → (batch, 1, 20, 5) "image"
    """
    def __init__(self, height=20, width=5):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((4, 2))
        self.fc = nn.Linear(32 * 4 * 2, 1)
        self.sigmoid = nn.Sigmoid()
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        return self.sigmoid(self.fc(x))
```

### Autoencoders (Nonlinear Dimensionality Reduction)

```python
class FeatureAutoencoder(nn.Module):
    """
    Learn compressed representation of features.
    Useful for: nonlinear PCA, anomaly detection, synthetic feature generation.
    """
    def __init__(self, n_features: int, latent_dim: int = 5):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(n_features, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, n_features),
        )
    
    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent
    
    def encode(self, x):
        return self.encoder(x)

# Train on reconstruction loss, then use encoder output as features
# latent features = autoencoder.encode(X)
# These capture nonlinear combinations of original features
```

---

## NLP for Financial Text

### Signal Sources

| Source | Signal Type | Frequency | Libraries |
|--------|-----------|-----------|-----------|
| SEC filings (10-K, 10-Q) | Fundamental sentiment | Quarterly | `sec-edgar-downloader` |
| Earnings call transcripts | Forward guidance | Quarterly | `earnings-call-api` |
| News articles | Event-driven | Real-time | `newsapi`, `gdelt` |
| Social media (Twitter/Reddit) | Retail sentiment | Real-time | Platform APIs |
| Analyst reports | Consensus shifts | Weekly | Bloomberg, Refinitiv |

### Sentiment Analysis Approaches

```python
# Approach 1: Dictionary-based (Loughran-McDonald financial dictionary)
# Fast, interpretable, no training needed
from collections import Counter

def lm_sentiment(text: str, positive_words: set, negative_words: set) -> dict:
    """Loughran-McDonald financial sentiment score."""
    words = text.lower().split()
    n_pos = sum(1 for w in words if w in positive_words)
    n_neg = sum(1 for w in words if w in negative_words)
    total = len(words)
    return {
        'positive_pct': n_pos / total if total > 0 else 0,
        'negative_pct': n_neg / total if total > 0 else 0,
        'net_sentiment': (n_pos - n_neg) / total if total > 0 else 0,
    }

# Approach 2: Pre-trained transformer (FinBERT)
# More accurate but slower, requires GPU for scale
from transformers import pipeline

finbert = pipeline("sentiment-analysis", model="ProsusAI/finbert")
result = finbert("The company reported strong earnings growth of 15%")
# Returns: [{'label': 'positive', 'score': 0.95}]

# Approach 3: Topic modeling (LDA) for thematic analysis
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(max_features=5000, stop_words='english')
doc_term = vectorizer.fit_transform(documents)
lda = LatentDirichletAllocation(n_components=10, random_state=42)
topics = lda.fit_transform(doc_term)
# Each document now has a 10-dimensional topic distribution → use as features
```

### Word Embeddings for Finance

```python
# Word2Vec trained on financial corpus
from gensim.models import Word2Vec

# Train on financial text corpus
model = Word2Vec(sentences, vector_size=100, window=5, min_count=5)

# Document embedding (average of word vectors)
def doc2vec_simple(text: str, model) -> np.ndarray:
    words = text.lower().split()
    vectors = [model.wv[w] for w in words if w in model.wv]
    return np.mean(vectors, axis=0) if vectors else np.zeros(model.vector_size)

# Use document vectors as features in trading model
```

---

## Reinforcement Learning for Trading

### Concept

Model trading as a Markov Decision Process (MDP):
- **State**: Market features + current position
- **Action**: Buy, sell, hold (or position size)
- **Reward**: Portfolio return (or risk-adjusted return)
- **Environment**: Historical market simulator

### Simple Q-Learning Agent

```python
class TradingEnvironment:
    """
    Simple trading environment for RL agent.
    """
    def __init__(self, features: np.ndarray, returns: np.ndarray):
        self.features = features
        self.returns = returns
        self.n_steps = len(features)
        self.current_step = 0
        self.position = 0  # 0 = cash, 1 = invested
    
    def reset(self):
        self.current_step = 0
        self.position = 0
        return self._get_state()
    
    def _get_state(self):
        return np.append(self.features[self.current_step], self.position)
    
    def step(self, action):
        """action: 0 = cash, 1 = invest"""
        reward = self.returns[self.current_step] * action
        self.position = action
        self.current_step += 1
        done = self.current_step >= self.n_steps - 1
        return self._get_state(), reward, done

# Libraries for more sophisticated RL:
# - stable-baselines3 (PPO, A2C, SAC)
# - FinRL (finance-specific RL framework)
# - gym-anytrading (OpenAI Gym environments for trading)
```

### When to Use RL

| Scenario | RL Appropriate? | Why |
|----------|----------------|-----|
| Portfolio rebalancing across N assets | Yes | Natural sequential decision problem |
| Single-asset binary long/cash | Probably not | Simpler supervised learning works |
| Market making | Yes | Bid-ask optimization is a classic RL problem |
| Dynamic position sizing | Yes | State-dependent sizing benefits from RL |
| Strategy with path-dependent objectives | Yes | RL naturally handles sequential rewards |

**Caution:** RL requires massive amounts of data (N > 50,000) and is extremely prone to overfitting in financial applications. Always compare against a supervised learning baseline.

---

## Regime Detection — Full Guide

### Threshold-Based Regimes

```python
def threshold_regime(df: pd.DataFrame) -> pd.Series:
    """
    Simple threshold-based regime detection.
    Returns: 0 = risk-on, 1 = neutral, 2 = risk-off
    """
    vix_percentile = df['vix'].expanding().rank(pct=True)
    vol_zscore = (df['realized_vol'] - df['realized_vol'].expanding().mean()) / \
                  df['realized_vol'].expanding().std()
    
    regime = pd.Series(1, index=df.index)  # Default: neutral
    regime[vix_percentile < 0.30] = 0       # Low VIX → risk-on
    regime[vix_percentile > 0.80] = 2       # High VIX → risk-off
    regime[vol_zscore > 2.0] = 2            # Vol spike → risk-off
    
    return regime
```

### Hidden Markov Model (HMM)

```python
from hmmlearn.hmm import GaussianHMM

def fit_hmm_regimes(
    returns: pd.Series,
    n_regimes: int = 2,
    n_iter: int = 100,
) -> pd.DataFrame:
    """
    Fit HMM to identify bull/bear (or bull/neutral/bear) regimes.
    
    Returns:
        DataFrame with regime labels and probabilities
    """
    # Prepare features: returns + volatility
    features = pd.DataFrame({
        'return': returns,
        'vol': returns.rolling(20).std(),
    }).dropna()
    
    X = features.values
    
    model = GaussianHMM(
        n_components=n_regimes,
        covariance_type='full',
        n_iter=n_iter,
        random_state=42,
    )
    model.fit(X)
    
    hidden_states = model.predict(X)
    state_probs = model.predict_proba(X)
    
    result = pd.DataFrame(index=features.index)
    result['regime'] = hidden_states
    for i in range(n_regimes):
        result[f'prob_regime_{i}'] = state_probs[:, i]
    
    # Label regimes by mean return (highest mean = bull)
    regime_means = {s: returns.loc[features.index][hidden_states == s].mean()
                    for s in range(n_regimes)}
    sorted_regimes = sorted(regime_means, key=regime_means.get)
    label_map = {sorted_regimes[i]: i for i in range(n_regimes)}
    result['regime_ordered'] = result['regime'].map(label_map)
    # 0 = bear (lowest return), highest = bull
    
    return result
```

### Using Regimes in Strategy

```python
# Option 1: Regime as a feature
df['regime'] = detect_regime(df)
X['regime'] = df['regime']  # Add to feature matrix

# Option 2: Regime as a filter (only trade in favorable regimes)
signals = model.predict(X)
signals[df['regime'] == 2] = 0  # Go to cash in risk-off regime

# Option 3: Separate models per regime (most powerful, needs more data)
for regime in [0, 1, 2]:
    mask = df['regime'] == regime
    model_per_regime[regime].fit(X[mask], y[mask])

# At prediction time:
current_regime = df['regime'].iloc[-1]
prediction = model_per_regime[current_regime].predict(X_latest)
```

---

## Strategy Ensembles

### Voting Ensemble (Multiple Strategies)

```python
def voting_ensemble(
    strategy_signals: pd.DataFrame,
    weights: dict = None,
    threshold: float = 0.5,
) -> pd.Series:
    """
    Combine multiple strategy signals via weighted voting.
    
    Args:
        strategy_signals: DataFrame where each column is a strategy's binary signal
        weights: Dict of {strategy_name: weight}. Default = equal weight.
        threshold: Minimum weighted vote to generate a long signal
    
    Returns:
        Combined signal (0 or 1)
    """
    if weights is None:
        weights = {col: 1.0 / len(strategy_signals.columns)
                   for col in strategy_signals.columns}
    
    weighted_sum = sum(
        strategy_signals[col] * weights[col]
        for col in strategy_signals.columns
    )
    
    return (weighted_sum >= threshold).astype(int)

# Weight strategies by inverse variance (more stable → more weight)
def inverse_variance_weights(strategy_returns: pd.DataFrame) -> dict:
    variances = strategy_returns.var()
    inv_var = 1.0 / variances
    weights = inv_var / inv_var.sum()
    return weights.to_dict()
```

### Stacking Ensemble (Meta-Learner)

```python
def stacking_ensemble(
    base_predictions: pd.DataFrame,
    y: pd.Series,
    meta_model=None,
    n_splits: int = 5,
):
    """
    Train a meta-learner on base strategy predictions.
    CRITICAL: Use purged CV for the meta-learner to avoid leakage.
    """
    from sklearn.linear_model import LogisticRegression
    
    if meta_model is None:
        meta_model = LogisticRegression(C=0.1)
    
    # Generate OOS predictions from base models using purged CV
    # Then train meta-learner on those OOS predictions
    # This prevents the meta-learner from seeing inflated in-sample predictions
    
    return meta_model
```

### Hierarchical Risk Parity (HRP) for Strategy Allocation

Treat each strategy as an "asset" and use HRP to allocate capital:

```python
# Concept:
# 1. Compute correlation matrix of strategy returns
# 2. Cluster strategies by similarity (hierarchical clustering)
# 3. Allocate inversely proportional to cluster variance
# 4. Benefits: no matrix inversion (unlike Markowitz), handles correlated strategies

# Library: riskfolio-lib
# from riskfolio import HCPortfolio
# or implement manually using scipy.cluster.hierarchy
```

---

## Synthetic Data Generation

### Block Bootstrap for Confidence Intervals

```python
def block_bootstrap_ci(
    returns: pd.Series,
    strategy_func,
    n_bootstrap: int = 1000,
    block_length: int = None,
    confidence: float = 0.95,
) -> dict:
    """
    Compute confidence intervals for strategy metrics via block bootstrap.
    
    Args:
        returns: Original return series
        strategy_func: Function that takes returns → metric (e.g., Sharpe)
        n_bootstrap: Number of bootstrap samples
        block_length: Length of blocks (default: sqrt(N))
        confidence: Confidence level (e.g., 0.95 for 95% CI)
    """
    if block_length is None:
        block_length = max(1, int(np.sqrt(len(returns))))
    
    metrics = []
    n = len(returns)
    n_blocks = n // block_length + 1
    
    for _ in range(n_bootstrap):
        # Sample blocks with replacement
        block_starts = np.random.randint(0, n - block_length, size=n_blocks)
        bootstrap_returns = pd.concat([
            returns.iloc[start:start + block_length]
            for start in block_starts
        ]).iloc[:n]  # Trim to original length
        bootstrap_returns.index = returns.index  # Preserve index
        
        metric = strategy_func(bootstrap_returns)
        metrics.append(metric)
    
    alpha = 1 - confidence
    return {
        'point_estimate': strategy_func(returns),
        'ci_lower': np.percentile(metrics, 100 * alpha / 2),
        'ci_upper': np.percentile(metrics, 100 * (1 - alpha / 2)),
        'bootstrap_std': np.std(metrics),
        'n_bootstrap': n_bootstrap,
    }

# Usage
def compute_sharpe(returns, freq=52):
    return returns.mean() / returns.std() * np.sqrt(freq)

ci = block_bootstrap_ci(strategy_returns, compute_sharpe)
print(f"Sharpe: {ci['point_estimate']:.2f} [{ci['ci_lower']:.2f}, {ci['ci_upper']:.2f}]")
```

### GAN for Synthetic Financial Data (Advanced)

```python
# Concept:
# - Generator: produces synthetic return paths
# - Discriminator: distinguishes real vs synthetic
# - After training, Generator creates plausible alternative market histories
#
# Use cases:
# - Stress testing (what if 2008 happened differently?)
# - Training data augmentation (N is too small)
# - Monte Carlo scenario generation
#
# Libraries:
# - ydata-synthetic: pip install ydata-synthetic
# - Custom PyTorch GAN
#
# CAUTION: Requires N > 5,000 to train meaningful generator
# Always validate: synthetic data should match real data's statistical properties
# (mean, variance, autocorrelation, fat tails, volatility clustering)
```
