This  module contains methods for producing graphs and publishing them on Amazon S3, or in the location of your choice.

It is written and maintained for `Newsworthy <https://www.newsworthy.se/en/>`_, but could possibly come in handy for other people as well.

By `Journalism++ Stockholm <http://jplusplus.org/sv>`_.

Installing
----------

.. code:: bash
  pip install newsworthy-charts


Using
-----

.. code:: python3
  >>> from newsworthycharts import Chart
  >>> c = Chart(600, 800)
  >>> c
  <Chart: 139689239312144 (800 x 600)>
  >>>


Changelog
---------

- 1.0.0
  - First version

Todo
----

- Pass a Publisher class instance to Chart to allow for alternatives to S3
