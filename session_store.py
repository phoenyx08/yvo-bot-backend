from collections import defaultdict
from typing import Dict, List, Tuple

# type alias
Session = Tuple[List[Dict[str, str]], float]   # (history, expiry_ts)

sessions: Dict[str, Session] = defaultdict(lambda: ([], 0.0))
