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
    def buildTree(self, preorder, inorder):
        """
        :type preorder: List[int]
        :type inorder: List[int]
        :rtype: TreeNode
        """
        # we have to do it iteratively.

        assert(len(preorder) == len(inorder))
        n = len(preorder)
        root = TreeNode('dummy')
        st = []
        # note(yan): 如果这里可以传递引用的话就更简单了.
        st.append((preorder, inorder, root, 'left'))

        while st:
            (po, io, parent, lr) = st.pop()
            if po:
                x = po[0]
                p = io.index(x)
                t = TreeNode(x)
                st.append((po[1:p+1], io[0:p], t, 'left'))
                st.append((po[p+1:], io[p+1:], t, 'right'))
            else:
                t = None
            if lr == 'left':
                parent.left = t
            else:
                parent.right = t
        return root.left
