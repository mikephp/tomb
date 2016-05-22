.. demoapp documentation master file, created by
   sphinx-quickstart on Wed May 18 22:34:32 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================================
 Welcome to demoapp's documentation!
=====================================

Contents:
=========

.. toctree::
   :maxdepth: 3

   hello


`Contents` 部分是用来显示文档提纲的。maxdepth参数可以控制每个子文件显示到第几层的标题。

Sphinx-Doc入门
==============

- 官方文档 http://www.sphinx-doc.org/en/stable/contents.html
- reST(reStructuredText)入门 http://www.sphinx-doc.org/en/stable/rest.html
- reST快速参考 http://docutils.sourceforge.net/docs/user/rst/quickref.html
- 快速入门视频 `Sphinx & Read the Docs`_

.. _`Sphinx & Read the Docs`: https://www.youtube.com/watch?feature=player_embedded&v=oJsUvBQyHBs

可能用到的几个命令:

- ``sphinx-quickstart`` 快速搭建环境
- ``make html`` 编译html
- ``sphinx-autobuild source build`` 可以实时地看到html输出


reStructuredText语法
====================

引用内部文件
------------
引用hello.rst :doc:`hello`. 可以看到显示的是文件第一个标题，因此也说明了每一个.rst首标题必须说明清楚这个文件的作用。


引用外部链接
-----------

稍微有点麻烦。Target分为Named和Annonymous两种，还有一种是直接粘贴链接。
直接粘贴链接非常方便，但是如果链接太长显示效果就太差了，这个时候还是要使用Named Target. 比如

https://www.google.com/#newwindow=1&safe=strict&q=convert+png+to+jpg+imagemagick 这个链接就太长了，
显示效果非常不好。这样 `Google 'convert png to jpg imagemagick'`_ 就好看多了。

.. _`Google 'convert png to jpg imagemagick'`: https://www.google.com/#newwindow=1&safe=strict&q=convert+png+to+jpg+imagemagick


引用内部图片
-----------
.. image:: _static/hello.jpg

还有一种有意思的使用是将内部文字替换为图片.

The |biohazard| symbol must be used on containers used to dispose of medical waste.

.. |biohazard| image:: _static/biohazard.png


引用代码片段
-----------
这里代码片段不仅限于代码片段，更加准确地说是literal blocks(字面块)::

  print 'hello'
  >> hello

  def foo():
     if request.args.get('path') == '/call':
       return True


文字格式选项
---------------
- *斜体*
- **加粗**
- ``字面``
- 脚注 [#f1]_

表格

=== === ===
 A   B   C
=== === ===
 OK  OK  OK
 OK  OK  OK
=== === ===


Python代码支持
---------------
**Python函数支持**

.. py:function:: enumrate(a, [split=2])
   enumerate(a, [split=2], [split=3])

   this is enumerte function which do some enumeration.


**引用Python函数文档**

.. autofunction:: random.randrange

   well this is just ``random`` function.
   so have you thought through?


.. rubric:: Footnotes

.. [#f1] 脚注对应说明

====================
 Indices and tables
====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
