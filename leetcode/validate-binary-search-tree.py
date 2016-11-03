#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution(object):
    def isValidBST(self, root):
        """
        :type root: TreeNode
        :rtype: bool
        """
        def fx(root):
            if not root: return (True, None, None)
            (ok0, min0, max0) = fx(root.left)
            (ok1, min1, max1) = fx(root.right)
            if not ok0 or \
              not ok1 or \
              (max0 is not None and root.val <= max0) or \
              (min1 is not None and root.val >= min1):
                return (False, None, None)
            return (True, min0 or root.val, max1 or root.val)

        (ok, _, _) = fx(root)
        return ok
