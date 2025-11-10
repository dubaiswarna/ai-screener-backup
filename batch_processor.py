"""
Batch Processor for Large Stock Universes
==========================================
Efficiently processes 500+ stocks using batching and parallel processing

Features:
- Batch processing (configurable batch size)
- Parallel execution within batches
- Progress tracking
- Result caching
- Memory optimization

Author: AI Screener v3.0
Date: November 2025
"""

import os
import time
import pandas as pd
import numpy as np
from typing import List, Dict, Callable, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from pathlib import Path
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Processes large number of stocks efficiently using batching.
    """
    
    def __init__(self, 
                 batch_size: int = 50,
                 max_workers: int = 10,
                 use_multiprocessing: bool = False,
                 cache_results: bool = True,
                 cache_duration: int = 300):
        """
        Initialize batch processor.
        
        Args:
            batch_size: Number of stocks per batch
            max_workers: Number of parallel workers
            use_multiprocessing: Use ProcessPoolExecutor instead of ThreadPoolExecutor
            cache_results: Enable result caching
            cache_duration: Cache duration in seconds
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.use_multiprocessing = use_multiprocessing
        self.cache_results = cache_results
        self.cache_duration = cache_duration
        self.cache = {}
        self.cache_timestamps = {}
        
    def clear_cache(self):
        """Clear all cached results."""
        self.cache = {}
        self.cache_timestamps = {}
        logger.info("✅ Cache cleared")
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached result is still valid."""
        if key not in self.cache_timestamps:
            return False
        
        timestamp = self.cache_timestamps[key]
        age = (datetime.now() - timestamp).total_seconds()
        
        return age < self.cache_duration
    
    def _get_from_cache(self, key: str) -> Any:
        """Get result from cache if valid."""
        if not self.cache_results:
            return None
        
        if key in self.cache and self._is_cache_valid(key):
            logger.debug(f"📦 Cache hit: {key}")
            return self.cache[key]
        
        return None
    
    def _add_to_cache(self, key: str, value: Any):
        """Add result to cache."""
        if not self.cache_results:
            return
        
        self.cache[key] = value
        self.cache_timestamps[key] = datetime.now()
    
    def process_batch(self, 
                      items: List[Any],
                      process_func: Callable,
                      batch_num: int = 1,
                      total_batches: int = 1) -> List[Any]:
        """
        Process a single batch of items.
        
        Args:
            items: List of items to process
            process_func: Function to process each item
            batch_num: Current batch number
            total_batches: Total number of batches
            
        Returns:
            List of results
        """
        results = []
        
        logger.info(f"📊 Processing batch {batch_num}/{total_batches} ({len(items)} items)")
        
        # Choose executor
        ExecutorClass = ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor
        
        with ExecutorClass(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(process_func, item): item 
                for item in items
            }
            
            # Collect results
            for i, future in enumerate(as_completed(future_to_item), 1):
                item = future_to_item[future]
                
                try:
                    result = future.result()
                    
                    # Add to cache if enabled
                    if self.cache_results and isinstance(item, str):
                        self._add_to_cache(item, result)
                    
                    results.append(result)
                    
                    # Progress update
                    if i % 10 == 0 or i == len(items):
                        progress = (i / len(items)) * 100
                        logger.info(f"  Progress: {i}/{len(items)} ({progress:.1f}%)")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing {item}: {e}")
                    results.append(None)
        
        # Filter out None results
        results = [r for r in results if r is not None]
        
        logger.info(f"✅ Batch {batch_num}/{total_batches} complete: {len(results)} successful")
        
        return results
    
    def process_all(self,
                    items: List[Any],
                    process_func: Callable,
                    show_progress: bool = True) -> List[Any]:
        """
        Process all items in batches.
        
        Args:
            items: List of all items to process
            process_func: Function to process each item
            show_progress: Show progress updates
            
        Returns:
            List of all results
        """
        start_time = time.time()
        
        logger.info("="*60)
        logger.info(f"🚀 Starting batch processing")
        logger.info(f"   Total items: {len(items)}")
        logger.info(f"   Batch size: {self.batch_size}")
        logger.info(f"   Max workers: {self.max_workers}")
        logger.info(f"   Cache enabled: {self.cache_results}")
        logger.info("="*60)
        
        # Check cache first
        if self.cache_results:
            cached_results = []
            uncached_items = []
            
            for item in items:
                if isinstance(item, str):
                    cached = self._get_from_cache(item)
                    if cached is not None:
                        cached_results.append(cached)
                    else:
                        uncached_items.append(item)
                else:
                    uncached_items.append(item)
            
            if cached_results:
                logger.info(f"📦 Cache hits: {len(cached_results)}/{len(items)}")
            
            items = uncached_items
        else:
            cached_results = []
        
        # Split into batches
        batches = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batches.append(batch)
        
        total_batches = len(batches)
        logger.info(f"📦 Created {total_batches} batches")
        
        # Process each batch
        all_results = cached_results.copy()
        
        for batch_num, batch in enumerate(batches, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"BATCH {batch_num}/{total_batches}")
            logger.info(f"{'='*60}")
            
            batch_results = self.process_batch(
                batch, 
                process_func, 
                batch_num, 
                total_batches
            )
            
            all_results.extend(batch_results)
            
            # Show overall progress
            if show_progress:
                overall_progress = (batch_num / total_batches) * 100
                logger.info(f"📊 Overall Progress: {overall_progress:.1f}%")
        
        # Summary
        elapsed_time = time.time() - start_time
        
        logger.info("\n" + "="*60)
        logger.info("✅ BATCH PROCESSING COMPLETE")
        logger.info("="*60)
        logger.info(f"Total items: {len(items) + len(cached_results)}")
        logger.info(f"Cached: {len(cached_results)}")
        logger.info(f"Processed: {len(items)}")
        logger.info(f"Successful: {len(all_results)}")
        logger.info(f"Failed: {len(items) + len(cached_results) - len(all_results)}")
        logger.info(f"Time elapsed: {elapsed_time:.1f}s ({elapsed_time/60:.1f} min)")
        logger.info(f"Avg time/item: {elapsed_time/len(items):.2f}s" if items else "N/A")
        logger.info("="*60)
        
        return all_results


class StockBatchProcessor(BatchProcessor):
    """
    Specialized batch processor for stock analysis.
    """
    
    def __init__(self, 
                 batch_size: int = 50,
                 max_workers: int = 10,
                 data_dir: str = 'data/stocks_all'):
        """
        Initialize stock batch processor.
        
        Args:
            batch_size: Number of stocks per batch
            max_workers: Number of parallel workers
            data_dir: Directory containing stock data
        """
        super().__init__(
            batch_size=batch_size,
            max_workers=max_workers,
            cache_results=True,
            cache_duration=300
        )
        
        self.data_dir = Path(data_dir)
    
    def load_stock_data(self, symbol: str) -> pd.DataFrame:
        """
        Load data for a single stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            DataFrame with stock data
        """
        file_path = self.data_dir / f"{symbol}.csv"
        
        if not file_path.exists():
            logger.warning(f"⚠️ Data file not found: {symbol}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            logger.error(f"❌ Error loading {symbol}: {e}")
            return pd.DataFrame()
    
    def analyze_stocks(self, 
                       symbols: List[str],
                       analysis_func: Callable) -> List[Dict]:
        """
        Analyze multiple stocks using batch processing.
        
        Args:
            symbols: List of stock symbols
            analysis_func: Function to analyze each stock
            
        Returns:
            List of analysis results
        """
        logger.info(f"🔍 Analyzing {len(symbols)} stocks...")
        
        def process_stock(symbol: str) -> Dict:
            """Process a single stock."""
            try:
                # Load data
                df = self.load_stock_data(symbol)
                
                if df.empty:
                    return None
                
                # Run analysis
                result = analysis_func(symbol, df)
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Error analyzing {symbol}: {e}")
                return None
        
        # Process all stocks in batches
        results = self.process_all(symbols, process_stock)
        
        return results


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == '__main__':
    print("🧪 Testing Batch Processor...")
    
    # Test function
    def test_process(item: str) -> Dict:
        """Example processing function."""
        time.sleep(0.1)  # Simulate work
        return {
            'item': item,
            'result': len(item),
            'timestamp': datetime.now()
        }
    
    # Create processor
    processor = BatchProcessor(
        batch_size=10,
        max_workers=5,
        cache_results=True
    )
    
    # Test items
    items = [f"STOCK{i:03d}" for i in range(50)]
    
    # Process
    print("\n" + "="*60)
    print("TEST 1: First run (no cache)")
    print("="*60)
    results1 = processor.process_all(items, test_process)
    print(f"\n✅ Processed {len(results1)} items")
    
    # Process again (should use cache)
    print("\n" + "="*60)
    print("TEST 2: Second run (with cache)")
    print("="*60)
    results2 = processor.process_all(items, test_process)
    print(f"\n✅ Processed {len(results2)} items")
    
    print("\n✅ Batch processor test complete!")

