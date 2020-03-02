
'''
by Mathieu Blondel
'''

import numpy as np
import unittest
import math 

def dcg_score(y_true, y_score, k=50, gains="exponential"):
    """Discounted cumulative gain (DCG) at rank k
    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevance labels).
    y_score : array-like, shape = [n_samples]
        Predicted scores.
    k : int
        Rank.
    gains : str
        Whether gains should be "exponential" (default) or "linear".
    Returns
    -------
    DCG @k : float
    """
    order = np.argsort(y_score)[::-1]
    y_true = np.take(y_true, order[:k])

    if gains == "exponential":
        gains = 2 ** y_true - 1
    elif gains == "linear":
        gains = y_true
    else:
        raise ValueError("Invalid gains option.")

    # highest rank is 1 so +2 instead of +1
    discounts = np.log2(np.arange(len(y_true)) + 2)
    return np.sum(gains / discounts)


def ndcg_score(y_true, y_score, k=50, gains="exponential"):
    """Normalized discounted cumulative gain (NDCG) at rank k
    Parameters
    ----------
    y_true : array-like, shape = [n_samples]
        Ground truth (true relevance labels).
    y_score : array-like, shape = [n_samples]
        Predicted scores.
    k : int
        Rank.
    gains : str
        Whether gains should be "exponential" (default) or "linear".
    Returns
    -------
    NDCG @k : float
    """
    best = dcg_score(y_true, y_true, k, gains)
    actual = dcg_score(y_true, y_score, k, gains)
    return actual / best

class test(unittest.TestCase):

# Testing 
# Check that some rankings are better than others
  def dcg_score_test(self):
    assert dcg_score([12, 9, 2], [2, 1, 0]) > dcg_score([6, 3, 2], [2, 1, 0])
    assert dcg_score([6, 3, 2], [2, 1, 0]) > dcg_score([1, 3, 2], [2, 1, 0])
    assert dcg_score([12, 9, 2], [2, 1, 0], k=2) > dcg_score([6, 3, 2], [2, 1, 0], k=2)
    assert dcg_score([6, 3, 2], [2, 1, 0], k=2) > dcg_score([1, 3, 2], [2, 1, 0], k=2)

# Perfect rankings
  def ndcg_score_rank(self):
    assert ndcg_score([5, 3, 2], [2, 1, 0]) == 1.0
    assert ndcg_score([2, 3, 5], [0, 1, 2]) == 1.0

    assert ndcg_score([5, 3, 2], [2, 1, 0], k=2) == 1.0
    assert ndcg_score([2, 3, 5], [0, 1, 2], k=2) == 1.0

# Check that sample order is irrelevant
  def dcg_score_order(self):
    assert dcg_score([5, 3, 2], [2, 1, 0]) == dcg_score([2, 3, 5], [0, 1, 2])
    assert dcg_score([5, 3, 2], [2, 1, 0], k=2) == dcg_score([2, 3, 5], [0, 1, 2], k=2)
    
#if __name__ == '__main__':
#    unittest.main()